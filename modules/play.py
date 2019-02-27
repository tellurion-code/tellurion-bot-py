import discord
import asyncio
import datetime
import time

class MainClass():
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events=['on_message'] #events list
        self.command="%splay"%prefix #command prefix (can be empty to catch every single messages)

        self.name="Play"
        self.description="Module servant de soundboard"
        self.interactive=True
        self.color=0xc72c48
        self.help="""\
 </prefix>play <nombre>
 => Joue le morceau correspondant au nombre spécifié
 
 </prefix>play list
 => Affiche la liste des morceaux disponibles
"""

    async def on_message(self, message):
        args=message.content.split()
        if len(args) != 2:
            await self.modules['help'][1].send_help(message.channel, self)
        elif args[1] == "list":
            await message.channel.send(message.author.mention + ", ça à l'air de fonctionner, ici.")
        else:
            try:
                number = int(args[1])
            except ValueError:
                await self.modules['help'][1].send_help(message.channel, self)
            else:
                voice = await message.author.voice.channel.connect()
                await message.channel.send(message.author.mention + ", ça à l'air de fonctionner, ici aussi.")
                voice.play(discord.FFmpegPCMAudio("/home/epenser/epenser-bot/soundbox/for-the-damaged-coda.mp3"))
                while voice.is_playing():
                    await asyncio.sleep(1)
                await message.channel.send(message.author.mention + ", ça à l'air de fonctionner, ici aussi. bis")
                if voice.is_connected():
                    await voice.disconnect()
