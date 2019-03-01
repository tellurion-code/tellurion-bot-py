
import discord
import asyncio
class MainClass():
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events=['on_message'] #events list
        self.command="%srtfgd"%self.prefix #command prefix (can be empty to catch every single messages)

        self.name="rtfgd"
        self.description="ceci t'explique pourquoi tu es une merde and rtfgd !"
        self.interactive=True
        self.color=0x7289da
        self.help="""\
 Aucune fonction.
"""
    async def on_message(self, message):
        await message.channel.send(embed=discord.Embed(title="rtfgd", color=self.color).set_image(url="https://cdn.discordapp.com/attachments/326742676672086018/431574829607419914/telecharge_25.jpg"))
