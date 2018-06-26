import datetime
import time
from subprocess import call

import settings.archive
import utils.perms


async def everyOfGuild(client, message):
    randtimev=str(time.time())
    if str(message.content) == "/archive *" and (not (message.author == client.user)) and await utils.perms.hasrole(message.author, settings.archive.everyOfGuildAuth) :
        call(['mkdir', '-p', 'tmp/arch/' + randtimev + '/'])
        try:
            await client.delete_message(message)
        except:
            pass
        for chane in client.get_all_channels():
            if chane.server == message.server and (str(chane.type) == "text") :
                try:
                    with open("tmp/arch/" + randtimev + '/' + chane.name + "[" + str(chane.id) + "].txt", "w") as messlog:
                        async for rec in client.logs_from(chane, limit=100000) :
                            messlog.write("[" + chane.name + "]" +  " " + str(rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')) + " " + rec.author.name + "#" + rec.author.discriminator + "> " + rec.content + "\n")
                            messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
                    await client.send_message(message.author, chane.name + " `done.`")
                except:
                    pass
        zipname = time.strftime('%Y-%m-%d.%H.%M.%S') + ".zip"
        call(['bash', '-c', 'zip tmp/arch/' + zipname + ' tmp/arch/' + randtimev + '/' + '*'])
        await client.send_file(message.author, "tmp/arch/" + zipname)

async def specific(client, message):
    randtimev=str(time.time())
    if str(message.content) == "/archive" and (not (message.author == client.user)) and await utils.perms.hasrole(message.author, settings.archive.specificAuth) :
        call(['mkdir', '-p', 'tmp/arch/' + randtimev + '/'])
        try :
            await client.delete_message(message)
        except:
            pass
        try:
            with open("tmp/arch/" + randtimev + "/" + message.channel.name + "[" + str(message.channel.id) + "].txt", "w") as messlog:
                async for rec in client.logs_from(message.channel, limit=100000) :
                    messlog.write("[" + message.channel.name + "]" +  " " + str(rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')) + " " + rec.author.name + "#" + rec.author.discriminator + "> " + rec.content + "\n")
                    messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
            
            await client.send_file(message.author, "tmp/arch/" + randtimev + '/' + message.channel.name + "[" + str(message.channel.id) + "].txt")
        except:
            await client.send_message(message.author, "```FAILED```")
            raise
