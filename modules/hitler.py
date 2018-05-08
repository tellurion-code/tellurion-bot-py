#Secret Hitler is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License as in http://secrethitler.com/assets/Secret_Hitler_Rules.pdf
import random

import settings.hitler

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
		tmpl = random.shuffle(self.playerlist())
		for i in range(len(tmpl)) :
			if len(tmpl) == 5 or len(tmpl) == 6:
				pass
				self.liberals.append(tmpl[i]
			if len(tmpl) == 7 or len(tmpl) == 8:
				pass
			if len(tmpl) == 9 or len(tmpl) == 10:
				pass
	
