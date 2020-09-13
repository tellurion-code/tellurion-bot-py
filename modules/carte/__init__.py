import random
import discord

from modules.base import BaseClassPython

NUMEROS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "valet", "dame", "roi"]
COULEURS = ["coeur", "pique", "trèfle", "carreau"]

class MainClass(BaseClassPython):
    name = "card"
    help = {
        "description": "Tire une carte",
        "commands": {
            "{prefix}{command}": "Tire une carte"
        }
    }

    def __init__(self, client):
        super().__init__(client)

    async def command(self, message, args, kwargs):
        await message.channel.send("coucou")
        couleur = random.choice(COULEURS)
        numero = random.choice(NUMEROS)
        await message.channel.send(f"Vous avez tiré la carte: {numero} de {couleur}")
