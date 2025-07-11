import random

import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "radion"
    help = {
        "description": "Prévenir Radion des nombres premiers"
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"channel": 0,
                          "user": 0})

    def estPremier(self, n):
        for i in range(2, int(n**.5) + 1):
            if n % i == 0:
                return False
        return n > 1

    async def on_message(self, message):
        if message.channel.id == 431016132040851459:
            try:
                if self.estPremier(int(message.content[:10])):
                    await message.reply(f"Regarde, c'est un nombre premier <@&544845665910390784> !")
            except ValueError:
                pass
            except TypeError:
                pass
