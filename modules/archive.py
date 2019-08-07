import io
import os
import time
from types import GeneratorType

import discord

from modules.base import BaseClass

moduleFiles = "archive"


class MainClass(BaseClass):
    name = "Archive"
    color = 0x137584
    help_active = True
    help = {
        "description": "Module permettant d'archiver des salons",
        "commands": {
            "`{prefix}{command}`": "Archive le salon courant",
            "`{prefix}{command} *`": "Archive tous les salons du serveurs",
        }
    }
    command_text = "archive"

    async def command(self, message, args, kwargs):
        if len(args) and args[0] == "*":
            if not await self.auth(message.author, [522918472548745217, ]):
                await message.channel.send("Vous n'avez pas les permossions pour effectuer une sauvegarde complète des "
                                           "salons")
                return
            try:
                await message.delete()
            except discord.Forbidden:
                self.client.warning("Impossible de supprimer le message {message.id}, permissions "
                                    "refusée.".format(message=message))
            except discord.HTTPException:
                self.client.warning("Impossible de supprimer le message {message.id}.".format(message=message))
            current_time = time.time()
            files = await self.save_channel(current_time=current_time)
            zip_file_path = self.storage.mkzip(files, str(current_time)+".zip")
            with self.storage.open(zip_file_path, "rb") as zip_file:
                await message.author.send(file=discord.File(zip_file, filename=str(zip_file_path.encode('UTF-8'))))
        else:
            file_path = await self.save_channel(message.channel)
            with self.storage.open(file_path, "rb") as file:
                await message.author.send(file=discord.File(file, filename=str(file_path.encode('UTF-8'))))

    async def save_channel(self, channel=None, current_time=time.time()):
        if channel is None:
            channel = []
            for guild in self.client.guilds:
                for chan in guild.channels:
                    channel.append(chan)
        if type(channel) == GeneratorType or type(channel) == list:
            files = []
            for chan in channel:
                files.append(await self.save_channel(chan, current_time))
            return files
        self.storage.mkdir(str(current_time))
        with self.storage.open(os.path.join(str(current_time), channel.name + " [" + str(channel.id) + "]" + ".txt"), "bw") as file:
            if type(channel) is discord.TextChannel:
                try:
                    async for rec in channel.history(limit=None):
                        file.write(b"[" + bytes(rec.created_at.strftime('%d-%m-%Y %H:%M:%S'), "utf8") + b"] " +
                                bytes(str(rec.author), "utf8") +
                                b">>>\n")
                        file.write(b"    Content: \n")
                        for line in rec.content.split("\n"):
                            file.write(b"             " + line.encode('UTF-8') + b"\n")
                        file.write(b"	Attachments: \n")
                        for attachment in rec.attachments:
                            file.write(b"              - " + bytes(attachment.url, "utf8") + b", " +
                                    bytes(attachment.proxy_url, "utf8") + b"\n")
                except discord.Forbidden:
                    file.write(b"Forbidden")
        return os.path.join(str(current_time), str(channel.id) + ".txt")
