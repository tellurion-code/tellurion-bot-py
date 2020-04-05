import sys
import random
import discord
import asyncio

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Nosferatu"
    help_active = True
    help = {
        "description": "Module du jeu Nosferatu",
        "commands": {
            "`{prefix}{command}`": "Démarre une partie de Nosferatu",
            "`{prefix}{command} join`": "Rejoint une partie de Nosferatu",
            "`{prefix}{command} quit`": "Quitte une partie de Nosferatu",
            "`{prefix}{command} players`": "Affiche les joueurs d'une partie de Nosferatu",
        }
    }
    color = 0xff0000
    command_text = "nosferatu"
    games = {}

    def __init__(self, client):
        super().__init__(client)

    async def command(self, message, args, kwargs):
        if not message.channel.id in self.games:
            embed = discord.Embed(title = "Démarrage de la partie de Nosferatu",
                                description = "Tapez !nosferatu join pour rejoindre la partie",
                                color = self.color)

            await message.channel.send(embed = embed)

            self.games[message.channel.id] = {
                "players": [
                    {
                        "id": message.author.id,
                        "role": ""
                    }
                ],
                "turn": -1
            }
        else:
            await message.channel.send("Il y a déjà une partie en cours")
    #     self._can_delete.add(message.id)

    async def com_start(self, message, args, kwargs):
        if message.channel.id in self.games:
            if self.games[message.channel.id].players.length >= 5:
                await message.channel.send("Début de partie")
            else:
                await message.channel.send("Il faut au minimum 5 joueurs pour commencer la partie")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_join(self, message, args, kwargs):
        if message.channel.id in self.games:
            if self.games[message.channel.id].players.length < 8:
                await message.channel.send("<@" + message.author.id + "> rejoint la partie")
            else:
                await message.channel.send("Il y a déjà le nombre maximum de joueurs (8)")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_players(self, message, args, kwargs):
        if message.channel.id in self.games:
            embed = discord.Embed(
                title = "Liste des joueurs",
                color = self.color,
                description = "```" + ' '.join([self.client.get_user(x["id"]).name for x in self.games[message.channel.id].get("players")]) + "```"
            )
            await message.channel.send(embed = embed)
        else:
            await message.channel.send("Il n'y a pas de partie en cours")
