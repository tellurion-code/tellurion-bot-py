import random
import discord
import re
from modules.base import BaseClassPython

class MainClass(BaseClassPython):
	name = "1KBWC"
	help = {
		"description": "Gère une partie de 1KBWC",
		"commands": {
			"{prefix}{command} draw": "Tire une carte",
			"{prefix}{command} list": "Envoie la liste de toutes les cartes, et des cartes défaussées",
			"{prefix}{command} edit <index>": "Modifie la carte à cet index"
		}
	}
	games = {}

	def __init__(self, client):
		super().__init__(client)
		self.config["auth_everyone"] = True
		self.config["configured"] = True
		self.config["help_active"] = True
		self.config["command_text"] = "tbwc"
		self.config["color"] = 0xeeeeee

	async def on_ready(self):
		if self.objects.save_exists("games"):
			self.games = self.objects.load_object("games")

	async def com_draw(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			index = game["deck"].pop(0)
			msg = None

			if not game["list"][index]:
				msg = await message.channel.send("```md\n [Carte Blanche] Envoyez un message pour définir la carte en tapant \"[Nom de la carte](Type): Effet\"! (Type) accepte Aura, Terrain ou Ephémère.```")
				await self.startCardCreation(message.author, message.channel, index)
				# await message.channel.send("Carte définie")

			card = game["list"][index]
			if msg:
				await msg.edit(content="```md\n" + self.printCard(card) + "```")
			else:
				await message.channel.send("```md\n" + self.printCard(card) + "```")

			game["discard"].append(index)

			if len(game["deck"]) <= len(game["list"])/5:
				random.shuffle(game["discard"])
				game["deck"].extend(game["discard"])
				game["discard"].clear()

				await message.channel.send("```http\nLe deck est trop petit! La défausse a été mélangée pour reformer un nouveau deck```")

			self.objects.save_object("games", self.games)
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_list(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			# await message.channel.send("Listes des cartes:")
			await self.sendCardList(message.channel)
			await self.sendBigMessage("Défausse\n========\n" + '\n'.join([self.printCard(game["list"][e]) if game["list"][e] else "[En attente de défintion...](?)" for e in game["discard"]]), message.channel)
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_start(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			await message.channel.send("Il y a déjà une partie en cours dans ce salon")
		else:
			if len(args) > 1:
				try:
					amount = int(args[1])
					game = {
						"deck": [i for i in range(amount)],
						"discard": [],
						"list": [None for i in range(amount)]
					}

					random.shuffle(game["deck"])

					self.games[str(message.channel.id)] = game
					await message.channel.send("Partie créée")

					self.objects.save_object("games", self.games)
				except:
					await message.channel.send("Veuillez renseigner le nombre de cartes dans le deck")
			else:
				await message.channel.send("Veuillez renseigner le nombre de cartes dans le deck")

	async def com_edit(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			if len(args) > 1:
				try:
					index = int(args[1])

					if index < 1 or index > len(game["list"]):
						await message.channel.send("Aucune carte n'a cet index")
					else:
						await message.channel.send("Définissez la carte en tapant \"[Nom de la carte](Type): Effet\". (Type) accepte Aura, Terrain ou Ephémère.")
						await self.startCardCreation(message.author, message.channel, index - 1)
						# await message.channel.send("Carte éditée")
						await self.sendCardList(message.channel)

					self.objects.save_object("games", self.games)
				except:
					await message.channel.send("Veuillez renseigner l'index de la carte à modifier")
			else:
				await message.channel.send("Veuillez renseigner l'index de la carte à modifier")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_end(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			await self.sendCardList(message.channel)
			del self.games[str(message.channel.id)]
			await message.channel.send("Partie finie!")

			self.objects.save_object("games", self.games)
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def sendBigMessage(self, message, channel):
		sentences = message.split("\n")
		form = ""

		for sentence in sentences:
			if (len(form) + len(sentence) > 2000):
				await channel.send("```md\n" + form + "```")
				form = ""

			form += sentence + "\n"

		await channel.send("```md\n" + form + "```")

	async def sendCardList(self, channel):
		game = self.games[str(channel.id)]
		await self.sendBigMessage("Liste des cartes en jeu\n=======================\n" + '\n'.join([str(i + 1).rjust(3, ' ') + ". " + (self.printCard(e) if e else "[Carte Blanche]") for i, e in enumerate(game["list"])]), channel)

	async def startCardCreation(self, author, channel, index):
		regex = r"^\[(.+)\]\((Aura|Terrain|Ephémère)\) (.+)$"

		def check(m):
			return m.author == author and m.channel == channel and re.search(regex, m.content)

		msg = await self.client.wait_for('message', check=check)
		await msg.delete()

		match = re.match(regex, msg.content)

		card = {
		"name": match.groups()[0],
		"type": match.groups()[1],
		"effect": match.groups()[2]
		}
		self.games[str(channel.id)]["list"][index] = card

	def printCard(self, card):
		return " [" + card["name"] +"](" + card["type"] + ") " + card["effect"]
