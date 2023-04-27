"""Game class."""

import discord
import random
import math
from modules.timebomb.components import RolesButton, SelfHandButton, SelfRoleButton

from modules.timebomb.player import Player
from modules.timebomb.roles import Role
from modules.timebomb.wires import BombWire, GroundWire, LiveWire
from modules.timebomb.views import JoinView, PlayerSelectView
# from modules.timebomb.utils import ...

import modules.timebomb.globals as global_values

role_dict = { role.__name__.lower(): role for role in Role.__subclasses__() }

class Game:
    def __init__(self, mainclass, message=None):
        self.mainclass = mainclass

        self.channel = None
        self.players = {}  # Dict pour rapidement accéder aux infos
        if message:
            self.channel = message.channel
            self.players = {
                message.author.id: Player(self, message.author)
            }

        self.turn = -1  # Le tour (user id du joueur) en cours, -1 = pas commencé
        self.previous_turn = -1  # Le joueur précédent, pour éviter le ping-pong
        self.round = 0
        self.deck = []  # Paquet de cartes
        self.aside = []  # Cartes retirées
        self.info_view = None
        self.roles = {}  # Rôles (dictionnaire avec comme clés les noms)
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

    async def on_creation(self, message):
        embed = discord.Embed(
            title="Partie de Timebomb | Joueurs (1) :",
            description=self.player_list,
            color=global_values.color
        )

        await self.channel.send(
            embed=embed,
            view=JoinView(self)
        )

    @property
    def player_list(self):
        return '\n'.join("`" + str(x.user) + "`" for x in self.players.values())

    @property
    def current_player(self):
        return self.players[self.turn]
    
    @property
    def stack_string(self):
        return '\n'.join(self.stack)

    async def start_game(self):
        if not len(self.roles):
            players_to_roles = [
                [],
                [],
                ["evil", "good"],  # Debug
                ["evil", "good", "good"],  # Debug
                ["evil", "evil", "good", "good", "good"],  # 4
                ["evil", "evil", "good", "good", "good"],  # 5
                ["evil", "evil", "good", "good", "good", "good"],  # 6
                ["evil", "evil", "evil", "good", "good", "good", "good", "good"],  # 7
                ["evil", "evil", "evil", "good", "good", "good", "good", "good"]  # 8
            ]
            self.roles = players_to_roles[len(self.players)]
        
        random.shuffle(self.roles)
        self.roles = [role_dict[x](self) for x in self.roles]

        if self.mainclass.objects.save_exists("icons"):
            icons = self.mainclass.objects.load_object("icons")
        else:
            icons = {}

        for i, id in enumerate(self.players.keys()):
            self.players[id].index_emoji = icons[str(id)] if str(id) in icons else global_values.number_emojis[i]
            self.players[id].role = self.roles[i]
            self.deck.append(LiveWire(self))

        random.shuffle(self.roles)

        self.deck.append(BombWire(self))
        remaining = len(self.players) * 5 - len(self.deck)
        for _ in range(remaining): self.deck.append(GroundWire(self))

        self.turn = random.choice(tuple(self.players.keys()))
        await self.start_round({
            "name": "Première coupe",
            "value": f"{self.current_player} doit choisir chez qui couper un fil"
        })

    def get_info_embed(self, info=None, color=None):
        self.info = info or self.info
        color = color or global_values.color

        embed = discord.Embed(
            title=f"[TIMEBOMB] Manche {self.round} | Tour de `{self.current_player.user}` ✂️",
            description="",
            color=color
        )

        wires = '\n'.join(' '.join(str(self.aside[x+y*6]) for x in range(y*6, min(len(self.aside), y*6+6))) for y in range(math.floor(len(self.aside)/len(self.players))))
        embed.add_field(
            name="Fils coupés",
            value=wires if len(self.aside) else "Aucun",
            inline=False
        )

        player_infos = []
        for id, player in self.players.items():
            player_info = f'{player.index_emoji} {"✂️ " if self.turn == id else ""}`{player.user}`'
            cards = ' '.join(str(x) for x in player.wires)
            player_infos.append(f'{player_info}: {cards}')

        embed.add_field(
            name="Joueurs",
            value='\n'.join(player_infos),
            inline=False
        )

        if self.info:
            embed.add_field(name=self.info["name"], value=self.info["value"], inline=False)

        embed.set_footer(text="Mettez une réaction pour changer votre icône!")
        return embed

    async def send_info(self, mode="replace", view=None, info=None):
        new_view = self.info_view
        if view:
            view.add_item(SelfRoleButton(row=1))
            view.add_item(SelfHandButton(row=1))
            view.add_item(RolesButton(row=1))
            new_view = view

        embed = self.get_info_embed(info=info)
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

    async def start_round(self, message=None):
        if self.round == 4:
            self.end_game(False, message, "temps écoulé")
            return
        
        for player in self.players.values():
            self.deck.extend(player.wires)
            player.wires = []

        random.shuffle(self.deck)

        i, ids = 0, tuple(self.players.keys())
        while len(self.deck):
            player = self.players[ids[i]]
            wire = self.deck.pop()
            wire.player = player
            player.wires.append(wire)
            
            i = (i + 1) % len(ids)
        
        self.round += 1
        if message:
            message["value"] += "\n**Une nouvelle manche a commencé**"
        else:
            message = {
                "name": "Nouvelle manche",
                "value": "**Une nouvelle manche a commencé**"
            }
        
        await self.start_turn(message)

    async def start_turn(self, message=None):
        if self.phase != "end":
            self.phase = "action"
        
        self.stack = []
        await self.send_info(
            view=PlayerSelectView(
                self,
                self.current_player.choose_wire_to_cut,
                condition=lambda e: e.user.id != self.current_player.user.id and (e.user.id != self.previous_turn or global_values.debug)
            ), 
            info=message
        )

    # Passe au prochain tour
    async def next_turn(self, next_index, message=None):
        self.previous_turn = self.turn
        self.turn = next_index
        
        # Vérifier si la manche est finie, et si les gentils ont gagnés
        if sum(1 for wire in self.aside if wire.name == LiveWire.name) == len(self.players):
            await self.end_game(True, message)
            return
        
        if len(self.aside) == len(self.players) * self.round:
            await self.start_round(message)
            return
        
        await self.start_turn(message)

    # Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, good_win, message=None, cause=""):
        if self.phase == "end":
            return
        
        self.phase = "end"
        embed = discord.Embed(
            title=f"[TIMEBOMB] Victoire des {'🟦 Gentils' if good_win else '🟥 Méchants par ' + cause} !",
            color=global_values.color,
            description="**Joueurs :**\n" + '\n'.join(f"{p} : {p.role}" for i, p in enumerate(self.players.values()))
        )
        await self.info_view.message.edit(embed=self.get_info_embed(message))
        await self.info_view.clear()

        await self.channel.send(embed=embed)
        # self.delete_save()
        del global_values.games[self.channel.id]

    # def serialize(self, state):
    #     object = {
    #         "channel": self.channel.id,
    #         "order": self.order,
    #         "turn": self.turn,
    #         "round": self.round,
    #         "team": self.team,
    #         "refused": self.refused,
    #         "quests": self.quests,
    #         "info_message": self.info_message.id if self.info_message else None,
    #         "played": self.played,
    #         "lady_of_the_lake": self.lady_of_the_lake,
    #         "roles": self.roles,
    #         "phase": self.phase,
    #         "gamerules": self.game_rules,
    #         "players": {},
    #         "state": state
    #     }

    #     for id, player in self.players.items():
    #         object["players"][id] = {
    #             "role": player.role,
    #             "last_vote": player.last_vote,
    #             "inspected": player.inspected,
    #             "quest_choices": player.quest_choices,
    #             "info_message": player.info_message.id if player.info_message else None,
    #             "user": player.user.id
    #         }

    #     return object

    # async def deserialize(self, object, client):
    #     self.channel = client.get_channel(object["channel"])
    #     self.order = object["order"]
    #     self.turn = int(object["turn"])
    #     self.round = int(object["round"])
    #     self.quests = object["quests"]
    #     self.roles = object["roles"]
    #     self.phase = object["phase"]
    #     self.game_rules = object["gamerules"]
    #     self.refused = int(object["refused"])
    #     self.info_message = await self.channel.fetch_message(object["info_message"]) if object["info_message"] else None
    #     self.played = object["played"]
    #     self.lady_of_the_lake = object["lady_of_the_lake"]
    #     self.players = {}
    #     self.team = {}

    #     for i, id in object["team"].items():
    #         self.team[int(i)] = int(id)

    #     for id, info in object["players"].items():
    #         player = self.players[int(id)] = self.roles[info["role"]](client.get_user(info["user"]))
    #         player.last_vote = info["last_vote"]
    #         player.inspected = info["inspected"]
    #         player.quest_choices = info["quest_choices"]
    #         player.info_message = await player.user.fetch_message(info["info_message"]) if info["info_message"] else None

    # def save(self, state):
    #     if self.mainclass.objects.save_exists("games"):
    #         object = self.mainclass.objects.load_object("games")
    #     else:
    #         object = {}

    #     object[self.channel.id] = self.serialize(state)
    #     self.mainclass.objects.save_object("games", object)

    # def delete_save(self):
    #     if self.mainclass.objects.save_exists("games"):
    #         object = self.mainclass.objects.load_object("games")
    #         if str(self.channel.id) in object:
    #             object.pop(str(self.channel.id))

    #         self.mainclass.objects.save_object("games", object)
    #     else:
    #         print("no save")

# Module créé par Le Codex#9836
