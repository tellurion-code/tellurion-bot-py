#Secret Hitler is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License as in http://secrethitler.com/assets/Secret_Hitler_Rules.pdf
import settings.hitler

async def commandHandler(client, message, hitlerGame):
	if message.content == "/game join secret-hitler":
		await hitlerGame.AddPlayer(client, message)
	elif message.content == "/game start secret-hitler":
		await hitlerGame.StartGame(client, message)

class HitlerSave :
	def __init__(self):
		self.playerlist=[]
		self.started=False
	
	async def strUsers(self):
		retlist="Joueurs [secret-hitler] :\n\n"
		for member in self.playerlist:
			retlist += (member.name + '#' + member.discriminator + '\n')
		return retlist
	
	async def AddPlayer(self, client, message):
		if not self.started :
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
