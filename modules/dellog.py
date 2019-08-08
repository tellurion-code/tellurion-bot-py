import datetime
import time

import discord

from modules.base import BaseClass

moduleFiles = "dellog"


class MainClass(BaseClass):
    name = "Dellog"
    command_text = "logs"
    help_active = True
    help = {
        "description": "Module de la NSA (log des messages supprimés)",
        "commands": {
            "`{prefix}{command}`": "Envoie le journal des messages supprimés en message privé",
        }
    }
    authorized_roles = [431043517217898496]

    async def on_message_delete(self, message):
        with self.storage.open("delLog.txt", "a") as dellogfile:
            if type(message.channel) is discord.TextChannel:
                dellogfile.write(
                    str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) +
                    " [" + str(message.channel.name) + "] " +
                    str(message.created_at.strftime('%Y-%m-%d %H:%M:%S')) + " " +
                    message.author.name +
                    "#" + message.author.discriminator + "> " +
                    str(message.content) + "\n")
            else:
                dellogfile.write(
                    str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
                    + " [" + str("_DM_") + "] " +
                    str(message.created_at.strftime('%Y-%m-%d %H:%M:%S')) + " " +
                    message.author.name +
                    "#" + message.author.discriminator + "> " +
                    str(message.content) + "\n")
            dellogfile.write("	Attachments : " +
                             ' ;; '.join([str(i.url + ", " + i.proxy_url) for i in message.attachments]) +
                             "\n\n")

    async def command(self, message, args, kwargs):
        try:
            await message.delete()
        except:
            pass
        with self.storage.open("delLog.txt", 'rb') as dellog:
            await message.author.send(file=discord.File(dellog, filename='delLog.txt'))
