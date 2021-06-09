import discord
import asyncio
import random

from modules.codenames.game import Game
from modules.codenames.player import Player
from modules.base import BaseClassPython

import modules.codenames.globals as global_values
global_values.init()

class MainClass(BaseClassPython):
    name = "Codenames"
    help_active = True
    help = {
        "description": "Module du jeu Codenames",
        "commands": {
            "`{prefix}{command} create`": "Rejoint la partie de Codenames. S'il n'y en a pas dans le salon, en crée une nouvelle."
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.color = global_values.color

        self.config["color"] = self.color
        self.config["auth_everyone"] = True
        self.config["help_active"] = True
        self.config["configured"] = True
        self.config["command_text"] = "codenames"

    async def com_create(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            await message.channel.send("Il y a déjà une partie en cours dans le salon")
        else:
            global_values.games[message.channel.id] = Game(message)
            await global_values.games[message.channel.id].create_game(message)

    async def com_reset(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            if game.turn == "none":
                await message.channel.send("La partie a été réinitialisée")
                global_values.games.pop(message.channel.id)
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            global_values.debug = not global_values.debug
            await message.channel.send("Debug: " + str(global_values.debug))
