import asyncio

import discord


class MainClass:
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message']  # events list
        self.command = "%splay" % prefix  # command prefix (can be empty to catch every single messages)
        self.voice = None
        self.musics = [
            "for-the-damaged-coda",
            "see-you-again",
            "roundabout-long",
            "roundabout-short",
            'pillar-men-theme',
            'ba-dum-tss'
        ]

        self.name = "Play"
        self.description = "Module servant de soundboard"
        self.interactive = True
        self.authlist = [431043517217898496, 456142467666804746]
        self.color = 0xc72c48
        self.help = """\
 </prefix>play <nombre>
 => Joue le morceau correspondant au nombre spécifié
 
 </prefix>play list
 => Affiche la liste des morceaux disponibles
"""

    async def on_message(self, message):
        args = message.content.split()
        if len(args) != 2:
            await self.modules['help'][1].send_help(message.channel, self)
        elif args[1] == "list":
            await message.channel.send(embed=discord.Embed(title="PLAY - Soundboard", description='\n'.join(
                [str(i) + " : " + name for i, name in enumerate(self.musics)]), color=self.color))
        else:
            try:
                number = int(args[1])
            except ValueError:
                await self.modules['help'][1].send_help(message.channel, self)
            else:
                if number in range(len(self.musics)):
                    if not self.voice:
                        self.voice = True
                        self.voice = await message.author.voice.channel.connect()
                        try:
                            await message.delete()
                        except discord.Forbidden:
                            pass
                        except discord.HTTPException:
                            pass
                        self.voice.play(discord.PCMVolumeTransformer(
                            discord.FFmpegPCMAudio("assets/" + self.musics[number] + ".mp3"), volume=0.1))
                        while self.voice.is_playing():
                            await asyncio.sleep(1)
                        if self.voice and self.voice.is_connected():
                            await self.voice.disconnect()
                            self.voice = None
                else:
                    await message.channel.send(message.author.mention + ", Veuillez préciser un nombre valide.")
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        pass
                    except discord.HTTPException:
                        pass
