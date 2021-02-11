import random
import discord
from modules.base import BaseClassPython

def userstr(user):
	if user:
		return user.name
	else:
		return "None"

class MainClass(BaseClassPython):
	name = "Roll"
	help = {
		"description": "Some random stuff",
		"commands": {
			"{prefix}{command}": "Throws a d6",
			"{prefix}{command} [N]": "Throws a dN",
			"{prefix}{command} vowel [amount]": "Sends a random vowel",
			"{prefix}{command} consonant [amount]": "Sends a random consonant",
			"{prefix}{command} letter [amount]": "Sends a random letter",
			"{prefix}{command} rps|shifumi": "Throws a random Rock-Paper-Scissors symbol"
		}
	}
	games = {}

	def __init__(self, client):
		super().__init__(client)
		self.config["auth_everyone"] = True
		self.config["configured"] = True
		self.config["help_active"] = True
		self.config["command_text"] = "roll"
		self.config["color"] = 0x000000

	async def command(self, message, args, kwargs):
		amount = 6
		if len(args) == 1:
			try:
				amount = int(args[0])
			except:
				await message.channel.send("Un des arguments n'est pas un nombre valide")
				return
		result = random.randint(1, amount)
		embed_description = "🎲 Resultat du lancer : " + str(result)
		await message.channel.send(embed=discord.Embed(description=embed_description, color=self.config.color))

	async def com_vowel(self, message, args, kwargs):
		vowels = "AEIOUY"
		result = []
		amount = 1
		if len(args) > 1:
			try:
				amount = int(args[1])
			except:
				await message.channel.send("Un des arguments n'est pas un nombre valide")
				return
		amount = [100,amount][amount<100]

		for i in range(amount):
			result.append(random.choice(vowels))

		embed_description = "🔠 Resultat du lancer : " + ", ".join(result)
		await message.channel.send(embed=discord.Embed(description=embed_description, color=self.config.color))

	async def com_consonant(self, message, args, kwargs):
		consonants = "BCDFGHJKLMNPQRSTVWXZ"
		result = []
		amount = 1
		if len(args) > 1:
			try:
				amount = int(args[1])
			except:
				await message.channel.send("Un des arguments n'est pas un nombre valide")
				return
		amount = [100,amount][amount<100]

		for i in range(amount):
			result.append(random.choice(consonants))

		embed_description = "🔠 Resultat du lancer : " + ", ".join(result)
		await message.channel.send(embed=discord.Embed(description=embed_description, color=self.config.color))

	async def com_letter(self, message, args, kwargs):
		letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		result = []
		amount = 1
		if len(args) > 1:
			try:
				amount = int(args[1])
			except:
				await message.channel.send("Un des arguments n'est pas un nombre valide")
				return
		amount = [100,amount][amount<100]

		for i in range(amount):
			result.append(random.choice(letters))

		embed_description = "🔠 Resultat du lancer : " + ", ".join(result)
		await message.channel.send(embed=discord.Embed(description=embed_description, color=self.config.color))

	async def com_rps(self, message, args, kwargs):
		choices = [":rock: Rock", "📄 Paper", "✂️ Scissors"]
		embed_description = "✊ Resultat du lancer : " + random.choice(choices)
		await message.channel.send(embed=discord.Embed(description=embed_description, color=self.config.color))

	async def com_shifumi(self, message, args, kwargs):
		self.com_rps(message, args, kwargs)
