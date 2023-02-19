import discord
import random
import math

from modules.codenames.player import Player
from  modules.codenames.views import JoinView, TeamView, SpymasterView, BoardView, ControlsView

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
        self.turn = -1 # Le tour en cours. 0 = bleu, 1 = rouge, -1 = pas commencé (et 2 = "gris", vert en vrai, 3 = "noir", gris en vrai)
        self.board = [] # Liste des mots utilisés pour la partie et leurs couleurs (vraies et révélées)
        self.hint = "" # Dernier indice donné
        self.affected = 0 # Nombre de mots affectés par l'indice

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

    async def create_game(self):
        embed = discord.Embed(
            title="Partie de Codenames | Joueurs (1) :",
            description='\n'.join(["`" + str(x.user) + "`" for x in self.players.values()]),
            color=global_values.color
        )

        await self.channel.send(
            embed=embed,
            view=JoinView(self)
        )

    async def choose_teams(self):
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

        await self.channel.send(
            embed=embed,
            view=TeamView(self)
        )

    async def choose_spymasters(self):
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

        await self.channel.send(
            embed=embed,
            view=SpymasterView(self)
        )

    def get_info_embed(self):
        embed = discord.Embed(
            title="Partie de Codenames | Tour de l'équipe " + ["Bleue", "Rouge"][self.turn],
            color=discord.Color.blue() if self.turn == 0 else discord.Color.brand_red()
        )

        for i in range(2):
            embed.add_field(
                name=["🟦", "🟥"][i] + " Equipe " + ["Bleue", "Rouge"][i],
                value="__Spymaster:__ `" + str(self.players[self.spy_masters[i]].user) + "`\n\n" + '\n'.join(["`" + str(x.user) + "`" for x in self.players.values() if x.team == i])
            )

        return embed

    async def send_game_messages(self):
        embed = self.get_info_embed()
        self.game_view = BoardView(self)
        await self.channel.send(
            embed=embed,
            view=self.game_view
        )

        self.controls_view = ControlsView(self)
        await self.channel.send(
            embed=discord.Embed(
                title="Contrôles pour les Spymasters",
                color=global_values.color
            ),
            view=self.controls_view
        )

    async def send_info(self, interaction):
        embed = self.get_info_embed()
        await interaction.response.defer()
        await self.game_view.message.edit_message(embed=embed, view=self.game_view)

    async def check_if_win(self):
        for word in self.board:
            if word.color == self.turn and not word.revealed:
                return

        await self.end_game()

    async def end_game(self):
        embed = discord.Embed(
            title = "Victoire de l'équipe " + ("bleue !" if self.turn == 0 else "rouge !"),
            value = '\n'.join("`" + str(x.user) + "`" for x in self.game.players.values() if x.team == self.turn),
            color = discord.color.blue() if self.turn == 0 else discord.color.brand_red()
        )
        await self.channel.send(embed=embed)

        await self.game_view.reveal_all_words()
        await self.game_view.freeze()
        await self.controls_view.delete()

        global_values.games.pop(self.channel.id)

 #  Module créé par Le Codex#9836
