import discord
import random
import math

from modules.avalon.player import Player, Good, Evil, Merlin, Percival, Lancelot, Assassin, Morgane, Mordred, Oberon, Agrav1, Agrav2
from modules.avalon.reaction_message import ReactionMessage

import modules.avalon.globals as globals

class Game:
    def __init__(self, mainclass, **kwargs):
        message = kwargs["message"] if "message" in kwargs else None
        self.mainclass = mainclass

        if message:
            self.channel = message.channel
            self.players = {
                message.author.id: Player(message.author)
            } #Dict pour rapidement accéder aux infos
        else:
            self.channel = None
            self.players = {}

        self.order = [] #Ordre des id des joueurs
        self.turn = -1 #Le tour (index du leader) en cours, -1 = pas commencé
        self.round = 0 #Quête en cours
        self.team = {} #Equipe qui part en quête. Contient les indices d'ordre et les id
        self.quests = [] #Réussite (-1) ou échec (0) des quêtes. Chiffre = pas faite
        self.refused = 0 #Nombre de gouvernements refusés
        self.info_message = None
        self.played = [] #Dernière cartes jouées
        self.roles = [] #Rôles

    # async def reload(self, object, client):
    #     await self.deserialize(object, client)
    #
    #     if object["state"]["type"] == "send_chancellor_choice":
    #         await self.send_chancellor_choice()
    #     elif object["state"]["type"] == "send_laws":
    #         await self.send_laws()

    async def start_game(self):
        self.turn = 0

        quests = [
            [], #0
            [], #1
            [1, 1, 2, 2, 2], #2, Debug
            [2, 2, 2, 2, 2], #3
            [1, 2, 2, 2, 2], #4
            [2, 3, 2, 3, 3], #5
            [2, 3, 4, 3, 4], #6
            [2, 3, 3, 4, 4], #7
            [3, 4, 4, 5, 5], #8
            [3, 4, 4, 5, 5], #9
            [3, 4, 4, 5, 5] #10
        ]

        self.quests = quests[len(self.players)]

        roles = [
            [], #0?
            ["good"], #1
            ["good", "evil"], #2, Debug
            ["good", "good", "evil"], #3
            ["good", "good", "good", "evil"], #4
            ["merlin", "percival", "good", "morgane", "assassin"], #5
            ["merlin", "percival", "good", "good", "morgane", "assassin"], #6
            ["merlin", "percival", "good", "good", "evil", "morgane", "assassin"], #7
            ["merlin", "percival", "good", "good", "good", "evil", "morgane", "assassin"], #8
            ["merlin", "percival", "good", "good", "good", "good", "evil", "morgane", "assassin"], #9
            ["merlin", "percival", "good", "good", "good", "good", "evil", "evil", "morgane", "assassin"], #10
        ]

        classes = {
            "good": Good,
            "evil": Evil,
            "merlin": Merlin,
            "percival": Percival,
            "lancelot": Lancelot,
            "assassin": Assassin,
            "morgane": Morgane,
            "mordred": Mordred,
            "oberon": Oberon,
            "agrav1": Agrav1,
            "agrav2": Agrav2
        }

        if len(self.roles) == 0:
            self.roles = roles[len(self.players)]

        for id in self.players:
            self.order.append(id)

        random.shuffle(self.order)
        random.shuffle(self.roles)

        for i in range(len(self.order)):
            self.players[self.order[i]] = classes[self.roles[i]](self.players[self.order[i]].user)

        for i in range(len(self.order)):
            await self.players[self.order[i]].game_start(self)

        await self.send_info(mode = "set", info = "Début de partie\n")
        await self.send_team_choice()

    #Envoies un message à tous les joueurs + le channel
    async def broadcast(self, _embed, **kwargs):
        exceptions = kwargs["exceptions"] if "exceptions" in kwargs else []
        mode = kwargs["mode"] if "mode" in kwargs else "normal"

        if mode == "append": #append = ajoute à la description
            if self.info_message:
                embed = self.info_message.embeds[0]
                embed.description += _embed.description

                await self.info_message.edit(embed = embed)
            else:
                self.info_message = await self.channel.send(embed = _embed)

            for id, player in self.players.items():
                if id not in exceptions:
                    if player.info_message:
                        embed = player.info_message.embeds[0]
                        embed.description += _embed.description

                        await player.info_message.edit(embed = embed)
                    else:
                        player.info_message = await player.user.send(embed = _embed)
        elif mode == "replace": #replace = modifie le dernier message
            if self.info_message:
                await self.info_message.edit(embed = _embed)
            else:
                self.info_message = await self.channel.send(embed = _embed)

            for id, player in self.players.items():
                if id not in exceptions:
                    if player.info_message:
                        await player.info_message.edit(embed = _embed)
                    else:
                        player.info_message = await player.user.send(embed = _embed)
        elif mode == "set": #set = nouveau message
            self.info_message = await self.channel.send(embed = _embed)
            for id, player in self.players.items():
                if id not in exceptions:
                    player.info_message = await player.user.send(embed = _embed)
        else: #normal = nouveau message sans mémoire
            await self.channel.send(embed = _embed)
            for id, player in self.players.items():
                if id not in exceptions:
                    await player.user.send(embed = _embed)

    #Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        info = kwargs["info"] if "info" in kwargs else ""
        color = kwargs["color"] if "color" in kwargs else globals.color

        embed = discord.Embed(title = "[AVALON] Tour de `" + str(self.players[self.order[self.turn]].user) + "` 👑️",
            description = info,
            color = color
        )

        if self.round == 3 and len(self.players) >= 7:
            embed.description += "⚠️ Deux Echecs requis pour faire rater la quête ⚠️\n"

        embed.description += "__Chevaliers:__\n" + '\n'.join([self.players[x].last_vote[:1] + globals.number_emojis[i] + " `" + str(self.players[x].user) + "` " + ("👑" if self.turn == i else "") for i, x in enumerate(self.order)])

        if len(self.team):
            embed.add_field(name = "Participants à la Quête :",
                value = '\n'.join([(globals.number_emojis[i] + ' `' + str(self.players[x].user) + '`') for i, x in self.team.items()]),
                inline = False)

        embed.add_field(name = "Quêtes :",
            value = " ".join([globals.number_emojis[x - 1] if x > 0 else (globals.quest_emojis["success"] if x else globals.quest_emojis["failure"]) for x in self.quests]))

        embed.add_field(name = "Equipes refusées :",
            value = "🟧" * self.refused + "🔸" * ( 4 - self.refused ))

        if len(self.played):
            embed.add_field(name = "Choix dans la dernière quête :",
                value = " ".join(self.played),
                inline = False)

        # --[ANCIEN BROADCAST]--
        # await self.channel.send(embed = embed)
        # for player in self.players.values():
        #     await player.user.send(embed = embed)

        await self.broadcast(embed, mode = mode)

    #Est aussi un début de tour, envoies le choix de chancelier
    async def send_team_choice(self):
        #self.save({"type": "send_chancellor_choice"})

        leader = self.players[self.order[self.turn]] #Tour actuel

        valid_candidates = [x for i, x in enumerate(self.order) if i != self.turn or globals.debug]
        emojis = [globals.number_emojis[self.order.index(x)] for x in valid_candidates]
        choices = ["`" + str(self.players[x].user) + "`" for x in valid_candidates]

        async def propose_team(reactions):
            for i in reactions[leader.user.id]:
                self.team[i] = valid_candidates[i]

            await self.send_info()

            for id in self.order:
                await self.players[id].send_vote(self)

        async def cond(reactions):
            return len(reactions[self.order[self.turn]]) == self.quests[self.round]

        await ReactionMessage(cond,
            propose_team
        ).send(leader.user,
            "Choisissez votre Equipe (" + str(self.quests[self.round]) + (" participants)" if self.quests[self.round] > 1 else " participant)"),
            "",
            globals.color,
            choices,
            emojis = emojis
        )

    #Appelé à chaque fois qu'un joueur vote. Vérifie les votes manquants puis la majorité
    #TODO: Trouvez pourquoi il est call 2 fois d'affilée parfois
    async def check_vote_end(self):
        missing = False

        for id in self.order:
            player = self.players[id]

            if player.vote_message:
                embed = player.vote_message.message.embeds[0]
                embed.set_field_at(0, name = "Votes:",
                    value = ' '.join(["✉️" if self.players[x].last_vote == "" else "📩" for x in self.order])
                )

                if player.last_vote != "":
                    embed.description = "Le Leader `" + str(self.players[self.order[self.turn]].user) + "` a proposé comme Equipe:\n" + '\n'.join([(globals.number_emojis[i] + ' `' + str(self.players[x].user) + '`') for i, x in self.team.items()]) + "\n\nVous avez voté " + player.last_vote
                    embed.color = 0x00ff00 if player.last_vote[:1] == "✅" else 0xff0000
                else:
                    missing = True

                await player.vote_message.message.edit(embed = embed)

        if not missing:
            for_votes = len([self.players[x] for x in self.order if self.players[x].last_vote[:1] == "✅"])

            await self.send_info(color = 0x00ff00 if for_votes > len(self.order)/2 else 0xff0000) #Change la couleur du message en fonction

            if for_votes > len(self.order)/2:
                #self.save({"type": "send_laws"})

                await self.broadcast(discord.Embed(title = "Equipe acceptée",
                    description = "L'Equipe proposée a été acceptée. Elle va partir en quête et choisir si elle sera une Réussite ou un Echec.",
                    color = 0x00ff00
                ), mode = "set")

                for id in self.team.values():
                    self.players[id].last_vote = ""
                    await self.players[id].send_choice(self)
            else:
                self.refused += 1

                if self.refused == 5:
                    await self.end_game(False, "5 Equipes refusées")
                elif self.refused >= 1:
                    await self.next_turn("**L'Equipe proposée a été refusée**\n")

    async def check_quest_end(self):
        missing = False

        for id in self.team.values():
            player = self.players[id]

            if player.vote_message:
                embed = player.vote_message.message.embeds[0]

                if player.last_vote != "":
                    print(player.last_vote[:1], globals.quest_emojis["success"])

                    embed.description = "Vous avez choisi " + player.last_vote
                    embed.color = (0x00ff00 if globals.quest_emojis["success"] in player.last_vote else 0xff0000 if globals.quest_emojis["failure"] in player.last_vote else 0x0000ff)
                else:
                    missing = True

                await player.vote_message.message.edit(embed = embed)

        if not missing:
            self.played = [self.players[x].last_vote[:1] for x in self.team.values()]
            random.shuffle(self.played)

            fails = len([x for x in self.played if x == globals.quest_emojis["failure"]])
            reverses = len([x for x in self.played if x == globals.quest_emojis["reverse"]])

            success = fails < (2 if self.round == 3 and len(self.players) >= 7 else 1)
            if reverses == 1:
                success = not success

            self.quests[self.round] = -1 if success else 0
            self.round += 1
            self.refused = 0

            await self.broadcast(discord.Embed(title = "Equipe acceptée: Quête " + (("réussie " + globals.quest_emojis["success"]) if success else ("échouée " + globals.quest_emojis["failure"])),
                description = "L'Equipe proposée a été acceptée. Elle va partir en quête et choisir si elle sera une Réussite ou un Echec.\nLa quête a été " + ("une réussite." if success else "un échec."),
                color = 0x2e64fe if success else 0xef223f
            ), mode = "replace")

            if len([x for x in self.quests if x == 0]) == 3:
                await self.end_game(False, "3 Quêtes échouées")
            elif len([x for x in self.quests if x == -1]) == 3:
                if len([x for x in self.players.values() if x.role == "merlin"]):
                    await self.broadcast(discord.Embed(title = "Assassinat",
                        description = "3 Quêtes ont été réussies. Les méchants vont maintenant délibérer sur quelle personne l'Assassin va tuer.\n**Que les gentils coupent leurs micros.**",
                        color = globals.color
                    ))

                    await [x for x in self.players.values() if x.role == "assassin"][0].send_assassin_choice(self)
                else:
                    await self.end_game(True, "3 Quêtes réussies")
            else:
                await self.next_turn()

    #Passe au prochain tour
    async def next_turn(self, message = ""):
        self.turn = (self.turn + 1) % len(self.order)

        for player in self.players.values():
            player.last_vote = ""

        self.team = {}

        await self.send_info(mode = "set", info = message)
        await self.send_team_choice()

    #Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, good_wins, cause):
        if good_wins:
            embed = discord.Embed(title = "Victoire des Gentils 🟦️ par " + cause  + " !", color = 0x2e64fe)
        else:
            embed = discord.Embed(title = "Victoire des Méchants 🟥 par " + cause  + " !", color = 0xef223f)

        roles = {
            "good": "🟦 Libéral",
            "evil": "🟥 Fasciste",
            "merlin": "🧙‍♂️ Merlin",
            "percival": "🤴 Perceval",
            "lancelot": "🛡️ Lancelot",
            "assassin": "🗡️ Assassin",
            "morgane": "🧙‍♀️ Morgane",
            "mordred": "😈 Mordred",
            "oberon": "😶 Oberon",
            "agrav1": "⚔️ Agravain",
            "agrav2": "⚔️ Agravain"
        }

        embed.description = "__Joueurs :__\n" + '\n'.join([globals.number_emojis[i] + " `" + str(self.players[x].user) + "` : " + roles[self.players[x].role] for i,x in enumerate(self.order)])

        await self.broadcast(embed)
        #self.delete_save()
        globals.games.pop(self.channel.id)

    # def serialize(self, state):
    #     object = {
    #         "channel": self.channel.id,
    #         "order": self.order,
    #         "turn": self.turn,
    #         "chancellor": self.chancellor,
    #         "after_special_election": self.after_special_election,
    #         "deck": self.deck,
    #         "discard": self.discard,
    #         "policies": self.policies,
    #         "liberal_laws": self.liberal_laws,
    #         "fascist_laws": self.fascist_laws,
    #         "term_limited": self.term_limited,
    #         "refused": self.refused,
    #         "info_message": self.info_message.id if self.info_message else None,
    #         "played": self.played,
    #         "players": {},
    #         "state": state
    #     }
    #
    #     for id, player in self.players.items():
    #         object["players"][id] = {
    #             "role": player.role,
    #             "last_vote": player.last_vote,
    #             "inspected": player.inspected,
    #             "info_message": player.info_message.id if player.info_message else None,
    #             "user": player.user.id
    #         }
    #
    #     return object
    #
    # async def deserialize(self, object, client):
    #     self.channel = client.get_channel(object["channel"])
    #     self.order = object["order"]
    #     self.turn = object["turn"]
    #     self.chancellor = object["chancellor"]
    #     self.after_special_election = object["after_special_election"]
    #     self.deck = object["deck"]
    #     self.discard = object["discard"]
    #     self.policies = object["policies"]
    #     self.liberal_laws = object["liberal_laws"]
    #     self.fascist_laws = object["fascist_laws"]
    #     self.term_limited = object["term_limited"]
    #     self.refused = object["refused"]
    #     self.info_message = await self.channel.fetch_message(object["info_message"]) if object["info_message"] else None
    #     self.played = object["played"]
    #     self.players = {}
    #
    #     classes = {
    #         "liberal": Liberal,
    #         "fascist": Fascist,
    #         "hitler": Hitler,
    #         "goebbels": Goebbels,
    #         "merliner": Merliner
    #     }
    #
    #     for id, info in object["players"].items():
    #         player = self.players[int(id)] = classes[info["role"]](client.get_user(info["user"]))
    #         player.last_vote = info["last_vote"]
    #         player.inspected = info["inspected"]
    #         player.info_message = await player.user.fetch_message(info["info_message"]) if info["info_message"] else None
    #
    # def save(self, state):
    #     if self.mainclass.objects.save_exists("games"):
    #         object = self.mainclass.objects.load_object("games")
    #     else:
    #         object = {}
    #
    #     object[self.channel.id] = self.serialize(state)
    #     self.mainclass.objects.save_object("games", object)
    #
    # def delete_save(self):
    #     if self.mainclass.objects.save_exists("games"):
    #         object = self.mainclass.objects.load_object("games")
    #         if str(self.channel.id) in object:
    #             object.pop(str(self.channel.id))
    #
    #         self.mainclass.objects.save_object("games", object)
    #     else:
    #         print("no save")
