import discord

from modules.base import BaseClassPython

QUEUE = [];

class MainClass(BaseClassPython):
	name = "queue"
	help = {
		"description": "Gère une queue",
		"commands": {
			"{prefix}{command}": "Envoie la liste",
			"{prefix}{command} add": "S'ajouter à la liste",
			"{prefix}{command} remove": "S'enlever de la liste",
			"{prefix}{command} next": "Ping le suivant dans la liste",
		}
	}

	def __init__(self, client):
		super().__init__(client)
		self.config["auth_everyone"] = True
		self.config["configured"] = True


	async def command(self, message, args, kwargs):
		if len(QUEUE) == 0:
			await message.channel.send("Queue vide")
			return

		await message.channel.send(embed=discord.Embed(
			description='\n'.join([str(x) for x in QUEUE])
		))

	async def com_add(self, message, args, kwargs):
		QUEUE.append(message.author)

		await message.channel.send(embed=discord.Embed(
			description='\n'.join([str(x) for x in QUEUE])
		))

	async def com_remove(self, message, args, kwargs):
		QUEUE.remove(message.author)

		if len(QUEUE) == 0:
			await message.channel.send("Queue vide")
			return

		await message.channel.send(embed=discord.Embed(
			description='\n'.join([str(x) for x in QUEUE])
		))

	async def com_next(self, message, args, kwargs):
		if len(QUEUE) == 0:
			await message.channel.send("Queue vide")
			return


		next = QUEUE.pop(0)

		await message.channel.send(next.mention)
