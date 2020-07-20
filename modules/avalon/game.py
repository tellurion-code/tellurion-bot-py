import discord
import random

from modules.avalon.player import Player, Good, Evil, Merlin, Percival, Gawain, Karadoc, Galaad, Uther, Arthur, Vortigern, Assassin, Morgane, Mordred, Oberon, Lancelot, Accolon, Kay, Agravain, Elias, Maleagant
from modules.reaction_message.reaction_message import ReactionMessage

import modules.avalon.globals as global_values

classes = {
    "good": Good,
    "evil": Evil,
    "merlin": Merlin,
    "percival": Percival,
    "karadoc": Karadoc,
    "gawain": Gawain,
    "galaad": Galaad,
    "uther": Uther,
    "arthur": Arthur,
    "vortigern": Vortigern,
    "assassin": Assassin,
    "morgane": Morgane,
    "mordred": Mordred,
    "oberon": Oberon,
    "lancelot": Lancelot,
    "accolon": Accolon,
    "kay": Kay,
    "agravain": Agravain,
    "elias": Elias,
    "maleagant": Maleagant
}

class Game:
    def __init__(self, mainclass, **kwargs):
        message = kwargs["message"] if "message" in kwargs else None
        self.mainclass = mainclass

        if message:
            self.channel = message.channel
            self.players = {
                message.author.id: Player(message.author)
            }  # Dict pour rapidement accéder aux infos
        else:
            self.channel = None
            self.players = {}

        self.order = []  # Ordre des id des joueurs
        self.turn = -1  # Le tour (index du leader) en cours, -1 = pas commencé
        self.round = 0  # Quête en cours
        self.team = {}  # Equipe qui part en quête. Contient les indices d'ordre et les id
        self.quests = []  # Réussite (-1) ou échec (0) des quêtes. Chiffre supérieur à 0 = pas faite
        self.refused = 0  # Nombre de gouvernements refusés
        self.info_message = None
        self.played = []  # Dernière cartes jouées
        self.roles = []  # Rôles
        self.phase = "team_selection"
        self.lady_of_the_lake = 0  # Index du joueur qui a la Dame du Lac
        self.game_rules = {
            "lancelot_know_evil": False,
            "4th_quest_two_failures": True,
            "uther_learns_role": False,
            "lady_of_the_lake": False,
            "agravain_know_oberon": False
        }

    async def reload(self, object, client):
        await self.deserialize(object, client)

        if object["state"]["type"] == "send_team_choice":
            await self.send_team_choice()
        elif object["state"]["type"] == "quest":
            await self.send_players_quest_choice()
        elif object["state"]["type"] == "next_turn":
            await self.next_turn()

    async def start_game(self):
        self.turn = 0

        quests = [
            [],  # 0
            [],  # 1
            [1, 1, 2, 2, 2],  # 2, Debug
            [1, 2, 2, 2, 2],  # 3
            [2, 2, 2, 2, 2],  # 4
            [2, 3, 2, 3, 3],  # 5
            [2, 3, 4, 3, 4],  # 6
            [2, 3, 3, 4, 4],  # 7
            [3, 4, 4, 5, 5],  # 8
            [3, 4, 4, 5, 5],  # 9
            [3, 4, 4, 5, 5]  # 10
        ]

        self.quests = quests[len(self.players)]

        roles = [
            [],  # 0?
            ["good"],  # 1
            ["good", "evil"],  # 2, Debug
            ["good", "good", "evil"],  # 3
            ["good", "good", "good", "evil"],  # 4
            ["merlin", "percival", "good", "morgane", "assassin"],  # 5
            ["merlin", "percival", "good", "good", "morgane", "assassin"],  # 6
            ["merlin", "percival", "good", "good", "evil", "morgane", "assassin"],  # 7
            ["merlin", "percival", "good", "good", "good", "evil", "morgane", "assassin"],  # 8
            ["merlin", "percival", "good", "good", "good", "good", "evil", "morgane", "assassin"],  # 9
            ["merlin", "percival", "good", "good", "good", "good", "evil", "evil", "morgane", "assassin"],  # 10
        ]

        if len(self.roles) == 0:
            self.roles = roles[len(self.players)]

        for player_id in self.players:
            self.order.append(player_id)

        random.shuffle(self.order)
        random.shuffle(self.roles)

        for i in range(len(self.order)):
            self.players[self.order[i]] = classes[self.roles[i]](self.players[self.order[i]].user)

        for i in range(len(self.order)):
            await self.players[self.order[i]].game_start(self)

        random.shuffle(self.roles)

        self.lady_of_the_lake = len(self.players)-1

        await self.send_info(mode="set")
        await self.send_team_choice()

    # Envoie un message à tous les joueurs + le channel
    async def broadcast(self, _embed, **kwargs):
        exceptions = kwargs["exceptions"] if "exceptions" in kwargs else []
        mode = kwargs["mode"] if "mode" in kwargs else "normal"

        if mode == "append":  # append = ajoute à la description
            if self.info_message:
                embed = self.info_message.embeds[0]
                embed.description += _embed.description

                await self.info_message.edit(embed=embed)
            else:
                self.info_message = await self.channel.send(embed=_embed)

            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    if player_object.info_message:
                        embed = player_object.info_message.embeds[0]
                        embed.description += _embed.description

                        await player_object.info_message.edit(embed=embed)
                    else:
                        player_object.info_message = await player_object.user.send(embed=_embed)
        elif mode == "replace":  # replace = modifie le dernier message
            if self.info_message:
                await self.info_message.edit(embed=_embed)
            else:
                self.info_message = await self.channel.send(embed=_embed)

            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    if player_object.info_message:
                        await player_object.info_message.edit(embed=_embed)
                    else:
                        player_object.info_message = await player_object.user.send(embed=_embed)
        elif mode == "set":  # set = nouveau message
            self.info_message = await self.channel.send(embed=_embed)
            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    player_object.info_message = await player_object.user.send(embed=_embed)
        else:  # normal = nouveau message sans mémoire
            await self.channel.send(embed=_embed)
            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    await player_object.user.send(embed=_embed)

    # Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        info = kwargs["info"] if "info" in kwargs else None
        color = kwargs["color"] if "color" in kwargs else global_values.color

        embed = discord.Embed(
            title="[AVALON] Tour de `" + str(self.players[self.order[self.turn]].user) + "` 👑",
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
            value='\n'.join([self.players[x].last_vote.split(" ")[0] + global_values.number_emojis[i] + " `" + str(self.players[x].user) + "` " + ("👑" if self.turn == i else "") + ("🌊" if self.lady_of_the_lake == i and self.game_rules["lady_of_the_lake"] else "") for i, x in enumerate(self.order)]),
            inline=False
        )

        if len(self.team):
            embed.add_field(
                name="Participants à la Quête :",
                value='\n'.join([(global_values.number_emojis[i] + ' `' + str(self.players[x].user) + '`') for i, x in self.team.items()]),
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

        # --[ANCIEN BROADCAST]--
        # await self.channel.send(embed = embed)
        # for player in self.players.values():
        #     await player.user.send(embed = embed)

        await self.broadcast(embed, mode=mode)

    async def start_turn(self, message):
        self.phase = "team_selection"
        self.turn = (self.turn + 1) % len(self.order)

        for player in self.players.values():
            player.last_vote = ""
            player.last_choice = ""

            if player.role == "maleagant":
                player.guess = None

        self.team = {}

        await self.send_info(mode="set", info=message)
        await self.send_team_choice()

        self.save({"type":"send_team_choice"})

    # Est aussi un début de tour, envoies le choix de team
    async def send_team_choice(self):
        # self.save({"type": "send_chancellor_choice"})

        leader = self.players[self.order[self.turn]]  # Tour actuel

        valid_candidates = [x for i, x in enumerate(self.order)]
        emojis = [global_values.number_emojis[self.order.index(x)] for x in valid_candidates]
        choices = ["`" + str(self.players[x].user) + "`" for x in valid_candidates]

        embed = discord.Embed(
            title="Equipe Choisie",
            color=global_values.color)

        embed.add_field(
            name="Equipe (" + str(self.quests[self.round]) + (" restants)" if self.quests[self.round] > 1 else " restant)"),
            value="❌ Pas de participant choisi")

        team_message = await leader.user.send(embed=embed)

        async def update(reactions):
            embed = team_message.embeds[0]
            embed.set_field_at(
                0,
                name="Equipe (" + str(max(0, self.quests[self.round] - len(reactions[leader.user.id]))) + (" restants)" if self.quests[self.round] - len(reactions[leader.user.id]) > 1 else " restant)"),
                value='\n'.join([(global_values.number_emojis[self.order.index(valid_candidates[i])] + ' `' + str(self.players[valid_candidates[i]].user) + '`') for i in reactions[leader.user.id]]) if len(reactions[leader.user.id]) else "❌ Pas de participants choisis")

            await team_message.edit(embed=embed)

        async def propose_team(reactions):
            for i in reactions[leader.user.id]:
                self.team[self.order.index(valid_candidates[i])] = valid_candidates[i]

            await team_message.delete()
            await self.send_info()

            for player_id in self.order:
                await self.players[player_id].send_vote(self)

        async def cond(reactions):
            return len(reactions[self.order[self.turn]]) == self.quests[self.round]

        await ReactionMessage(
            cond,
            propose_team,
            update=update
        ).send(
            leader.user,
            "Choisissez votre Equipe (" + str(self.quests[self.round]) + (" participants)" if self.quests[self.round] > 1 else " participant)"),
            "",
            global_values.color,
            choices,
            emojis=emojis
        )

    # Appelé à chaque fois qu'un joueur vote. Vérifie les votes manquants puis la majorité
    # TODO: Trouvez pourquoi il est call 2 fois d'affilée parfois
    async def check_vote_end(self):
        missing = False

        for player_id in self.order:
            player = self.players[player_id]

            if player.vote_message:
                embed = player.vote_message.message.embeds[0]
                embed.set_field_at(
                    0,
                    name="Votes:",
                    value=' '.join(["✉️" if self.players[x].last_vote == "" else "📩" for x in self.order]))

                if player.last_vote != "":
                    embed.description = "Le Leader `" + str(self.players[self.order[self.turn]].user) + "` a proposé comme Equipe:\n" + '\n'.join([(global_values.number_emojis[i] + ' `' + str(self.players[x].user) + '`') for i, x in self.team.items()]) + "\n\nVous avez voté " + player.last_vote
                    embed.color = 0x00ff00 if player.last_vote[:1] == "✅" else 0xff0000
                else:
                    missing = True

                await player.vote_message.message.edit(embed=embed)

        if not missing and self.phase == "team_selection":
            self.phase = "vote_for_team"

            for_votes = len([self.players[x] for x in self.order if self.players[x].last_vote[:1] == "✅"])

            for player_id in self.order:
                player = self.players[player_id]
                if player.vote_message:
                    await player.vote_message.message.delete()

            # Change la couleur du message en fonction
            # await self.send_info(color = 0x00ff00 if for_votes > len(self.order)/2 else 0xff0000)

            if for_votes > len(self.order)/2:
                await self.send_info(
                    info={
                        "name": "Equipe acceptée",
                        "value": "Les membres vont partir en quête et décider de la faire réussire ou échouer."
                    },
                    color=0x2e64fe)

                await self.send_players_quest_choice()

                self.save({"type":"quest"})
            else:
                if self.refused == 4:
                    await self.end_game(False, "5 Equipes refusées")
                else:
                    await self.send_info(
                        info={
                            "name": "Equipe refusée",
                            "value": "Le prochain leader va proposer une nouvelle composition."
                        })

                    self.refused += 1

                    await self.next_turn()

    async def send_players_quest_choice(self):
        for player_id in self.team.values():
            await self.players[player_id].send_choice(self)

        for player in self.players.values():
            if player.role == "maleagant":
                if player.can_guess:
                    await player.send_guess()

    async def check_quest_end(self):
        missing = False

        for player_id in self.team.values():
            player = self.players[player_id]

            if player.last_choice != "":
                if player.vote_message:
                    if player.vote_message.message:
                        embed = player.vote_message.message.embeds[0]

                        embed.description = "Vous avez choisi " + str(global_values.quest_choices["emojis"][player.last_choice]) + " " + global_values.quest_choices["names"][player.last_choice]
                        embed.color = global_values.quest_choices["colors"][player.last_choice]

                        await player.vote_message.message.edit(embed=embed)
            else:
                missing = True

        for player in self.players.values():
            if player.role == "maleagant":
                if player.can_guess and player.guess is None:
                    missing = True

        if not missing and self.phase == "vote_for_team":
            self.phase = "quest"

            for player_id in self.team.values():
                player = self.players[player_id]

                if player.vote_message:
                    await player.vote_message.message.delete()

                if player.last_choice == "sabotage":
                    for id in self.team.values():
                        self.players[id].last_choice = "failure"

            self.played = [self.players[x].last_choice for x in self.team.values()]
            random.shuffle(self.played)

            cancelled = len([x for x in self.played if x == "cancel"])
            fails = len([x for x in self.played if x == "failure"])
            reverses = len([x for x in self.played if x == "reverse"])

            if not cancelled:
                success = fails < (2 if self.round == 3 and len(self.players) >= 7 and self.game_rules["4th_quest_two_failures"] else 1)
                if reverses == 1:
                    success = not success

                self.quests[self.round] = -1 if success else 0

                if len([x for x in self.players.values() if x.role == "maleagant"]):
                    for maleagant in [x for x in self.players.values() if x.role == "maleagant"]:
                        if maleagant.guess != success:
                            maleagant.can_guess = False

                await self.send_info(
                    info={
                        "name": ((str(global_values.quest_choices["emojis"]["success"]) + " Quête réussie " + str(global_values.quest_choices["emojis"]["success"])) if success else (str(global_values.quest_choices["emojis"]["failure"]) + " Quête échouée " + str(global_values.quest_choices["emojis"]["failure"]))),
                        "value": "Choix : " + " ".join([str(global_values.quest_choices["emojis"][x]) for x in self.played])
                    },
                    color=0x76ee00 if success else 0xef223f)

                self.round += 1
                self.refused = 0

                if len([x for x in self.quests if x == 0]) == 3:
                    for player in self.players.values():
                        if player.role == "maleagant":
                            if player.can_guess:
                                await self.end_game("Méléagant 🧿", "sans-faute")
                                return

                    await self.end_game(False, "3 Quêtes échouées")
                elif len([x for x in self.quests if x == -1]) == 3:
                    for player in self.players.values():
                        if player.role == "maleagant":
                            if player.can_guess:
                                await self.end_game("Méléagant 🧿", "sans-faute")
                                return

                    if len([x for x in self.players.values() if x.role == "assassin"]):
                        await self.broadcast(discord.Embed(
                            title="Assassinat",
                            description="3 Quêtes ont été réussies. Les méchants vont maintenant délibérer sur quelle personne l'Assassin va tuer.\n**Que les gentils coupent leurs micros.**",
                            color=global_values.color))

                        await ([x for x in self.players.values() if x.role == "assassin"][0]).send_assassin_choice(self)
                    else:
                        await self.end_game(True, "3 Quêtes réussies")
                else:
                    await self.next_turn()
            else:
                for player_id in self.team.values():
                    if "cancel" in self.players[player_id].quest_choices:
                        self.players[player_id].quest_choices.remove("cancel")

                await self.send_info(
                    info={
                        "name": str(global_values.quest_choices["emojis"]["cancel"]) + " Quête annulée " + str(global_values.quest_choices["emojis"]["cancel"]),
                        "value": "**Arthur a décidé d'annuler la quête.** Le prochain leader va proposer une nouvelle composition."
                    })

                self.refused += 1

                await self.next_turn()

    # Passe au prochain tour
    async def next_turn(self, message=None):
        if self.game_rules["lady_of_the_lake"] and self.round >= 2:
            lady = self.players[self.order[self.lady_of_the_lake]]

            valid_candidates = [x for i, x in enumerate(self.order) if x != lady.user.id]
            emojis = [global_values.number_emojis[self.order.index(x)] for x in valid_candidates]
            choices = ["`" + str(self.players[x].user) + "`" for x in valid_candidates]

            async def inspect(reactions):
                inspected = self.players[valid_candidates[reactions[lady.user.id][0]]]

                self.lady_of_the_lake = self.order.index(inspected.user.id)

                await lady_choice_message.message.edit(embed=discord.Embed(
                    title="🔎 Inspection 🔎",
                    description="L'allégeance de `" + str(inspected.user) + "` est " + ("🟦 Gentil" if inspected.allegiance == "good" else "🟥 Méchant" if inspected.allegiance == "evil" else "🟩 Solo"),
                    color=global_values.color))

                await self.start_turn({
                    "name": "🔎 Inspection 🔎",
                    "value": "La Dame du Lac (`" + str(lady.user) + "`) a inspecté l'allégeance de `" + str(inspected.user) + "`"})

            async def cond(reactions):
                return len(reactions[self.order[self.lady_of_the_lake]]) == 1

            lady_choice_message = ReactionMessage(
                cond,
                inspect,
                temporary=False
            )

            await lady_choice_message.send(
                lady.user,
                "Choisissez qui vous souhaitez inspecter",
                "",
                0x2e64fe,
                choices,
                emojis=emojis
            )

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

        embed.description = "**Joueurs :**\n" + '\n'.join([global_values.number_emojis[i] + " `" + str(self.players[x].user) + "` : " + global_values.visual_roles[self.players[x].role] for i, x in enumerate(self.order)])

        await self.broadcast(embed)
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
            player = self.players[int(id)] = classes[info["role"]](client.get_user(info["user"]))
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
