import datetime
import time
import settings
from subprocess import call
call(['mkdir', 'tmp'])
async def log_deleted(client, message):
	with open("tmp/delLog.txt", "a") as dellogfile:
		dellogfile.write(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " [" + message.channel.name + "]" + " " + str(message.timestamp.strftime('%Y-%m-%d %H:%M:%S')) +  " " + message.author.name + "#" + message.author.discriminator + "> " + message.content + "\n")
		dellogfile.write("	Attachments : " + str(message.attachments) + "\n\n")
async def send_logs(client, message):
	if str(message.content) == "/logs" :
		try:
			await client.delete_message(message)
			await client.send_file(message.author, "tmp/delLog.txt")
		except:
			await client.send_message(message.author, "```FAILED```")
