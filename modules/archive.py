import time
from subprocess import call

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
            "`{prefix}archive`": "Archive le salon courant",
            "`{prefix}archive *`": "Archive tous les salons du serveurs",
        }
    }
    command_text = "archive"

    async def on_message(self, message):
        current_time = str(time.time())
        args = message.content.split()

        if len(args) > 1 and args[1] == '*':
            if not await self.auth(message.author, [522918472548745217]):
                await message.channel.send("Vous n'avez pas les permissions pour effectuer une sauvegarde complète.")
                return
            # Archive server
            try:
                await message.delete()
            except:
                pass
            call(['mkdir', '-p', 'storage/%s/' % moduleFiles + current_time + '/'])
            for chan in message.channel.guild.channels:
                try:
                    with open(
                            'storage/%s/' % moduleFiles + current_time + '/' + chan.name + "[" + str(chan.id) + "].txt",
                            "w") as messlog:
                        async for rec in chan.history(limit=None):
                            messlog.write("[" + chan.name + "]" + " " + str(
                                rec.created_at.strftime('%Y-%m-%d %H:%M:%S')) + " " + str(
                                rec.author) + "> " + rec.content + "\n")
                            messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
                    await message.author.send(chan.name + " `done.`")
                except:
                    pass
            zip_name = time.strftime('%Y-%m-%d.%H.%M.%S') + ".zip"
            call(['bash', '-c',
                  'zip storage/%s/' % moduleFiles + zip_name + ' storage/%s/' % moduleFiles + current_time + '/' + '*'])
            with open('storage/%s/' % moduleFiles + zip_name, 'rb') as messlogzip:
                await message.author.send(file=discord.File(messlogzip, filename=zip_name))

        elif len(args) == 1:
            # Archive channel
            try:
                await message.delete()
            except:
                pass
            call(['mkdir', '-p', 'storage/%s/' % moduleFiles + current_time + '/'])
            try:
                with open('storage/%s/' % moduleFiles + current_time + '/' + message.channel.name + "[" +
                          str(message.channel.id) + "].txt", "w") as messlog:
                    async for rec in message.channel.history(limit=None):
                        messlog.write("[" + message.channel.name + "]" + " " + str(
                            rec.created_at.strftime('%Y-%m-%d %H:%M:%S')) + " " + str(
                            rec.author) + "> " + rec.content + "\n")
                        messlog.write("	Attachments : " + ' ;; '.join(
                            [str(i.url + ", " + i.proxy_url) for i in rec.attachments]) + "\n\n")
                with open('storage/%s/' % moduleFiles + current_time + '/' + message.channel.name + "[" +
                          str(message.channel.id) + "].txt", "rb") as messlog:
                    await message.author.send(
                        file=discord.File(messlog,
                                          filename=message.channel.name + "[" + str(message.channel.id) + "].txt")
                    )
            except:
                await message.author.send("```FAILED```")
                raise

        else:
            await self.modules['help'][1].send_help(message.channel, self)
