import asyncio

import discord

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "play"
    color = 0xc72c48
    help_active = True
    help = {
        "description": "Module permettant de jouer des fichier audios",
        "commands": {
            "`{prefix}{command} list`": "Liste les fichiers disponibles",
            "`{prefix}{command} <numero>`": "Joue le fichier numéroté",
        }
    }
    command_text = "play"

    def __init__(self, client):
        self.client = client
        self.musics = [
            "for-the-damaged-coda",
            "see-you-again",
            "roundabout-long",
            "roundabout-short",
            'pillar-men-theme',
            'ba-dum-tss',
            'zelda-secret',
            'motus-boule-noire',
            'run',
            'tu-peux-rep'
        ]
        self.voice = None
        self.playing = False
        self.stop = False

    async def com_stop(self, messag, args, kwargs):
        self.stop = True

    async def com_list(self, message, args, kwargs):
        await message.channel.send(embed=discord.Embed(title="PLAY - Soundboard", description='\n'.join(
            [str(i) + " : " + name for i, name in enumerate(self.musics)]), color=self.color))

    async def command(self, message, args, kwargs):
        if len(args) == 0:
            await self.com_list(message, args, kwargs)
            return
        try:
            number = int(args[0])
        except ValueError:
            await message.channel.send("Vous devez rentrer un nombre valide")
        else:
            if number in range(len(self.musics)):
                if self.stop:
                    self.stop = False
                while self.playing:
                    if self.stop:
                        return
                    await asyncio.sleep(1)
                if not self.playing:
                    self.playing = True
                    if message.author.voice is None:
                        await message.channel.send(message.author.mention + ", Vous devez être dans un salon vocal")
                        self.playing = False
                        return
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
                    self.playing = False
            else:
                await message.channel.send(message.author.mention + ", Veuillez préciser un nombre valide.")
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass
