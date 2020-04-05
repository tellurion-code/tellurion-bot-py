import random

import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "rtfgd"
    help = {
        "description": "Read the fucking google doc",
        "commands": {
            "{prefix}{command} <mention>": "Demande gentilment de lire le google doc"
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"memes": []})

    async def command(self, message, args, kwargs):
        await message.channel.send(
            " ".join(member.mention for member in message.mentions),
            embed=discord.Embed(title="Read da fu**ing GOOGLE DOCS ! (╯°□°）╯︵ ┻━┻",
                                color=self.config.color).set_image(url=random.choice(self.config.memes)))
