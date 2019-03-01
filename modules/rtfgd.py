
import discord
import asyncio
import random
class MainClass():
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events=['on_message'] #events list
        self.command="%srtfgd"%self.prefix #command prefix (can be empty to catch every single messages)

        self.name="rtfgd"
        self.description="Module donnant des indications sur les Google Docs"
        self.interactive=True
        self.color=0x7289da
        self.help="""\
 </prefix>rtfgd [mention]
 => Incite les personnes mentionnées à lire les Google Docs
"""
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
    async def on_message(self, message):
        await message.channel.send(" ".join(member.mention for member in message.mentions), embed=discord.Embed(title="Read da fu**ing GOOGLE DOCS ! (╯°□°）╯︵ ┻━┻", color=self.color).set_image(url=random.choice(self.meme)))
        try:
            await message.delete()
        except:
            pass
