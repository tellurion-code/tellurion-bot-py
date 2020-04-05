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
                ]
            }
        else:
            await message.channel.send("Il y a déjà une partie en cours")
    #     self._can_delete.add(message.id)

    async def com_start():
        if message.channel.id in self.games:
            await message.channel.send("test")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")
