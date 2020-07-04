import discord
import random

from modules.borderland.reaction_message import ReactionMessage

import modules.borderland.globals as global_values


class Player:
    role = "random"
    symbol = ""
    choice = ""

    def __init__(self, user):
        self.user = user
        self.info_message = None
        self.symbol_choice_message = None

    async def game_start(self, game):
        await self.send_game_start_info()

        self.symbol = random.choice(["❤️", "♠️", "🔷", "🍀"])

        await self.send_choice_message()

    async def send_game_start_info(self):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed=discord.Embed(
            title="Début de partie 🎴",
            description="Vous êtes un random, votre but est d'éliminer le Valet de Coeur.\nUn symbole vous sera assigné à chaque tour, vous avez 24h pour le trouver et le valider sous peine d'être éliminé.\nVous pouvez utiliser `%bl tell <id>` pour envoyer votre symbole à quelqu'un d'autre.",
            color=global_values.color
        ))

    async def send_choice_message(self):
        if self.symbol_choice_message:
            await self.symbol_choice_message.message.delete()
            del self.symbol_choice_message

        choices = ["Coeur", "Pique", "Carreau", "Trèfle"]
        emojis = ["❤️", "♠️", "🔷", "🍀"]

        async def confirm_symbol(reactions):
            embed = self.symbol_choice_message.message.embeds[0]

            embed.description = "Vous avez choisi " + emojis[reactions[self.user.id][0]] + " " + choices[reactions[self.user.id][0]] + "."
            embed.color = 0xfffffe

            await self.symbol_choice_message.message.edit(embed=embed)

            self.choice = emojis[reactions[self.user.id][0]]

        async def cond(reactions):
            return len(reactions[self.user.id]) == 1

        self.symbol_choice_message = ReactionMessage(
            cond,
            confirm_symbol,
            temporary=False
        )

        await self.symbol_choice_message.send(
            self.user,
            "Choisissez le symbole que vous pensez avoir " + (self.symbol if global_values.debug else ""),
            "",
            global_values.color,
            choices,
            emojis=emojis
        )


class Jack(Player):
    role = "jack"

    async def send_game_start_info(self):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed=discord.Embed(
            title="Début de partie 🃏",
            description="Vous êtes le valet de Coeur, votre but est de rester en vie jusqu'à ce qu'il ne reste plus que deux joueurs.\nUn symbole vous sera assigné à chaque tour, vous avez 24h pour le trouver et le valider sous peine d'être éliminé.\nVous pouvez utiliser `%bl tell <id>` pour envoyer votre symbole à quelqu'un d'autre.",
            color=0xfffffe
        ))
