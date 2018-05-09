#Secret Hitler is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License as in http://secrethitler.com/assets/Secret_Hitler_Rules.pdf
import random

import settings.hitler
import utils.usertools
async def commandHandler(client, message, hitlerGame):
	if message.content == "/game join hitler":
		await hitlerGame.AddPlayer(client, message)
	elif message.content == "/game start hitler":
		await hitlerGame.StartGame(client, message)
	elif message.content == "/game players hitler":
		await client.send_message(message.channel,"```PYTHON\n{0}\n```".format(await hitlerGame.strUsers()))
	
	if settings.hitler.debug :
		if message.content == "/hitler distribute" :
			await hitlerGame.Distribute()
		if message.content.startswith("/hitler add"):
			args = message.content.split(" ")
			if len(args) == 3 :
				if await utils.usertools.UserByName(client, args[2]) is not False :
					hitlerGame.playerlist.append(await utils.usertools.UserByName(client, args[2]))
				else :
					await client.send_message(message.channel, message.author.mention + ", member not found.")
			else :
				await client.send_message(message.channel, message.author.mention + ", usage: `/hitler add <username>`")

class HitlerSave :
	def __init__(self):
		self.playerlist=[]
		self.started=False
		self.fascists=[]
		self.liberals=[]
	
	async def strUsers(self):
		retlist="Joueurs [secret-hitler] :\n\n"
		for member in self.playerlist:
			retlist += (member.name + '#' + member.discriminator + '\n')
		return retlist
	
	async def AddPlayer(self, client, message):
		if not self.started :
			if len(self.playerlist) >= 10 :
				await client.send_message(message.channel, message.author.mention + ", la partie est pleine. Vous ne pouvez pas rejoindre.")
			else :
				self.playerlist.append(message.author)
				await client.send_message(message.channel,"```PYTHON\n{0}\n```".format(await self.strUsers()))
		else :
			await client.send_message(message.channel, message.author.mention + ", Vous ne pouvez pas rejoindre une partie en cours.")
		pass
	
	async def StartGame(self, client, message):
		if not self.started :
			if len(self.playerlist) >= 5 and len(self.playerlist) <= 10 :
				self.started = True
			else :
				await client.send_message(message.channel, message.author.mention + ", secret-hitler se joue de 5 à 10 joueurs")
		else :
			await client.send_message(message.channel, message.author.mention + ", La partie a déjà commencé.")

	async def Distribute(self):
		self.fascists=[]
		self.liberals=[]
		tmpl = random.sample(self.playerlist, len(self.playerlist))
		for i in range(len(tmpl)) :
			if len(tmpl) == 5 or len(tmpl) == 6:
				if i < 2 :
					self.fascists.append(tmpl[i])
				else:
					self.liberals.append(tmpl[i])
			if len(tmpl) == 7 or len(tmpl) == 8:
				if i < 3 :
					self.fascists.append(tmpl[i])
				else:
					self.liberals.append(tmpl[i])
			if len(tmpl) == 9 or len(tmpl) == 10:
				if i < 4 :
					self.fascists.append(tmpl[i])
				else:
					self.liberals.append(tmpl[i])
			print("fascists : " + str(len(self.fascists)))
			print("liberals : " + str(len(self.liberals)))
	
