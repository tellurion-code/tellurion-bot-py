import random

import discord

from modules.game.views import GameView

class Player:
    def __init__(self, game, user):
        self.game = game
        self.user = user

class JoinView(GameView):
    @discord.ui.button(label="Rejoindre ou quitter", style=discord.ButtonStyle.blurple)
    async def join_or_leave(self, button, interaction):
        if interaction.user.id not in self.game.players:
            self.game.players[interaction.user.id] = Player(self, interaction.user)
        else:
            del self.game.players[interaction.user.id]

        await self.update_join_message(interaction)

    @discord.ui.button(label="Pas assez de rôles", disabled=True, style=discord.ButtonStyle.gray)
    async def start(self, button, interaction):
        await interaction.response.defer()

        if interaction.user.id in self.game.players:
            await self.game.start_game()
            await self.delete()

    def enough_players(self):
        if len(self.game.roles) < len(self.game.players):
            return {
                "bool": False,
                "reason": "Pas assez de rôles"
            }

        return {
            "bool": True,
            "reason": "Démarrer"
        }

    async def update_join_message(self, interaction=None):
        condition = self.enough_players()

        self.children[1].style = discord.ButtonStyle.green if condition["bool"] else discord.ButtonStyle.gray
        self.children[1].label = condition["reason"]
        self.children[1].disabled = not condition["bool"]

        embed = self.message.embeds[0]
        embed.title = "Partie | Joueurs (" + str(len(self.game.players)) + ") :"
        embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.game.players.values()])

        if interaction:
            await interaction.response.edit_message(
                embed=embed,
                view=self
            )
        else:
            await self.message.edit(
                embed=embed,
                view=self
            )

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

        self.roles = []  # Rôles

    async def on_creation(self):
        embed = discord.Embed(
            title="Partie | Joueurs (1) :",
            description='\n'.join(["`" + str(x.user) + "`" for x in self.players.values()]),
            color=self.mainclass.color
        )

        self.view = JoinView(self)
        await self.channel.send(
            embed=embed,
            view=self.view
        )

    async def start_game(self):
        embed = discord.Embed(
            title="Partie démarrée",
            color=self.mainclass.color
        )
        embed.add_field(name = "Joueur.ses", value = '\n'.join(["`" + str(x.user) + "`" for x in self.players.values()]), inline = True)
        embed.add_field(name = "Rôles", value = '\n'.join(["`" + x + "`" for x in self.roles]), inline = True)
        await self.channel.send(embed=embed)

        random.shuffle(self.roles)
        for player in self.players.values():
            await player.user.send(f"Tu es `{self.roles.pop()}`")

        del self.mainclass.games[self.channel.id]
