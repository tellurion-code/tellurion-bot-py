import discord
from discord_components import Button
import random
import math

from modules.codenames.player import Player
from modules.buttons.button import ComponentMessage
from modules.base import BaseClassPython

import modules.codenames.globals as global_values

class Word:
    def __init__(self, word, color):
        self.word = word
        self.color = color
        self.revealed = False


class Game:
    def __init__(self, message):
        self.channel = message.channel
        self.players = {
            message.author.id: Player(message.author)
        } # Dict pour rapidement accéder aux infos
        self.spy_masters = [0, 0] # Les Spy Masters, id
        self.turn = -1 # Le tour en cours. 0 = bleu, 1 = rouge, -1 = pas commencé (et 2 = "gris" vert en vrai, 3 = "noir", gris en vrai)
        self.board = [] # Liste des mots utilisés pour la partie et leurs couleurs (vraies et révélées)
        self.hint = "" # Dernier indice donné
        self.affected = 0 # Nombre de nombres affectés par l'indice
        self.game_message = None
        self.spymaster_message = None

        self.board.extend([Word(x, 2) for x in random.sample(global_values.words, 25)])

        self.board[random.randrange(len(self.board))].color = 3 # Mise en place de l'Assassin

        for i in range(9):
            while True:
                index = random.randrange(len(self.board))
                color = self.board[index].color
                if color == 2:
                    break

            self.board[index].color = 0

        for i in range(8):
            while True:
                index = random.randrange(len(self.board))
                color = self.board[index].color
                if color == 2:
                    break

            self.board[index].color = 1

    async def create_game(self, message):
        async def join_or_leave(button, interaction):
            if interaction.user.id not in self.players:
                self.players[interaction.user.id] = Player(interaction.user)
            else:
                del self.players[interaction.user.id]

            await update_join_message(interaction)

        async def start(button, interaction):
            await interaction.respond(type=6)
            await join_message.delete()
            await self.choose_teams(message)

        join_message = ComponentMessage(
            [
                [
                    {
                        "effect": join_or_leave,
                        "cond": lambda i: True,
                        "label": "Rejoindre ou partir",
                        "style": 1
                    },
                    {
                        "effect": start,
                        "cond": lambda i: i.user.id == message.author.id and (len(self.players) >= 4 or global_values.debug),
                        "label": "Pas assez de joueurs",
                        "style": 2,
                        "disabled": True
                    }
                ]
            ]
        )

        embed = discord.Embed(
            title="Partie de Codenames | Joueurs (1) :",
            description='\n'.join(["`" + str(x.user) + "`" for x in self.players.values()]),
            color=global_values.color
        )

        await join_message.send(
            message.channel,
            embed
        )

        async def update_join_message(interaction):
            join_message.components[0][1].style = 3 if (len(self.players) >= 4 or global_values.debug) else 2
            join_message.components[0][1].label = "Démarrer" if (len(self.players) >= 4 or global_values.debug) else "Pas assez de joueurs"
            join_message.components[0][1].disabled = False if (len(self.players) >= 4 or global_values.debug) else True

            embed.title = "Partie de Codenames | Joueurs (" + str(len(self.players)) + ") :"
            embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.players.values()])

            await interaction.respond(
                type=7,
                embed=embed,
                components=join_message.components
            )

    async def choose_teams(self, message):
        self.turn = 0

        async def join_team(button, interaction):
            self.players[interaction.user.id].team = button.index

            await update_team_message(interaction)

        async def confirm_teams(buton, interaction):
            await interaction.respond(type=6)
            await team_message.delete()
            await self.choose_spymasters(message)

        def balanced_teams():
            return abs(sum([2 * x.team - 1 for x in self.players.values()])) <= 1

        def missing_players():
            return len([0 for x in self.players.values() if x.team == -1])

        team_message = ComponentMessage(
            [
                [
                    {
                        "effect": join_team,
                        "cond": lambda i: i.user.id in self.players,
                        "label": "Rejoindre l'équipe bleue",
                        "style": 1
                    },
                    {
                        "effect": join_team,
                        "cond": lambda i: i.user.id in self.players,
                        "label": "Rejoindre l'équipe rouge",
                        "style": 4
                    }
                ],
                [
                    {
                        "effect": confirm_teams,
                        "cond": lambda i: i.user.id == message.author.id and balanced_teams() and not missing_players(),
                        "label": "Joueurs sans équipe restants",
                        "style": 2,
                        "disabled": True
                    }
                ]
            ]
        )

        embed = discord.Embed(
            title="Partie de Codenames | Choix des équipes",
            color=global_values.color
        )

        embed.add_field(
            name="🟦 Equipe Bleue",
            value="Personne"
        )

        embed.add_field(
            name="🟥 Equipe Rouge",
            value="Personne"
        )

        await team_message.send(
            message.channel,
            embed
        )

        async def update_team_message(interaction):
            style = 2
            label = "Continuer"
            disabled = True

            if missing_players():
                label = "Joueurs sans équipe restants"
            elif not balanced_teams():
                label = "Equipes déséquilibrées"
            else:
                style = 3
                disabled = False

            team_message.components[1][0].style = style
            team_message.components[1][0].label = label
            team_message.components[1][0].disabled = disabled

            for i in range(2):
                members = ["`" + str(x.user) + "`" for x in self.players.values() if x.team == i]

                embed.set_field_at(
                    i,
                    name=embed.fields[i].name,
                    value='\n'.join(members) if len(members) else "Personne"
                )

            await interaction.respond(
                type=7,
                embed=embed,
                components=team_message.components
            )

    async def choose_spymasters(self, message):
        async def become_spymaster(button, interaction):
            self.spy_masters[button.index] = interaction.user.id

            await update_spymaster_message(interaction)

        async def confirm_spymasters(buton, interaction):
            await interaction.respond(type=6)
            await spymaster_message.delete()
            await self.start_game()

        def missing_spymasters():
            return len([0 for x in self.spy_masters if x == 0])

        spymaster_message = ComponentMessage(
            [
                [
                    {
                        "effect": become_spymaster,
                        "cond": lambda i: i.user.id in self.players and self.players[i.user.id].team == 0,
                        "label": "Devenir Spymaster bleu",
                        "style": 1
                    },
                    {
                        "effect": become_spymaster,
                        "cond": lambda i: i.user.id in self.players and self.players[i.user.id].team == 1,
                        "label": "Devenir Spymaster rouge",
                        "style": 4
                    }
                ],
                [
                    {
                        "effect": confirm_spymasters,
                        "cond": lambda i: i.user.id == message.author.id and not missing_spymasters(),
                        "label": "Joueurs sans équipe restants",
                        "style": 2,
                        "disabled": True
                    }
                ]
            ]
        )

        embed = discord.Embed(
            title="Partie de Codenames | Choix des Spymasters",
            color=global_values.color
        )

        embed.add_field(
            name="🟦 Spymaster Bleu",
            value="Personne"
        )

        embed.add_field(
            name="🟥 Spymaster Rouge",
            value="Personne"
        )

        await spymaster_message.send(
            message.channel,
            embed
        )

        async def update_spymaster_message(interaction):
            style = 2
            label = "Continuer"
            disabled = True

            if missing_spymasters():
                label = "Spymaster manquant"
            else:
                style = 3
                disabled = False

            spymaster_message.components[1][0].style = style
            spymaster_message.components[1][0].label = label
            spymaster_message.components[1][0].disabled = disabled

            for i in range(2):
                embed.set_field_at(
                    i,
                    name=embed.fields[i].name,
                    value="`" + str(self.players[self.spy_masters[i]].user) + "`" if self.spy_masters[i] else "Personne"
                )

            await interaction.respond(
                type=7,
                embed=embed,
                components=spymaster_message.components
            )

    async def start_game(self):
        async def reveal_word(button, interaction):
            word = self.board[button.index]
            word.revealed = True
            button.disabled = True
            button.style = [1, 4, 3, 2][word.color]

            if word.color == 3:
                await self.end_game(False)
            else:
                await self.check_if_win()

            if word.color != self.turn:
                self.turn = 1 - self.turn

            await self.send_info(interaction)


        components = []
        for y in range(5):
            components.append([])
            for x in range(5):
                components[len(components) - 1].append({
                    "effect": reveal_word,
                    "cond": lambda i: i.user.id == self.spy_masters[self.turn],
                    "label": self.board[5 * y + x].word,
                    "style": 2
                })

        self.game_message = ComponentMessage(components, temporary=False)

        await self.game_message.send(
            self.channel,
            discord.Embed(
                title="Partie de Codenames",
                description="Tour du Spymaster `" + str(self.players[self.spy_masters[0]].user) + "`",
                color=0x4444ff
            )
        )

        async def send_spymaster_info(button, interaction):
            comps = []
            for y in range(5):
                comps.append([])
                for x in range(5):
                    word = self.board[5 * y + x]
                    comps[len(comps) - 1].append(
                        Button(
                            label=word.word,
                            style=[1, 4, 3, 2][word.color],
                            disabled=True
                        )
                    )

            await interaction.respond(content="Vraies couleurs des cartes", components=comps)

        async def pass_turn(button, interaction):
            self.turn = 1 - self.turn
            await self.send_info(interaction)

        self.spymaster_message = ComponentMessage(
            [
                [
                    {
                        "effect": send_spymaster_info,
                        "cond": lambda i: i.user.id in self.spy_masters,
                        "label": "Voir les vraies couleurs",
                        "style": 3
                    },
                    {
                        "effect": pass_turn,
                        "cond": lambda i: lambda i: i.user.id == self.spy_masters[self.turn],
                        "label": "Passer le tour",
                        "style": 3
                    }
                ]
            ]
        )

        await self.spymaster_message.send(
            self.channel,
            discord.Embed(
                title="Contrôles pour les Spymasters",
                color=global_values.color
            )
        )

    async def send_info(self, interaction):
        embed = discord.Embed(
            title="Partie de Codenames",
            description="Tour du Spymaster `" + str(self.players[self.spy_masters[self.turn]].user) + "`",
            color=0x4444ff if self.turn == 0 else 0xff4444
        )

        await interaction.respond(type=6)
        await self.game_message.message.edit(embed=embed, components=self.game_message.components)

    async def check_if_win(self):
        card_count = 0
        for word in self.board:
            if word.color == self.turn and not word.revealed:
                card_count += 1

        if card_count == 0:
            await self.end_game(True)

    async def end_game(self, current_win):
        if not current_win:
            self.turn = 1 - self.turn

        embed = discord.Embed(
            title = "Victoire de l'équipe " + ("bleue !" if self.turn == 0 else "rouge !"),
            color = 0x4444ff if self.turn == 0 else 0xff4444
        )

        for row in self.game_message.components:
            for button in row:
                button.style = [1, 4, 3, 2][self.board[button.index].color]

        await self.channel.send(embed=embed)

        await self.game_message.delete(False, True)
        await self.spymaster_message.delete()

        global_values.games.pop(self.channel.id)

 #  Module créé par Le Codex#9836
