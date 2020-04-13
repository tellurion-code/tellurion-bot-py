import discord
import random
import math

from modules.codenames.player import Player
from modules.codenames.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.codenames.globals as globals

class Game:
    def __init__(self, message):
        self.channel = message.channel
        self.players = {
            message.author.id: Player(message.author)
        } #Dict pour rapidement accéder aux infos
        self.spy_masters = [] #Les Spy Masters, id
        self.turn = "none" #Le tour en cours. "bleu" = bleu, "rouge" = rouge, "none" = pas commencé
        self.board = [] #Liste des mots utilisés pour la partie
        self.colors = [] #Liste des couleurs des mots, correspond aux mots dans board
        self.revealed = [] #Liste des couleurs révélées
        self.hint = "" #Dernier indice donné
        self.affected = 0 #Nombre de nombres affectés par l'indice

        self.board.extend(random.sample(globals.words, 25))

        for i in range(len(self.board)):
            self.colors.append("yellow")

        for i in range(len(self.board)):
            self.revealed.append("white")

        self.colors[random.randrange(len(self.colors))] = "black"

        for i in range(9):
            while True:
                index = random.randrange(len(self.colors))
                color = self.colors[index]
                if color == "yellow":
                    break

            self.colors[index] = "blue"

        for i in range(8):
            while True:
                index = random.randrange(len(self.colors))
                color = self.colors[index]
                if color == "yellow":
                    break

            self.colors[index] = "red"

    async def start_game(self):
        self.turn = "blue"

        async def cond_masters(reactions):
            ok = True

            for id in self.players:
                if id in reactions:
                    if len(reactions[id]) != 1:
                        ok = False
                        break
                else:
                    ok = False
                    break

            return ok

        async def set_teams(reactions):
            choices = []
            for id, indexes in reactions.items():
                self.players[id].team = "red" if indexes[0] == 1 else "blue"
                choices.append(id)

            choices.sort(key = lambda e: self.players[e].team)

            await self.message.message.clear_reactions()

            embed = self.message.message.embeds[0]
            embed.title = "Equipes choisies ✅"
            embed.description = ""
            await self.message.message.edit(embed = embed)

            async def set_spy_masters(reactions):
                embed = self.message.message.embeds[0]
                embed.title = "Spy Masters choisis ✅"
                embed.description = ""

                votes = []
                for i, id in enumerate(choices):
                    votes.append([id, 0])
                    for indexes in reactions.values():
                        if indexes[0] == i:
                            votes[-1][1] += 1

                random.shuffle(votes)
                votes.sort(key = lambda e: e[1])

                self.spy_masters = [0, 0]
                for vote in votes:
                    for i in range(2):
                        if self.players[vote[0]].team == ("red" if i == 1 else "blue") and self.spy_masters[i] == 0:
                            self.spy_masters[i] = vote[0]

                value = ""
                for id in self.spy_masters:
                    await self.players[id].user.send("||\n\n\n\n\n\n\n\n||Tu es le Spy Master de ton équipe. Utilise %codenames send pour envoyer un indice quand c'est ton tour")
                    value += globals.color_emojis[self.players[id].team] + " `" + str(self.players[id].user) + "`\n"

                embed.set_field_at(0,
                    name = "Résultats :",
                    value = value
                )

                await self.message.message.clear_reactions()
                await self.message.message.edit(embed = embed)

                self.message = None

                await self.send_info()

            def check_masters(reaction, user):
                if reaction.emoji == "✅":
                    return True

                if user.id in self.players:
                    return self.players[choices[globals.number_emojis.index(reaction.emoji)]].team == self.players[user.id].team
                else:
                    return False

            async def update_master_votes(reactions2):
                votes = {}
                for i, id in enumerate(choices):
                    votes[id] = 0
                    for indexes in reactions2.values():
                        if indexes[0] == i:
                            votes[id] += 1

                embed = self.message.message.embeds[0]
                embed.set_field_at(0,
                    name = "Votes",
                    value = '\n'.join([globals.color_emojis[self.players[x].team] + " `" + str(self.players[x].user) + "` : " + str(votes[x]) for i, x in enumerate(choices)])
                )
                await self.message.message.edit(embed = embed)

            self.message = ReactionMessage(cond_masters,
                set_spy_masters,
                check = check_masters,
                update = update_master_votes,
                temporary = False
            )

            await self.message.send(self.channel,
                "Votez pour votre Spy Master",
                "Les égalités seront résolues au hasard\n\n",
                0x880088,
                ["`" + str(self.players[x].user) + "`" for x in choices],
                fields = [
                    {
                        "name": "Votes",
                        "value": '\n'.join([globals.color_emojis[self.players[x].team] + " `" + str(self.players[x].user) + "` : 0" for i, x in enumerate(choices)])
                    }
                ]
            )
        async def cond_teams(reactions):
            ok = False

            old_team = -1
            for id, indexes in reactions.items():
                if old_team == -1:
                    old_team = indexes[0]
                elif old_team != indexes[0]:
                    ok = True
                    break

            if not ok:
                return False

            for id in self.players:
                if id in reactions:
                    if len(reactions[id]) != 1:
                        ok = False
                        break
                else:
                    ok = False
                    break

            return ok

        async def update_comp(reactions):
            teams = [[],[]]
            for id, indexes in reactions.items():
                if len(indexes) == 1:
                    teams[indexes[0]].append(id)

            embed = self.message.message.embeds[0]

            embed.set_field_at(0, name = "**Equipe Bleue**",
                value = "Joueurs : " + ', '.join([str(self.players[x].user) for x in teams[0]]),
                inline = False
            )
            embed.set_field_at(1, name = "**Equipe Rouge**",
                value = "Joueurs : " + ', '.join([str(self.players[x].user) for x in teams[1]]),
                inline = False
            )

            await self.message.message.edit(embed = embed)

        self.message = ReactionMessage(cond_teams,
            set_teams,
            check = lambda r, u: u.id in self.players,
            update = update_comp,
            temporary = False
        )

        await self.message.send(self.channel,
            "Chosissez votre équipe",
            "",
            0x880088,
            ["🟦 Bleue", "🟥 Rouge"],
            fields = [
                {
                    "name":"**Equipe Bleue**",
                    "value": "Joueurs :",
                    "inline": False
                },
                {
                    "name": "**Equipe Rouge**",
                    "value": "Joueurs :",
                    "inline": False
                },
            ]
        )

    async def send_info(self):
        board = "```"
        word_length = 16
        for i, card in enumerate(self.board):
            board += " " * math.floor((word_length - len(card))/2) + card + " " * math.ceil((word_length - len(card))/2) + ("|\n" if (i + 1) % 5 == 0 else "|")
        board += "```"

        colors = ""
        card_count = 0
        for card in self.colors:
            if card == self.turn:
                card_count += 1

        for i, card in enumerate(self.revealed):
            colors += globals.color_emojis[card] + ("\n" if (i + 1) % 5 == 0 else "")
            if card == self.turn:
                card_count -= 1

        embed = discord.Embed(title = "Tour de l'équipe " + ("bleue" if self.turn == "blue" else "rouge") + " (" + str(card_count) + " cartes restantes)",
            description = ("Indice : " + self.hint + " (" + str(self.affected) + ")") if self.hint != "" else "",
            color = 0x0000ff if self.turn == "blue" else 0xff0000)

        embed.add_field(name = "Couleurs révélées des cartes",
            value = colors)

        if self.message:
            await self.message.edit(content = board, embed = embed)
        else:
            self.message = await self.channel.send(board, embed =  embed)

        for id in self.spy_masters:
            await self.send_spy_master_infos(self.players[id])

    async def send_spy_master_infos(self, target):
        board = "```"
        word_length = 16
        for i, card in enumerate(self.board):
            board += " " * math.floor((word_length - len(card))/2) + card + " " * math.ceil((word_length - len(card))/2) + ("|\n" if (i + 1) % 5 == 0 else "|")
        board += "```"

        colors = ""
        revealed = ""
        card_count = 0
        for i, card in enumerate(self.colors):
            colors += globals.color_emojis[card] + ("\n" if (i + 1) % 5 == 0 else "")
            if card == self.turn:
                card_count += 1

        for i, card in enumerate(self.revealed):
            revealed += globals.color_emojis[card] + ("\n" if (i + 1) % 5 == 0 else "")
            if card == self.turn:
                card_count -= 1

        embed = discord.Embed(title = "Tour de l'équipe " + ("bleue" if self.turn == "blue" else "rouge") + " (" + str(card_count) + " cartes restantes)",
            description = ("Indice : " + self.hint + " (" + str(self.affected) + ")") if self.hint != "" else "",
            color = 0x0000ff if self.turn == "blue" else 0xff0000)

        embed.add_field(name = "Couleurs des cartes",
            value = colors)

        embed.add_field(name = "Couleurs révélées des cartes",
            value = revealed)

        if target.message:
            await target.message.edit(content = board, embed =  embed)
        else:
            target.message = await target.user.send(board, embed =  embed)

    async def end_game(self, current_win):
        if not current_win:
            self.turn = "blue" if self.turn == "red" else "red"

        board = "```"
        word_length = 16
        for i, card in enumerate(self.board):
            board += " " * math.floor((word_length - len(card))/2) + card + " " * math.ceil((word_length - len(card))/2) + ("|\n" if (i + 1) % 5 == 0 else "|")
        board += "```"

        colors = ""
        revealed = ""
        card_count = 0
        for i, card in enumerate(self.colors):
            colors += globals.color_emojis[card] + ("\n" if (i + 1) % 5 == 0 else "")
            if card == self.turn:
                card_count += 1

        for i, card in enumerate(self.revealed):
            revealed += globals.color_emojis[card] + ("\n" if (i + 1) % 5 == 0 else "")
            if card == self.turn:
                card_count -= 1

        embed = discord.Embed(title = "Victoire de l'équipe " + ("bleue !" if self.turn == "blue" else "rouge !"),
            color = 0x0000ff if self.turn == "blue" else 0xff0000 )

        embed.add_field(name = "Couleurs des cartes",
            value = colors)

        embed.add_field(name = "Couleurs révélées des cartes",
            value = revealed)

        await self.message.edit(content = board, embed =  embed)
        for id in self.spy_masters:
            await self.players[id].message.edit(content = board, embed =  embed)

        globals.games.pop(self.channel.id)
