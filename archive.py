import datetime
import time
from subprocess import call
import settings
async def hasrole(member, roleidlist):
	for role in member.roles :
		for roleid in roleidlist:
			print(roleid + " " + role.id)
			if role.id == roleid :
				return True
	return False

async def everyOfGuild(client, message):
	randtimev=str(time.time())
	if str(message.content) == "/archive *" and (not (message.author == client.user)) and await hasrole(message.author, settings.c_archive.everyOfGuildAuth) :
		call(['mkdir', '-p', 'tmp/arch/' + randtimev + '/'])
		await client.delete_message(message)
		for chane in client.get_all_channels():
			if chane.server == message.server and (str(chane.type) == "text") :
				if str(chane.type) == "text":
					try:
						with open("tmp/arch/" + randtimev + '/' + chane.name + "[" + str(chane.id) + "].txt", "w") as messlog:
							async for rec in client.logs_from(chane, limit=100000) :
								messlog.write("[" + chane.name + "]" +  " " + str(rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')) + " " + rec.author.name + "#" + rec.author.discriminator + "> " + rec.content + "\n")
								messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
						await client.send_message(message.author, chane.name + " `done.`")
					except:
						pass
		call(['bash', '-c', 'zip tmp/arch/' + randtimev + '/' + 'all.zip tmp/arch/' + randtimev + '/' + '*'])
		await client.send_file(message.author, "tmp/arch/" + randtimev + "/" + "all.zip")

async def specific(client, message):
	randtimev=str(time.time())
	if str(message.content) == "/archive" and (not (message.author == client.user)) and await hasrole(message.author, settings.c_archive.specificAuth) :
		call(['mkdir', '-p', 'tmp/arch/' + randtimev + '/'])
		await client.delete_message(message)
		try:
			with open("tmp/arch/" + randtimev + "/" + message.channel.name + "[" + str(message.channel.id) + "].txt", "w") as messlog:
				async for rec in client.logs_from(message.channel, limit=100000) :
					messlog.write("[" + message.channel.name + "]" +  " " + str(rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')) + " " + rec.author.name + "#" + rec.author.discriminator + "> " + rec.content + "\n")
					messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
			
			await client.send_file(message.author, "tmp/arch/" + randtimev + '/' + message.channel.name + "[" + str(message.channel.id) + "].txt")
		except:
			await client.send_message(message.author, "```FAILED```")
