import asyncio
import discord
import datetime
import time
from subprocess import call
import os
moduleFiles="dellog"
class MainClass():
    def __init__(self, client, modules, owners):
        if not os.path.isdir("storage/%s"%moduleFiles):
            call(['mkdir', 'storage/%s'%moduleFiles])
        self.client = client
        self.modules = modules
        self.owners = owners
        self.events=['on_message', 'on_message_delete'] #events list
        self.command="/logs" #command prefix (can be empty to catch every single messages)

        self.name="DelLog"
        self.description="Module de la NSA (log des messages supprimés)"
        self.interactive=True
        self.authlist=[431043517217898496]
        self.color=0x000000
        self.help="""\
 /logs
 => Envoie le journal des messages supprimés en message privé
"""

    async def on_message_delete(self, message):
        with open("storage/%s/delLog.txt"%moduleFiles, "a") as dellogfile:
            if message.channel is discord.TextChannel:
                dellogfile.write(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " [" + str(message.channel.name) + "]" + " " + str(message.created_at.strftime('%Y-%m-%d %H:%M:%S')) +  " " + message.author.name + "#" + message.author.discriminator + "> " + str(message.content) + "\n")
            else:
                dellogfile.write(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " [" + str("_DM_") + "]" + " " + str(message.created_at.strftime('%Y-%m-%d %H:%M:%S')) +  " " + message.author.name + "#" + message.author.discriminator + "> " + str(message.content) + "\n")
            dellogfile.write("	Attachments : " + str(message.attachments) + "\n\n")

    async def on_message(self, message):
        try:
            await message.delete()
        except:
            pass
        with open('storage/%s/delLog.txt'%moduleFiles, 'rb') as dellog:
            await message.author.send(file=discord.File(dellog, filename='delLog.txt'))
