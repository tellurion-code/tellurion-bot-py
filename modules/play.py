import asyncio

import discord

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "play"
    super_users = [431043517217898496]
    color = 0xc72c48
    help_active = True
    help = {
        "description": "Module permettant de jouer des fichier audios",
        "commands": {
            "`{prefix}play list`": "Liste les fichiers disponibles",
            "`{prefix}play <numero>`": "Joue le fichier numéroté",
        }
    }
    command_text = "play"

    def __init__(self, client):
        self.client = client
        self.voice = None
        self.musics = [
            "for-the-damaged-coda",
            "see-you-again",
            "roundabout-long",
            "roundabout-short",
            'pillar-men-theme',
            'ba-dum-tss'
        ]

    async def com_list(self, message, args, kwargs):
        await message.channel.send(embed=discord.Embed(title="PLAY - Soundboard", description='\n'.join(
            [str(i) + " : " + name for i, name in enumerate(self.musics)]), color=self.color))

    async def command(self, message, args, kwargs):
        try:
            number = int(args[0])
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