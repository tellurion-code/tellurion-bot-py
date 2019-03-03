import random

import discord

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "Read the fucking google doc"
    super_users = [431043517217898496]
    color = 0x7289da
    help_active = True
    help = {
        "description": "Module donnant les indications sur les googles docs (ou juste quand vous avez envie de crier sur"
                       " quelqu'un)",
        "commands": {
            "`{prefix}rtfgd <mention>`": "Essaye, tu verras"
        }
    }
    command_text = "rtfgd"

    def __init__(self, client):
        super().__init__(client)
        self.meme = [
            "https://i.imgflip.com/27tjun.gif",
            "https://cdn.discordapp.com/attachments/326742676672086018/431574829607419914/telecharge_25.jpg",
            "https://cdn.discordapp.com/attachments/326742676672086018/431575352381538304/telecharge_26.jpg",
            "https://cdn.discordapp.com/attachments/326742676672086018/431574292904280064/unknown.png",
            "https://cdn.discordapp.com/attachments/326742676672086018/431573317539856394/image-1.png",
            "https://cdn.discordapp.com/attachments/326742676672086018/431572693910028289/telecharge_19.jpg",
            "https://cdn.discordapp.com/attachments/326742676672086018/431572366951448588/telecharge_18.jpg",
            "https://cdn.discordapp.com/attachments/326742676672086018/431569158170345472/telecharge_11.jpg"
        ]

    async def command(self, message, args, kwargs):
        await message.channel.send(
            " ".join(member.mention for member in message.mentions),
            embed=discord.Embed(title="Read da fu**ing GOOGLE DOCS ! (╯°□°）╯︵ ┻━┻",
                                color=self.color).set_image(url=random.choice(self.meme)))
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass
