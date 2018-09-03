import discord
import asyncio
import datetime
import time
import traceback
from subprocess import call

moduleFiles="archive"
class MainClass():
    def __init__(self, client, modules, owners):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.events=['on_message'] #events list
        self.command="/archive" #command prefix (can be empty to catch every single messages)

        self.name="Archive"
        self.description="Module gérant l'archivage des messages"
        self.interactive=True
        self.authlist=[431043517217898496]
        self.color=0x137584
        self.help="""\
 /archive
 => Archive le salon dans lequel la commande a été éffectuée
 
 /archive *
 => Archive tous les salons du serveur dans lequel la commande a été effectuée
"""
    async def on_message(self, message):
        randtimev=str(time.time())
        args=message.content.split()

        if len(args)>1 and args[1]=='*':
            #Archive server
            try:
                await message.delete()
            except:
                pass
            call(['mkdir', '-p', 'storage/%s/'%moduleFiles + randtimev + '/'])
            for chan in message.channel.guild.channels:
                try:
                    with open('storage/%s/'%moduleFiles + randtimev + '/' + chan.name + "[" + str(chan.id) + "].txt", "w") as messlog:
                        async for rec in chan.history():
                            messlog.write("[" + chan.name + "]" +  " " + str(rec.created_at.strftime('%Y-%m-%d %H:%M:%S')) + " " + str(rec.author) + "> " + rec.content + "\n")
                            messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
                    await message.author.send(chan.name + " `done.`")
                except:
                    pass
            zipname = time.strftime('%Y-%m-%d.%H.%M.%S') + ".zip"
            call(['bash', '-c', 'zip storage/%s/'%moduleFiles + zipname + ' storage/%s/'%moduleFiles + randtimev + '/' + '*'])
            with open('storage/%s/'%moduleFiles + zipname, 'rb') as messlogzip:
                await message.author.send(file=discord.File(messlogzip, filename=zipname))

        elif len(args)==1:
            #Archive channel
            try:
                await message.delete()
            except:
                pass
            call(['mkdir', '-p', 'storage/%s/'%moduleFiles + randtimev + '/'])
            try:
                with open('storage/%s/'%moduleFiles + randtimev + '/' + message.channel.name + "[" + str(message.channel.id) + "].txt", "w") as messlog:
                    async for rec in message.channel.history():
                        messlog.write("[" + message.channel.name + "]" +  " " + str(rec.created_at.strftime('%Y-%m-%d %H:%M:%S')) + " " + str(rec.author) + "> " + rec.content + "\n")
                        messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
                with open('storage/%s/'%moduleFiles + randtimev + '/' + message.channel.name + "[" + str(message.channel.id) + "].txt", "rb") as messlog:
                    await message.author.send(file=discord.File(messlog, filename=message.channel.name + "[" + str(message.channel.id) + "].txt"))
            except:
                await message.author.send("```FAILED```")
                raise

        else:
            await self.modules['help'][1].send_help(message.channel, self)
