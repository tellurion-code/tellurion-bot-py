import discord
import random
import math

from modules.avalon.player import Player, Good, Evil
from modules.avalon.views import GameView, JoinView, TeamView, VoteView, QuestView, AssassinView
from modules.avalon.components import RoleButton

import modules.avalon.globals as global_values

classes = {"good": Good, "evil": Evil}
classes.update({c.__name__.lower(): c for t in [Good, Evil] for c in t.__subclasses__()})
# print(classes)

class Game:
    def __init__(self, mainclass, **kwargs):
        message = kwargs["message"] if "message" in kwargs else None
        self.mainclass = mainclass

        if message:
            self.channel = message.channel
            self.players = {
                message.author.id: Player(self, message.author)
            }  # Dict pour rapidement accéder aux infos
        else:
            self.channel = None
            self.players = {}

        self.order = []  # Ordre des id des joueurs
        self.turn = -1  # Le tour (index du leader) en cours, -1 = pas commencé
        self.round = 0  # Quête en cours
        self.team = []  # Equipe qui part en quête. Contient les indices d'ordre et les id
        self.quests = []  # Réussite (-1) ou échec (0) des quêtes. Chiffre supérieur à 0 = pas faite
        self.refused = 0  # Nombre de gouvernements refusés
        self.info_view = None
        self.played = []  # Dernière cartes jouées
        self.roles = []  # Rôles
        self.phase = "team_selection"
        self.lady_of_the_lake = 0  # Index du joueur qui a la Dame du Lac
        self.game_rules = {
            "lancelot_know_evil": False,
            "evil_know_lancelot": True,
            "4th_quest_two_failures": True,
            "uther_learns_role": False,
            "lady_of_the_lake": False,
            "agravain_know_oberon": False
        }

    async def reload(self, object, client):
        await self.deserialize(object, client)

        if object["state"]["type"] == "send_team_choice":
            await self.send_team_choice(None)
        elif object["state"]["type"] == "quest":
            await self.send_players_quest_choice()
        elif object["state"]["type"] == "next_turn":
            await self.next_turn()

    async def on_creation(self):
        embed = discord.Embed(
            title="Partie d'Avalon | Joueurs (1) :",
            description='\n'.join(["`" + str(x.user) + "`" for x in self.players.values()]),
            color=global_values.color
        )

        await self.channel.send(
            embed=embed,
            view=JoinView(self)
        )

    async def start_game(self):
        self.turn = -1

        quests = [
            [],  # 0
            [],  # 1
            [1, 1, 2, 2, 2],  # 2, Debug
            [1, 2, 2, 2, 2],  # 3
            [2, 2, 2, 3, 3],  # 4
            [2, 3, 2, 3, 3],  # 5
            [2, 3, 4, 3, 4],  # 6
            [2, 3, 3, 4, 4],  # 7
            [3, 4, 4, 5, 5],  # 8
            [3, 4, 4, 5, 5],  # 9
            [3, 4, 4, 5, 5]   # 10
        ]

        self.quests = quests[len(self.players)]

        roles = [
            [],  # 0?
            ["good"],  # 1
            ["assassin", "merlin"],  # 2, Debug
            ["merlin", "good", "assassin"],  # 3
            ["merlin", "good", "good", "assassin"],  # 4
            ["merlin", "percival", "good", "morgane", "assassin"],  # 5
            ["merlin", "percival", "good", "good", "morgane", "assassin"],  # 6
            ["merlin", "percival", "good", "good", "evil", "morgane", "assassin"],  # 7
            ["merlin", "percival", "good", "good", "good", "evil", "morgane", "assassin"],  # 8
            ["merlin", "percival", "good", "good", "good", "good", "evil", "morgane", "assassin"],  # 9
            ["merlin", "percival", "good", "good", "good", "good", "evil", "evil", "morgane", "assassin"]  # 10
        ]

        if len(self.roles) == 0:
            self.roles = roles[len(self.players)]

        self.order = []
        for player_id in self.players:
            self.order.append(player_id)

        random.shuffle(self.order)
        random.shuffle(self.roles)

        if self.mainclass.objects.save_exists("icons"):
            icons = self.mainclass.objects.load_object("icons")
        else:
            icons = {}

        for i, id in enumerate(self.order):
            self.players[id] = classes[self.roles[i]](self, self.players[id].user)
            self.players[id].index_emoji = icons[str(id)] if str(id) in icons else global_values.number_emojis[i]

        for id in self.order:
            await self.players[id].game_start()

        random.shuffle(self.roles)

        self.lady_of_the_lake = len(self.players) - 1

        await self.start_turn(None)

    @property
    def current_player(self):
        return self.players[self.order[self.turn]]

    # Envoies le résumé de la partie aux joueurs + le channel
    def get_info_embed(self, **kwargs):
        info = kwargs["info"] if "info" in kwargs else None
        color = kwargs["color"] if "color" in kwargs else global_values.color

        embed = discord.Embed(
            title="[AVALON] Tour de `" + str(self.current_player.user) + "` 👑",
            description="",
            color=color
        )

        embed.add_field(
            name="Quêtes :",
            value=" ".join([global_values.number_emojis[x - 1] if x > 0 else (str(global_values.quest_choices["emojis"]["success"]) if x else str(global_values.quest_choices["emojis"]["failure"])) for x in self.quests])
        )

        embed.add_field(
            name="Equipes refusées :",
            value="🟧 " * self.refused + "🔸 " * (5 - self.refused)
        )

        embed.add_field(
            name="Chevaliers :",
            value='\n'.join([(("📩" if self.phase == "team_selection" else (str(global_values.vote_choices["emojis"][self.players[x].last_vote]))) if len(self.players[x].last_vote) else "✉️") + " " + self.players[x].index_emoji + " `" + str(self.players[x].user) + "` " + ("👑" if self.turn == i else "") + ("🌊" if self.lady_of_the_lake == i and self.game_rules["lady_of_the_lake"] else "") for i, x in enumerate(self.order)]),
            inline=False
        )

        if len(self.team):
            embed.add_field(
                name="Participants à la Quête :",
                value='\n'.join([(self.players[x].index_emoji + ' `' + str(self.players[x].user) + '`') for x in self.team]),
                inline=False
            )

        if self.round == 3 and len(self.players) >= 7 and self.game_rules["4th_quest_two_failures"]:
            embed.add_field(
                name="4e Quête",
                value="⚠️ **Quête échouée à partir de deux échecs** ⚠️\n",
                inline=False
            )

        if info:
            embed.add_field(name=info["name"], value=info["value"])

        embed.set_footer(text="Mettez une réaction pour changer votre icône!")

        return embed

    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        view = None
        if "view" in kwargs:
            view = kwargs["view"]
            view.add_item(RoleButton(row=4))

        new_view = view or self.info_view
        embed = self.get_info_embed(**kwargs)
        if mode == "replace":
            if self.info_view and view:
                self.info_view.stop()

            message = await self.info_view.message.edit(
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
        self.phase = "team_selection"
        self.turn = (self.turn + 1) % len(self.order)

        for player in self.players.values():
            player.last_vote = ""
            player.last_choice = ""

        self.team = []

        await self.send_team_choice(message)

        self.save({"type":"send_team_choice"})

    # Est aussi un début de tour, envoies le choix de team
    async def send_team_choice(self, message):
        await self.send_info(mode="set", info=message, view=TeamView(self))

    async def send_players_vote_choice(self):
        await self.send_info(view=VoteView(self))

    # Appelé à chaque fois qu'un joueur vote. Vérifie les votes manquants puis la majorité
    async def check_vote_end(self):
        for player_id in self.order:
            player = self.players[player_id]
            if not len(player.last_vote):
                return

        if self.phase == "team_selection":
            self.phase = "vote_for_team"

            for_votes = len([self.players[x] for x in self.order if self.players[x].last_vote == "for"])

            if for_votes > len(self.order)/2:
                await self.send_players_quest_choice()
                self.save({"type":"quest"})
            else:
                await self.send_info(info={
                    "name": "Equipe refusée",
                    "value": "Le prochain leader va proposer une nouvelle composition."
                })

                self.refused += 1
                if self.refused == 5:
                    await self.end_game(False, "5 Equipes refusées")
                else:
                    await self.next_turn()

    async def send_players_quest_choice(self):
        await self.send_info(
            info={
                "name": "Equipe acceptée",
                "value": "Les membres vont partir en quête et décider de la faire réussir ou échouer."
            },
            view=QuestView(self),
            color=0x2e64fe
        )

    async def check_quest_end(self):
        for player_id in self.team:
            player = self.players[player_id]
            if not len(player.last_choice):
                return

        if self.phase == "vote_for_team":
            self.phase = "quest"

            for player_id in self.team:
                player = self.players[player_id]

                if player.last_choice == "sabotage":
                    for id in self.team:
                        self.players[id].last_choice = "failure"

            self.played = [self.players[x].last_choice for x in self.team]
            random.shuffle(self.played)

            cancelled = len([x for x in self.played if x == "cancel"])
            fails = len([x for x in self.played if x == "failure"])
            reverses = len([x for x in self.played if x == "reverse"])

            if not cancelled:
                success = fails < (2 if self.round == 3 and len(self.players) >= 7 and self.game_rules["4th_quest_two_failures"] else 1)
                if reverses == 1:
                    success = not success

                self.quests[self.round] = -1 if success else 0

                emoji = str(global_values.quest_choices["emojis"]["success"])
                name = " Quête réussie "
                if not success:
                    emoji = str(global_values.quest_choices["emojis"]["failure"])
                    name = " Quête échouée "

                await self.send_info(
                    info={
                        "name": emoji + name + emoji,
                        "value": "Choix : " + " ".join([str(global_values.quest_choices["emojis"][x]) for x in self.played])
                    },
                    color=0x76ee00 if success else 0xef223f)

                self.round += 1
                self.refused = 0

                if sum([1 for x in self.quests if x == 0]) == 3:
                    await self.end_game(False, "3 Quêtes échouées")
                    return

                if sum([1 for x in self.quests if x == -1]) == 3:
                    if sum([1 for x in self.players.values() if x.role == "assassin"]):
                        await self.info_view.clear()
                        await self.channel.send(
                            embed=discord.Embed(
                                title="Assassinat",
                                description="3 Quêtes ont été réussies. Les méchants vont maintenant délibérer sur quelle personne l'Assassin va tuer.\n**Que les gentils coupent leurs micros.**",
                                color=global_values.color
                            ),
                            view=AssassinView(self)
                        )
                    else:
                        await self.end_game(True, "3 Quêtes réussies")

                    return

                await self.next_turn()
                return

            for player_id in self.team:
                if "cancel" in self.players[player_id].quest_choices:
                    self.players[player_id].quest_choices.remove("cancel")

            empji = str(global_values.quest_choices["emojis"]["cancel"])
            await self.send_info(
                info={
                    "name": empji + " Quête annulée " + empji,
                    "value": "**Arthur a décidé d'annuler la quête.** Le prochain leader va proposer une nouvelle composition."
                }
            )

            self.refused += 1

            await self.next_turn()

    # Passe au prochain tour
    async def next_turn(self, message=None):
        if self.game_rules["lady_of_the_lake"] and self.round >= 2:
            # lady = self.players[self.order[self.lady_of_the_lake]]

            # valid_candidates = [x for i, x in enumerate(self.order) if x != lady.user.id]
            # emojis = [global_values.number_emojis[self.order.index(x)] for x in valid_candidates]
            # choices = ["`" + str(self.players[x].user) + "`" for x in valid_candidates]

            # async def inspect(reactions):
            #     inspected = self.players[valid_candidates[reactions[lady.user.id][0]]]

            #     self.lady_of_the_lake = self.order.index(inspected.user.id)

            #     await lady_choice_message.message.edit(embed=discord.Embed(
            #         title="🔎 Inspection 🔎",
            #         description="L'allégeance de `" + str(inspected.user) + "` est " + ("🟦 Gentil" if inspected.allegiance == "good" else "🟥 Méchant" if inspected.allegiance == "evil" else "🟩 Solo"),
            #         color=global_values.color))

            #     await self.start_turn({
            #         "name": "🔎 Inspection 🔎",
            #         "value": "La Dame du Lac (`" + str(lady.user) + "`) a inspecté l'allégeance de `" + str(inspected.user) + "`"})

            # async def cond(reactions):
            #     return len(reactions[self.order[self.lady_of_the_lake]]) == 1

            # lady_choice_message = ReactionMessage(
            #     cond,
            #     inspect,
            #     temporary=False
            # )

            # await lady_choice_message.send(
            #     lady.user,
            #     "Choisissez qui vous souhaitez inspecter",
            #     "",
            #     0x2e64fe,
            #     choices,
            #     emojis=emojis
            # )

            self.save({"type":"next_turn"})
        else:
            await self.start_turn(message)

    # Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, good_wins, cause):
        if good_wins is True:
            embed = discord.Embed(title="[AVALON] Victoire des Gentils 🟦 par " + cause + " !", color=0x2e64fe)
        elif good_wins is False:
            embed = discord.Embed(title="[AVALON] Victoire des Méchants 🟥 par " + cause + " !", color=0xef223f)
        else:
            embed = discord.Embed(title="[AVALON] Victoire " + ("d'" if good_wins[:1] in ["E", "A", "I", "O", "U", "Y"] else "de ") + good_wins + " par " + cause  + " !", color=0x76ee00)

        embed.description = "**Joueurs :**\n" + '\n'.join([self.players[x].index_emoji + " `" + str(self.players[x].user) + "` : " + global_values.visual_roles[self.players[x].role] for i, x in enumerate(self.order)])

        await self.info_view.clear()

        await self.channel.send(embed=embed)
        self.delete_save()
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
            "info_message": self.info_view.message.id if self.info_view else None,
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
                "user": player.user.id,
                "index_emoji": player.index_emoji
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
        self.info_view = GameView(self)
        self.info_view.message = await self.channel.fetch_message(object["info_message"]) if object["info_message"] else None
        self.played = object["played"]
        self.lady_of_the_lake = object["lady_of_the_lake"]
        self.players = {}
        self.team = []

        for id in object["team"]:
            self.team.append(int(id))

        for id, info in object["players"].items():
            player = self.players[int(id)] = classes[info["role"]](self, client.get_user(info["user"]))
            player.last_vote = info["last_vote"]
            player.inspected = info["inspected"]
            player.quest_choices = info["quest_choices"]
            player.info_message = await player.user.fetch_message(info["info_message"]) if info["info_message"] else None
            player.index_emoji = info["index_emoji"]

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
