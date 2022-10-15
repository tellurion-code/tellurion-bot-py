"""Game class."""

import discord
import random
from modules.mascarade.holder import Holder

from modules.mascarade.player import Player
from modules.mascarade.utils import display_money
from modules.mascarade.views import JoinView, RoleView, ConfirmView, TurnView

import modules.mascarade.globals as global_values

class Game:
    def __init__(self, mainclass, **kwargs):
        message = kwargs["message"] if "message" in kwargs else None
        self.mainclass = mainclass

        self.channel = None
        self.players = {}  # Dict pour rapidement accéder aux infos
        if message:
            self.channel = message.channel
            self.players = {
                message.author.id: Player(self, message.author)
            }

        self.order = []  # Ordre des id des joueurs
        self.turn = -1  # Le tour (index du leader) en cours, -1 = pas commencé
        self.round = 0
        self.tribunal = 0  # Pièces au tribunal
        self.info_view = None
        self.roles = {}  # Rôles (dictionnaire avec comme clés les noms)
        self.center = []  # Cartes au centre
        self.contestors = []
        self.stack = []  # Liste des résumés d'effets à afficher à la fin du tour
        self.info = None  # Dict d'info à afficher sur l'embed
        self.phase = ""  # Phase actuelle du jeu

    async def reload(self, object, client):
        # await self.deserialize(object, client)
        #
        # if object["state"]["type"] == "send_team_choice":
        #     await self.send_team_choice()
        # elif object["state"]["type"] == "quest":
        #     await self.send_players_quest_choice()
        # elif object["state"]["type"] == "next_turn":
        #     await self.next_turn()
        pass

    def get_neighbours(self, player):
        index = self.order.index(player.user.id)

        p = (index + 1) % len(self.order)
        n = (index - 1 + len(self.order)) % len(self.order)
        previous = self.players[self.order[p]]
        next = self.players[self.order[n]]

        return previous, next

    @property
    def player_list(self):
        return '\n'.join("`" + str(x.user) + "`" for x in self.players.values())

    @property
    def current_player(self):
        return self.players[self.order[self.turn]]

    @property
    def role_count(self):
        return sum(role.number for role in self.roles.values())

    async def on_creation(self, message):
        embed = discord.Embed(
            title="Partie de Mascarade | Joueurs (1) :",
            description=self.player_list,
            color=global_values.color
        )

        await self.channel.send(
            embed=embed,
            view=JoinView(self)
        )

    async def pick_roles(self):
        await self.channel.send(
            embed=discord.Embed(
                title=f"[MASCARADE] Choix des rôles | Joueurs ({len(self.players)})",
                description=self.player_list + '\n\nLes rôles en excès seront placés au centre',
                color=global_values.color
            ),
            view=RoleView(self)
        )

    async def start_game(self):
        self.turn = -1

        for player_id in self.players:
            self.order.append(player_id)

        random.shuffle(self.order)

        role_keys = [key for key, role in self.roles.items() for _ in range(role.number)]
        random.shuffle(role_keys)

        if self.mainclass.objects.save_exists("icons"):
            icons = self.mainclass.objects.load_object("icons")
        else:
            icons = {}

        for i, id in enumerate(self.order):
            self.players[id].index_emoji = icons[str(id)] if str(id) in icons else global_values.number_emojis[i]
            self.players[id].role = self.roles[role_keys.pop()]
            self.players[id].last_vote_emoji = "✉"

        # Mettre les rôles restants au centre avec des faux joueurs
        for i, key in enumerate(role_keys):
            fake_player = Holder(self, f"{i+1}e carte du centre")
            fake_player.role = self.roles[key]
            fake_player.index_emoji = "❔"

            self.center.append(fake_player)

        await self.send_all_roles()

    async def send_all_roles(self):
        center_roles = '\n'.join(f'{x}: {x.role}' for x in self.center)
        center_display = f"\n\nRôles au centre:\n{center_roles}" if len(self.center) else ""
        embed = discord.Embed(
            title="[MASCARADE] Rôles de tous les joueurs",
            description='\n'.join([f"{self.players[x]}: {self.players[x].role}" for x in self.order]) + center_display,
            color=global_values.color
        )

        await self.channel.send(
            embed=embed,
            view=ConfirmView(self, self.order, self.start_turn, [None], temporary=True)
        )

    def get_info_embed(self, **kwargs):
        self.info = kwargs["info"] if "info" in kwargs else self.info
        color = kwargs["color"] if "color" in kwargs else global_values.color

        embed = discord.Embed(
            title=f"[MASCARADE] Tour de `{self.current_player.user}` 🍷",
            description="",
            color=color
        )

        embed.add_field(
            name="Tribunal",
            value=display_money(self.tribunal),
            inline=False
        )

        player_infos = []
        for i, player_id in enumerate(self.order):
            player = self.players[player_id]
            
            vote = player.last_vote_emoji
            if self.phase == "contest":
                vote = "📩" if player.last_vote is not None else "✉"

            player_info = f'{player.index_emoji} {"🍷 " if self.turn == i else ""}`{player.user}`'
            role = f"({player.role})" if player.revealed else ""
            money = display_money(player.coins)

            player_infos.append(f'{vote} {player_info} {role}: {money}')

        embed.add_field(
            name="Invités",
            value='\n'.join(player_infos),
            inline=False
        )

        if len(self.center):
            embed.add_field(
                name="Centre",
                value='\n'.join(str(x) for x in self.center)
            )

        if self.info:
            embed.add_field(name=self.info["name"], value=self.info["value"], inline=False)

        if self.current_player.must_exchange and self.phase == "action":
            embed.add_field(name="Echange obligatoire", value=f"{self.current_player} doit échanger", inline=False)

        embed.set_footer(text="Mettez une réaction pour changer votre icône!")

        return embed

    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        view = kwargs["view"] if "view" in kwargs else None

        new_view = view or self.info_view
        embed = self.get_info_embed(**kwargs)
        if mode == "replace":
            if self.info_view:
                if view:
                    self.info_view.stop()

                message = await self.info_view.message.edit(
                    embed=embed,
                    view=new_view
                )
            else:
                message = await self.channel.send(
                    embed=embed,
                    view=new_view
                )

            new_view.message = message
        elif mode == "set":
            if self.info_view and view:
                await self.info_view.clear()

            await self.channel.send(
                embed=embed,
                view=new_view
            )

        self.info_view = new_view

    async def start_turn(self, message):
        self.phase = "action"
        self.turn = (self.turn + 1) % len(self.order)
        self.round += 1
        await self.send_info(view=TurnView(self), info=message)

    async def check_vote_end(self, role):
        for player_id in self.order:
            player = self.players[player_id]
            if player.last_vote is None:
                return False

        if self.phase != "contest":
            return False

        self.phase = "post_contest"
        self.contestors = [x for x in self.players.values() if x.last_vote]

        self.stack = []
        if len(self.contestors) == 0:
            self.stack.append("🚫 Personne n'a contesté")
            await role.use_power(self.current_player)
        else:
            self.stack.append(f"{','.join(str(x) for x in self.contestors)} {'a' if len(self.contestors) == 1 else 'ont'} contesté")
            self.contestors.append(self.current_player)
            successes = []
            for player in self.contestors:
                if player.user.id != self.current_player.user.id:
                    player.last_vote_emoji = "✋"
                
                player.revealed = True

                if player.role.name == role.name:
                    successes.append(player)
                else:
                    verb = 'annoncé' if player.user.id == self.current_player.user.id else 'contesté'
                    self.stack.append(f"{player} a {verb} à tort et a payé {display_money(1)} au Tribunal")
                    player.coins -= 1
                    self.tribunal += 1

            for player in successes:
                await role.use_power(player)

            if len(successes) == 0:
                self.stack.append("🚫 Aucun des contestants n'avait le rôle annoncé!")
                await role.end_turn()

        return True

    # Passe au prochain tour
    async def next_turn(self, message=None):
        for player in self.players.values():
            if (player.coins >= 13):
                await self.end_game(str(player.user))
                return

        await self.start_turn(message)

    # Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, winner):
        article = 'd\'' if winner[:1] in ('E', 'A', 'I', 'O', 'U', 'Y') else 'de '
        embed = discord.Embed(
            title=f"[MASCARADE] Victoire {article}`{winner}` !",
            color=global_values.color,
            description="**Joueurs :**\n" + '\n'.join(f"{self.players[x]} : {self.players[x].role} - {display_money(self.players[x].coins)}" for i, x in enumerate(self.order))
        )
        await self.info_view.message.edit(embed=self.get_info_embed())
        await self.info_view.clear()

        await self.channel.send(embed=embed)
        # self.delete_save()
        del global_values.games[self.channel.id]

    def serialize(self, state):
        object = {
            "channel": self.channel.id,
            "order": self.order,
            "turn": self.turn,
            "round": self.round,
            "team": self.team,
            "refused": self.refused,
            "quests": self.quests,
            "info_message": self.info_message.id if self.info_message else None,
            "played": self.played,
            "lady_of_the_lake": self.lady_of_the_lake,
            "roles": self.roles,
            "phase": self.phase,
            "gamerules": self.game_rules,
            "players": {},
            "state": state
        }

        for id, player in self.players.items():
            object["players"][id] = {
                "role": player.role,
                "last_vote": player.last_vote,
                "inspected": player.inspected,
                "quest_choices": player.quest_choices,
                "info_message": player.info_message.id if player.info_message else None,
                "user": player.user.id
            }

        return object

    async def deserialize(self, object, client):
        self.channel = client.get_channel(object["channel"])
        self.order = object["order"]
        self.turn = int(object["turn"])
        self.round = int(object["round"])
        self.quests = object["quests"]
        self.roles = object["roles"]
        self.phase = object["phase"]
        self.game_rules = object["gamerules"]
        self.refused = int(object["refused"])
        self.info_message = await self.channel.fetch_message(object["info_message"]) if object["info_message"] else None
        self.played = object["played"]
        self.lady_of_the_lake = object["lady_of_the_lake"]
        self.players = {}
        self.team = {}

        for i, id in object["team"].items():
            self.team[int(i)] = int(id)

        for id, info in object["players"].items():
            player = self.players[int(id)] = self.roles[info["role"]](client.get_user(info["user"]))
            player.last_vote = info["last_vote"]
            player.inspected = info["inspected"]
            player.quest_choices = info["quest_choices"]
            player.info_message = await player.user.fetch_message(info["info_message"]) if info["info_message"] else None

    def save(self, state):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
        else:
            object = {}

        object[self.channel.id] = self.serialize(state)
        self.mainclass.objects.save_object("games", object)

    def delete_save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
            if str(self.channel.id) in object:
                object.pop(str(self.channel.id))

            self.mainclass.objects.save_object("games", object)
        else:
            print("no save")

 #  Module créé par Le Codex#9836
