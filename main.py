#!/usr/bin/python3
import discord
import asyncio
import datetime
import time
from subprocess import call
import os
client = discord.Client(max_messages=100000)
def hasrole(member, roleid):
	for role in member.roles :
		if role.id == roleid :
			return True
	return False
@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name + "#" + client.user.discriminator)
	print(client.user.id)
	print('------')

@client.event
async def on_message(message):
	#//// ARCHIVE MODULE
	
	
	if not (message.author == client.user) :
		randtimev=str(time.time())
		
		if hasrole(message.author, "298516749702266880"): #E-NOBEL
			if str(message.content) == "/archive *" :
				call(['mkdir', '-p', 'tmp/arch/' + randtimev + '/'])
				await client.delete_message(message)
				for chane in client.get_all_channels():
					if chane.server == message.server :
						if str(chane.type) == "text":
							try:
								with open("tmp/arch/" + randtimev + '/' + chane.name + "[" + str(chane.id) + "].txt", "w") as messlog:
									async for rec in client.logs_from(chane, limit=100000) :
										messlog.write("[" + chane.name + "]" +  " " + str(rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')) + " " + rec.author.name + "#" + rec.author.discriminator + "> " + rec.content + "\n")
										messlog.write("	Attachments : " + str(rec.attachments) + "\n\n")
								await client.send_message(message.author, chane.name + " `done.`")
								#await client.send_file(message.author, "tmp/arch/" + chane.name + "[" + str(chane.id) + "]")
							except:
								pass
				call(['bash', '-c', 'zip tmp/arch/' + randtimev + '/' + 'all.zip tmp/arch/' + randtimev + '/' + '*'])
				await client.send_file(message.author, "tmp/arch/" + randtimev + "/" + "all.zip")
		
		
		if hasrole(message.author, "431043517217898496"): #staff
			if str(message.content) == "/archive" :
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
			
			#//// GET DELLOGS
			elif str(message.content) == "/logs" :
				try:
					await client.delete_message(message)
					await client.send_file(message.author, "delLog.txt")
				except:
					await client.send_message(message.author, "```FAILED```")
			#/// RESTART
			elif str(message.content) == "/restart" :
				client.logout()
			elif str(message.content) == "/restart py" :
				await client.send_message(message.channel, message.author.mention() + ", Le module Python va redémarrer..."
				client.logout()




@client.event
async def on_message_delete(message):
	#////DELLOG MODULE
	
	with open("delLog.txt", "a") as dellogfile:
		dellogfile.write(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " [" + message.channel.name + "]" + " " + str(message.timestamp.strftime('%Y-%m-%d %H:%M:%S')) +  " " + message.author.name + "#" + message.author.discriminator + "> " + message.content + "\n")
		dellogfile.write("	Attachments : " + str(message.attachments) + "\n\n")


client.run(os.environ['DISCORD_TOKEN'])
