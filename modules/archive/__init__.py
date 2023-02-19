import os
import time
import zipfile
from types import GeneratorType

import discord

from modules.base import BaseClassPython


class Storage:
    def __init__(self, base_path, client):
        self.client = client
        self.base_path = base_path
        try:
            os.makedirs(base_path)
        except FileExistsError:
            self.client.info(f"Le dossier {self.base_path} a déjà été créé")

    def mkdir(self, directory):
        try:
            os.makedirs(self.path(directory))
        except FileExistsError:
            self.client.info(f"Le dossier {directory} a déjà été créé")

    def mkzip(self, files, name):
        with zipfile.ZipFile(self.path(name), 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                zip_file.write(self.path(file), compress_type=zipfile.ZIP_DEFLATED)
        return name

    def open(self, filename, *args, **kwargs):
        return open(self.path(filename), *args, **kwargs)

    def path(self, filename):
        return os.path.join(self.base_path, filename)

    def exists(self, filename):
        return os.path.exists(self.path(filename))


class MainClass(BaseClassPython):
    name = "Archive"
    color = 0x137584
    help_active = True
    authorized_roles = [430777457898029057]
    help = {
        "description": "Module permettant d'archiver des salons",
        "commands": {
            "`{prefix}{command}`": "Archive le salon courant",
            "`{prefix}{command} *`": "Archive tous les salons du serveurs",
        }
    }
    command_text = "archive"

    def __init__(self, client):
        super().__init__(client)
        self.storage = Storage(os.path.join("data", self.name.lower(), client))

    async def command(self, message, args, kwargs):
        if len(args) and args[0] == "*":
            try:
                await message.delete()
            except discord.Forbidden:
                self.client.warning("Impossible de supprimer le message {message.id}, permission "
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
        return os.path.join(str(current_time), channel.name + " [" + str(channel.id) + "]" + ".txt")
