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
			"{prefix}{command} list": "Envoie la liste de toutes les cartes",
			"{prefix}{command} history <index>": "Envoie l'historique des versions de la carte à cet index",
			"{prefix}{command} show <index de zone>": "Envoie le récap, ou la liste des cartes dans la zone à l'index précisé",
			"{prefix}{command} edit <index>": "Modifie la carte à cet index",
			"{prefix}{command} burn <index>": "Brûle la carte à cet index",
			"{prefix}{command} discard <un ou plus index>": "Défausse la ou les carte(s) avec ces index",
			"{prefix}{command} move <un ou plus index> <index de zone>": "Déplace la ou les carte(s) avec ces index vers la zone indiquée",
			"{prefix}{command} shuffle <un ou plus index>": "Renvoie la ou les carte(s) avec ces index dans le paquet et le mélange." # \nSi `top` est utilisé, les cartes seront placées d'autant de cartes depuis le haut du paquet, et ce dernier ne sera pas mélangé"
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

			# for game in self.games.values():
			# 	for location in game["zones"]:
			# 		if location not in ["deck", "discard", "center"]:
			# 			try:
			# 				await self.client.fetch_user(int(location))
			# 			except:
			# 				pass

	async def com_draw(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]

			if len(game["zones"]["deck"]) <= len(game["zones"]["discard"]) and len(game["zones"]["discard"]):
				game["zones"]["deck"].extend(game["zones"]["discard"])
				game["zones"]["discard"].clear()
				random.shuffle(game["zones"]["deck"])

				await message.channel.send("```http\nLe deck est trop petit! La défausse a été mélangée pour reformer un nouveau deck```")
			elif not len(game["zones"]["discard"]) and not len(game["zones"]["deck"]):
				await message.channel.send("Le deck et la défausse sont vides!")
				await self.endGame(message.channel)
				return

			index = game["zones"]["deck"].pop(0)
			msg = None

			if not game["list"][index] or not game["list"][index]["name"]:
				msg = await message.channel.send("```ini\n" + str(index + 1) + ". (Carte Blanche) Envoyez un message pour définir cette carte en tapant \"[Nom de la carte] Effet\"!```")
				await self.startCardCreation(message.author, message.channel, index)
				# await message.channel.send("Carte définie")

			card = game["list"][index]
			content = "```ini\n" + str(index + 1) + ". " + (await self.printCard(card)) + "```"
			if msg:
				await msg.edit(content=content)
			else:
				await message.channel.send(content)

			if str(message.author.id) not in game["zones"]:
				game["zones"][str(message.author.id)] = []

			msg = await message.channel.send(await self.getRecap(game, "⚠ **Envoyez l'index de la zone où vous voulez jouer la carte** ⚠️"))
			zone = await self.waitForZone(message.author, message.channel)
			game["zones"][zone].append(index)

			await msg.edit(content=await self.getRecap(game))

			self.objects.save_object("games", self.games)
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_discard(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			success = False

			args.pop(0)
			if len(args):
				for arg in args:
					try:
						index = int(arg) - 1
					except:
						await message.channel.send("Index invalide : " + arg)
						return

					if index < 0 or index >= len(game["list"]):
						await message.channel.send("Aucune carte n'a l'index " + index)
					else:
						location = [x for x in game["zones"] if index in game["zones"][x]][0]
						if location == "discard":
							await message.channel.send("Cette carte est déjà dans la défausse")
						else:
							self.moveCards(game, [index], "discard")
							success = True

							# await message.channel.send("La carte `" + this.printCard(game["list"][index]) + "` a été défaussée depuis la " + ("pioche" if location == "deck" else "zone de " + self.userstr(location)))

				if success: await message.channel.send(await self.getRecap(game))
				self.objects.save_object("games", self.games)
			else:
				await message.channel.send("Veuillez renseigner l'index de la carte à modifier")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_move(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			print(args)

			args.pop(0)
			if len(args) > 1:
				cards = []

				for i, arg in enumerate(args):
					try:
						index = int(arg) - 1
					except:
						await message.channel.send("Index invalide : " + arg)
						return

					if i + 1 == len(args):
						index += 2

						if index < 1 or index >= len(list(game["zones"].keys())):
							await message.channel.send("Aucune zone n'a cette index")
							return
						else:
							self.moveCards(game, cards, list(game["zones"].keys())[index])
					else:
						if index < 0 or index >= len(game["list"]):
							await message.channel.send("Aucune carte n'a l'index " + index)
							return
						else:
							cards.append(index)

				await message.channel.send(await self.getRecap(game))
				self.objects.save_object("games", self.games)
			else:
				await message.channel.send("Veuillez renseigner l'index des cartes à déplacer et l'index de la zone d'arrivée")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_shuffle(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			print(args)

			args.pop(0)
			if len(args):
				cards = []

				for i, arg in enumerate(args):
					try:
						index = int(arg) - 1
					except:
						await message.channel.send("Index invalide : " + arg)
						return

					if index < 0 or index >= len(game["list"]):
						await message.channel.send("Aucune carte n'a l'index " + index)
						return
					else:
						cards.append(index)

				# position = 0
				# if "top" in kwargs:
				# 	try:
				# 		position = min(len(game["zones"]["deck"], int(top)))
				# 	except:
				# 		await message.channel.send("Nombre de cartes pour l'argument `top` invalide")
				# 		return

				self.moveCards(game, cards, "deck")
				random.shuffle(game["zones"]["deck"])

				await message.channel.send(await self.getRecap(game))
				self.objects.save_object("games", self.games)
			else:
				await message.channel.send("Veuillez renseigner l'index des cartes à mélanger dans le paquet")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_list(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			# await message.channel.send("Listes des cartes:")
			await self.sendCardList(message.channel)
			# await self.sendBigMessage("Défausse\n========\n" + '\n'.join([self.printCard(game["list"][e]) if game["list"][e] else "[En attente de défintion...](?)" for e in game["discard"]]), message.channel)
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_show(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]

			args.pop(0)
			if len(args):
				try:
					index = int(args[0]) + 1
				except:
					await message.channel.send("Index de zone invalide")
					return

				if index < 1 and index >= len(list(game["zones"].keys())):
					await message.channel.send("Aucune zone n'a cet index")
					return

				location = list(game["zones"].keys())[index]

				content = "\n= • - Recap - • =\n=================\n"
				content += str(index - 1).rjust(2, ' ') + ". " + ("Défausse" if index == 1 else ("Centre" if index == 2 else (await self.userstr(location)))) + " :\n" + '\n'.join(["  • " + str(x + 1).rjust(3, ' ') + ". " + (await self.printCard(game["list"][x], False)) for x in game["zones"][location]])

				await self.sendBigMessage(content, message.channel, "ini")
			else:
				await message.channel.send(await self.getRecap(game))
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_start(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			await message.channel.send("Il y a déjà une partie en cours dans ce salon")
		elif message.guild:
			if len(args) > 1:
				try:
					amount = int(args[1])
				except:
					await message.channel.send("Veuillez renseigner le nombre de cartes dans le deck")
					return

				game = {
					"zones": {
						"deck": [i for i in range(amount)],
						"discard": [],
						"center": []
					},
					"list": [None for i in range(amount)],
					"admin": message.author.id
				}

				random.shuffle(game["zones"]["deck"])

				self.games[str(message.channel.id)] = game
				await message.channel.send("Partie créée")

				self.objects.save_object("games", self.games)
			else:
				await message.channel.send("Veuillez renseigner le nombre de cartes dans le deck")

	async def com_edit(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			if len(args) > 1:
				try:
					index = int(args[1]) - 1
				except:
					await message.channel.send("Veuillez renseigner l'index de la carte à modifier")
					return

				if index < 0 or index >= len(game["list"]):
					await message.channel.send("Aucune carte n'a cet index")
				else:
					msg = await message.channel.send("```ini\nRedéfinissez cette carte en tapant \"[Nom de la carte] Effet\".```")
					card = game["list"][index]

					newCard = await self.startCardCreation(message.author, message.channel, index)
					await self.editCard(game, index, card, message.channel)

					await msg.edit(content="```ini\n" + (await self.printCard(newCard)) + "```")

				self.objects.save_object("games", self.games)
			else:
				await message.channel.send("Veuillez renseigner l'index de la carte à modifier")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_burn(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			if len(args) > 1:
				try:
					index = int(args[1]) - 1
				except:
					await message.channel.send("Veuillez renseigner l'index de la carte à brûler")
					return

				if index < 0 or index >= len(game["list"]):
					await message.channel.send("Aucune carte n'a cet index")
				else:
					card = game["list"][index]

					game["list"][index] =  {
						"author": message.author.id,
						"name": None,
						"effect": "",
						"history": []
					}

					await self.editCard(game, index, card, message.channel)
					await message.channel.send("```Carte (" + str(index + 1) + ") brûlée```")

				self.objects.save_object("games", self.games)
			else:
				await message.channel.send("Veuillez renseigner l'index de la carte à brûler")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_end(self, message, args, kwargs):
		if len(args) > 1:
			if args[1] == "force":
				await self.endGame(message.channel)
				return

		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			if (game["admin"] == message.author.id):
				await self.endGame(message.channel)
			else:
				await message.channel.send("Vous n'avez pas le droit d'exécuter cette commande. Seul l'administrateur de la partie peut l'arrêter")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def com_history(self, message, args, kwargs):
		if str(message.channel.id) in self.games:
			game = self.games[str(message.channel.id)]
			if len(args) > 1:
				index = None
				try:
					index = int(args[1]) - 1
				except:
					await message.channel.send("Veuillez renseigner l'index de la carte à voir")
					return

				if index < 0 or index >= len(game["list"]):
					await message.channel.send("Aucune carte n'a cet index")
				elif not game["list"][index]:
					await message.channel.send("Carte Blanche")
				else:
					card = game["list"][index]
					await self.sendBigMessage("Carte actuelle : " + (await self.printCard(card)) + "\n" + '\n'.join(["  ↳ " + (await self.printCard(e)) for e in card["history"]]), message.channel)
			else:
				await message.channel.send("Veuillez renseigner l'index de la carte à voir")
		else:
			await message.channel.send("Aucune partie n'est actuellement en cours dans ce salon")

	async def endGame(self, channel):
		await self.sendCardList(channel)
		await channel.send(await self.getRecap(self.games[str(channel.id)]))
		del self.games[str(channel.id)]
		await channel.send("Partie finie!")

		self.objects.save_object("games", self.games)

	def moveCards(self, game, cards, zone, position=None):
		if not position: position = len(game["zones"][zone])

		for card in cards:
			location = [x for x in game["zones"] if card in game["zones"][x]][0]
			game["zones"][location].remove(card)
			game["zones"][zone].insert(position, card)

	async def editCard(self, game, index, card, channel):
		newCard = game["list"][index]

		newCard["history"].append({
			"author": card["author"],
			"name": card["name"],
			"effect": card["effect"]
		})
		newCard["history"].extend(card["history"])
		# await message.channel.send("Carte éditée")

		location = [x for x in game["zones"] if index in game["zones"][x]][0]
		if location not in ["deck", "discard"]:
			game["zones"][location].remove(index)
			game["zones"]["discard"].append(index)
			await channel.send("La carte a été défaussée suite à la modification")

			await channel.send(await self.getRecap(game))

	async def sendBigMessage(self, message, channel, language="ini"):
		sentences = message.split("\n")
		form = ""

		for sentence in sentences:
			if (len(form) + len(sentence) + len(language) > 1990):
				await channel.send("```" + language + "\n" + form + "```")
				form = ""

			form += sentence + "\n"

		return await channel.send("```" + language + "\n" + form + "```")

	async def sendCardList(self, channel):
		game = self.games[str(channel.id)]
		await self.sendBigMessage(
			"[Liste des cartes en jeu]\n=========================\n"
			+ '\n'.join([str(i + 1).rjust(3, ' ') + ". " + (await self.printCard(e, False) if e else "(Carte Blanche)") for i, e in enumerate(game["list"])]), channel
		)

	async def getRecap(self, game, message=""):
		maxLength = len("Centre")
		for i, k in enumerate(list(game["zones"].keys())):
			if k not in ["center", "discard", "deck"]: maxLength = max(maxLength, len(await self.userstr(k)))

		def sendZone(zone):
			return ' '.join(["[" + str(x + 1) + " " + (game["list"][x]["name"] if game["list"][x]["name"] else "Carte Blanche") + "]" for x in zone])

		content = message
		content += "```md"
		content += "\n= • - Recap - • =\n================="
		content += "\n\n••• Paquet : " + str(len(game["zones"]["deck"])) + " carte(s)"
		content += "\n 0. Défausse : " + sendZone(game["zones"]["discard"])
		content += "\n\n 1. Centre : " + sendZone(game["zones"]["center"])
		content += "\n\n" + '\n'.join([str(list(game["zones"].keys()).index(k) - 1).rjust(2, ' ') + ". " + (await self.userstr(k)).ljust(maxLength, ' ') + " : " + sendZone(v) for k, v in game["zones"].items() if k not in ["center", "deck", "discard"]])
		content += "```"

		return content

	async def startCardCreation(self, author, channel, index):
		regex = r"^\[(.{1,30})\] (.+)$"

		def check(m):
			return m.author == author and m.channel == channel and re.search(regex, m.content)

		msg = await self.client.wait_for('message', check=check)
		await msg.delete()

		match = re.match(regex, msg.content)

		card = {
			"author": author.id,
			"name": match.groups()[0],
			"effect": match.groups()[1],
			"history": []
		}
		self.games[str(channel.id)]["list"][index] = card

		return card

	async def waitForZone(self, author, channel):
		regex = r"^\d+$"

		def check(m):
			return m.author == author and m.channel == channel and re.search(regex, m.content)

		msg = await self.client.wait_for('message', check=check)
		await msg.delete()

		index = int(msg.content) + 1
		locations = list(self.games[str(channel.id)]["zones"].keys())

		if index >= len(locations):
			await channel.send("Zone invalide")
			return await self.waitForZone(author, channel)
		else:
			return locations[index]

	async def printCard(self, card, authored=True):
		return ("[" + card["name"] + "]" if card["name"] else "(Carte Blanche)") + " " + card["effect"] + (" (Créée par " + (await self.userstr(card["author"])) + ")" if authored else "")

	async def userstr(self, id):
		try:
			user = await self.client.fetch_user(int(id))
			# print(user)
			return user.name
		except Exception as e:
			print(e)
			return str(id)

	# def printCardAuthors(self, card):
	# 	return "(Créée par " + card["author"] + ")"
