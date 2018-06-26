import datetime
import time
from subprocess import call

import settings.dellog
import utils.perms

try:
    call(['mkdir', 'tmp'])
except:
    pass

async def log_deleted(client, message):
    with open("tmp/delLog.txt", "a") as dellogfile:
        dellogfile.write(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " [" + str(message.channel.name) + "]" + " " + str(message.timestamp.strftime('%Y-%m-%d %H:%M:%S')) +  " " + message.author.name + "#" + message.author.discriminator + "> " + str(message.content) + "\n")
        dellogfile.write("	Attachments : " + str(message.attachments) + "\n\n")

async def send_logs(client, message):
    if str(message.content) == "/logs" and (not (message.author == client.user)) and await utils.perms.hasrole(message.author, settings.dellog.logsAuth) :
        try:
            try :
                await client.delete_message(message)
            except :
                pass
            await client.send_file(message.author, "tmp/delLog.txt")
        except:
            await client.send_message(message.author, "```FAILED```")
