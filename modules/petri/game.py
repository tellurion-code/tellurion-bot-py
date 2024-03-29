import discord
import random
import math
import copy

from modules.reaction_message.reaction_message import ReactionMessage
from modules.petri.player import Player

import modules.petri.globals as global_values

classes = {"player": Player}
classes.update({c.__name__.lower(): c for c in Player.__subclasses__()})

class Game:
	def __init__(self, mainclass, **kwargs):
		message = kwargs["message"] if "message" in kwargs else None
		self.mainclass = mainclass

		if message:
			self.channel = message.channel
			self.players = {
				message.author.id: Player(message.author)
			}  # Dict pour rapidement accéder aux infos
		else:
			self.channel = None
			self.players = {}

		self.order = []  # Ordre des id des joueurs
		self.turn = -1  # Le tour (index du joueur en cours) en cours, -1 = pas commencé
		self.round = 1  # Le nombre de tours de table complets
		self.map = []  # Carte où la partie se déroule
		self.ranges = [10, 10, 2]  # Taille horizontale, taille verticale, nombre de murs par quartiers
		self.info_message = None
		self.game_creation_message = None
		self.power_selection_message = None
		self.last_choice = -1

	async def reload(self, object, client):
		await self.deserialize(object, client)
		await self.send_info()

	async def on_creation(self, message):
		async def start(reactions):
			if len([0 for x in reactions.values() if 0 in x]):
				await self.send_power_selection()
			else:
				await self.start_game()

		async def update(reactions):
			if len([0 for x in reactions.values() if 1 in x]):
				await self.game_creation_message.message.remove_reaction("📩", self.mainclass.client.user)
			else:
				await self.game_creation_message.message.add_reaction("📩")

			self.players = {}
			for player_id, reaction in reactions.items():
				if 1 in reaction:
					self.players[player_id] = Player(self.mainclass.client.get_user(player_id))

			embed = self.game_creation_message.message.embeds[0]

			embed.set_field_at(
				0,
				name="🦸 Pouvoirs",
				value="Activé" if len([0 for x in reactions.values() if 0 in x]) else "Désactivé"
			)

			embed.description = "Cliquez sur la réaction 📩 pour rejoindre la partie.\n\n__Joueurs:__\n" + '\n'.join(["`"+ str(x.user) + "`" for x in self.players.values()])
			await self.game_creation_message.message.edit(embed=embed)

		async def cond(reactions):
			return len([0 for x in reactions.values() if 1 in x]) in range(2, 7)

		self.game_creation_message = ReactionMessage(
			cond,
			start,
			update=update,
			check=lambda r, u: r.emoji == "📩" or u.id == message.author.id
		)

		await self.game_creation_message.send(
			message.channel,
			"Création de la partie de Petri",
			"Appuyez sur la réaction 📩 pour vous inscrire au jeu.\n\n__Joueurs:__\n",
			global_values.color,
			["Pouvoirs", "Inscription"],
			emojis=["🦸", "📩"],
			silent=True,
			fields=[{
				"name": "🦸 Pouvoirs",
				"value": "Désactivé"
			}]
		)

	async def send_power_selection(self):
		self.game_creation_message = None

		choices = list(classes.keys())
		emojis = [classes[x].name.split()[0] for x in choices]
		fields = [{
			"name": classes[x].name,
			"value": classes[x].description
		} for x in choices]

		async def start(reactions):
			for player_id, choice in reactions.items():
				self.players[player_id] = classes[choices[choice[0]]](self.players[player_id].user)

			await self.start_game()

		async def cond(reactions):
			return len([0 for x in reactions.values() if len(x) == 1]) == len(self.players)

		self.power_selection_message = ReactionMessage(
			cond,
			start,
			check=lambda r, u: u.id in self.players
		)

		await self.power_selection_message.send(
			self.channel,
			"🦸 Choix des pouvoirs",
			"Choississez un pouvoir pour la partie",
			global_values.color,
			choices,
			emojis=emojis,
			silent=True,
			fields=fields
		)

	async def start_game(self):
		self.turn = 0
		self.game_creation_message = None
		self.power_selection_message = None

		for y in range(self.ranges[1]):
			self.map.append([])
			for _ in range(self.ranges[0]):
				self.map[y].append(-1)  # -1 = vide, -2 = mur

		for player_id, player in self.players.items():
			self.order.append(player_id)

		random.shuffle(self.order)

		for i, player_id in enumerate(self.order):
			self.players[player_id].index = i

		def check_bloating(map):
			for y in range(1, self.ranges[1]-1):
				for x in range(1, self.ranges[0]-1):
					count = 0
					for dx in range(-1, 2):
						for dy in range(-1, 2):
							if map[y + dy][x + dx] == -2:
								count += 1
					if count >= 2:
						return False
			return True

		new_map = None
		while True:
			new_map = copy.deepcopy(self.map)
			for my in range(0, self.ranges[1], int(self.ranges[1]/2)):
				for mx in range(0, self.ranges[0], int(self.ranges[0]/2)):
					for _ in range(self.ranges[2]):
						x = mx
						y = my

						while True:
							x = mx + random.randrange(self.ranges[0]/2)
							y = my + random.randrange(self.ranges[1]/2)
							if new_map[y][x] == -1:
								break

						new_map[y][x] = -2

			r, a = round(min(self.ranges[0], self.ranges[1])/3), random.uniform(0, math.pi*2)

			for i, player_id in enumerate(self.players.keys()):
				sx, sy = 0, 0
				while True:
					sx, sy = int(round(self.ranges[0]/2 - .5 + r * math.cos(a))), int(round(self.ranges[1]/2 - .5 + r * math.sin(a)))

					if new_map[sy][sx] == -1:
						break

					a += math.pi/20

				self.players[player_id].spawn(self, new_map, sx, sy)
				a += math.pi/len(self.players) * 2

			valid = check_bloating(new_map)

			if valid:
				break

		self.map = new_map

		await self.send_info()
		self.save()

	# Envoies le résumé de la partie aux joueurs + le channel
	async def send_info(self, **kwargs):
		info = kwargs["info"] if "info" in kwargs else None
		color = kwargs["color"] if "color" in kwargs else global_values.color

		row_strings = []
		for y in range(self.ranges[1]):
			row_strings.append("")
			for x in range(self.ranges[0]):
				row_strings[-1] += global_values.tile_colors[self.map[y][x] + 2]

		map_string = '\n'.join(row_strings)

		fields = []

		fields.append({
			"name": "Joueurs (Score de Domination : " + str(int((self.ranges[0] * self.ranges[1])/2)) +  ")" + (" / Dernière direction choisie : " + global_values.choice_emojis[self.last_choice] if self.last_choice != -1 else ""),
			"value":'\n'.join([self.players[x].show_player(self) for i, x in enumerate(self.order)])
		})

		if self.round > 40:
			fields.append({
				"name": "💀 Mort Subite 💀",
				"value": "Le premier joueur à prendre l'avantage gagne"
			})

		if info:
			fields.append({
				"name": info["name"],
				"value": info["value"]
			})

		# --[ANCIEN BROADCAST]--
		# await self.channel.send(embed = embed)
		# for player in self.players.values():
		#	 await player.user.send(embed = embed)

		if self.info_message:
			embed=discord.Embed(
				title="[PETRI Manche " + str(self.round) + "] Tour de `" + str(self.players[self.order[self.turn]].user) + "`",
				description=map_string,
				color=global_values.player_colors[self.turn]
			)

			for field in fields:
				embed.add_field(
					name=field["name"],
					value=field["value"],
					inline=field["inline"] if "inline" in field else False
				)

			await self.info_message.message.edit(embed=embed)
		else:
			choices = ["Gauche", "Haut", "Bas", "Droite", "Capituler", "Valider"]
			if len([0 for x in self.players.values() if x.power_active]):
				choices.append("Pouvoir")

			async def next_turn(reactions):
				if self.order[self.turn] in reactions:
					if len(reactions[self.order[self.turn]]):
						if reactions[self.order[self.turn]][0] == 6:
							field = self.players[self.order[self.turn]].active_power(self)
							await self.send_info(info=field)

							await self.info_message.message.remove_reaction(global_values.choice_emojis[6], self.players[self.order[self.turn]].user)
							if not (self.players[self.order[self.turn]].power_active):
								self.info_message.reactions[self.order[self.turn]].pop(0)
						elif reactions[self.order[self.turn]][0] == 4:
							if 5 in reactions[self.order[self.turn]]:
								self.last_choice = 4

								for y in range(self.ranges[1]):
									for x in range(self.ranges[0]):
										if self.map[y][x] == self.turn:
											self.map[y][x] = -1

								for i in reactions[self.order[self.turn]]:
									await self.info_message.message.remove_reaction(global_values.choice_emojis[i], self.players[self.order[self.turn]].user)
								self.info_message.reactions = {}

								await self.next_turn({
									"name": "Capitulation",
									"value": global_values.tile_colors[self.turn + 2] + " `" + str(self.players[self.order[self.turn]].user) + "` a capitulé"
								})

								return
						elif reactions[self.order[self.turn]][0] < 4:
							self.last_choice = reactions[self.order[self.turn]][0] if len(reactions[self.order[self.turn]]) else self.last_choice

							summary = self.players[self.order[self.turn]].play(self, reactions[self.order[self.turn]][0])

							for i in reactions[self.order[self.turn]]:
								await self.info_message.message.remove_reaction(global_values.choice_emojis[i], self.players[self.order[self.turn]].user)
							self.info_message.reactions = {}

							if (summary is not None):
								await self.next_turn({
									"name": "Combats",
									"value": summary
								} if len(summary) else None)

			async def cond(reactions):
				return False

			self.info_message = ReactionMessage(
				cond,
				None,
				update=next_turn,
				temporary=False,
				check=lambda r, u: u.id == self.order[self.turn] and (r.emoji != global_values.choice_emojis[6] or self.players[u.id].power_active)
			)

			await self.info_message.send(
				self.channel,
				"[PETRI Manche " + str(self.round) + "] Tour de `" + str(self.players[self.order[self.turn]].user) + "`",
				map_string,
				global_values.player_colors[self.turn],
				choices,
				emojis=global_values.choice_emojis,
				silent=True,
				fields=fields
			)

	def inside(self, x, y):
		return x >= 0 and x < self.ranges[0] and y >= 0 and y < self.ranges[1]

	# Passe au prochain tour
	async def next_turn(self, message=None):
		while True:
			self.players[self.order[self.turn]].on_turn_end(self)

			self.turn = (self.turn + 1) % len(self.order)
			if self.turn == 0:
				self.round += 1

			self.players[self.order[self.turn]].on_turn_start(self)

			if len([0 for row in self.map for tile in row if tile == self.turn]) and len(self.players[self.order[self.turn]].check_for_moves(self)):
				break

		await self.send_info(info=message)

		if self.round > 30:
			max_score, winner, tie = 0, 0, False
			for i, player_id in enumerate(self.order):
				score = len([0 for row in self.map for tile in row if tile == i])
				if score == max_score:
					tie = True
				elif score > max_score:
					tie = False
					max_score = score
					winner = player_id

			if not tie:
				await self.end_game(str(self.players[winner].user), "Usure")
				return

		alives = [i for i in range(len(self.order)) if len([0 for row in self.map for tile in row if tile == i])]

		if len(alives) == 1:
			await self.end_game(str(self.players[self.order[alives[0]]].user), "Annihiliation")
			return

		for i in range(len(self.order)):
			if len([0 for row in self.map for tile in row if tile == i]) >= (self.ranges[0] * self.ranges[1])/2:
				await self.end_game(str(self.players[self.order[i]].user), "Domination")
				return

		self.save()

	# Fin de partie, envoies le message de fin et détruit la partie
	async def end_game(self, name, cause):
		embed = discord.Embed(title="[PETRI] Victoire " + ("d'`" if name[:1] in "EAIOU" else "de `") + name + "` par " + cause  + " !", color=global_values.color)

		players = [i for i in range(len(self.order))]
		players.sort(key=lambda e: len([0 for row in self.map for tile in row if tile == e]), reverse=True)

		embed.description = "**Joueurs :**\n" + '\n'.join([global_values.number_emojis[i] + " " + global_values.tile_colors[index + 2] + " `" + str(self.players[self.order[index]].user) + "` : " + str(len([0 for row in self.map for tile in row if tile == index])) for i, index in enumerate(players)])

		if self.info_message:
			await self.info_message.delete()
			await self.info_message.message.clear_reactions()

		await self.channel.send(embed=embed)
		self.delete_save()
		del global_values.games[self.channel.id]

	def serialize(self):
		object = {
			"channel": self.channel.id,
			"order": self.order,
			"turn": self.turn,
			"map": self.map,
			"ranges": self.ranges,
			"last_choice": self.last_choice,
			"round": self.round,
			"players": {}
		}

		for id, player in self.players.items():
			object["players"][id] = {
				"user": player.user.id,
				"class": player.__class__.__name__.lower(),
				"power_active": player.power_active,
				"index": player.index,
				"variables": player.variables
			}

		return object

	async def deserialize(self, object, client):
		self.channel = client.get_channel(object["channel"])
		self.order = object["order"]
		self.turn = int(object["turn"])
		self.round = int(object["round"])
		self.map = list(object["map"])
		self.ranges = object["ranges"]
		self.last_choice = object["last_choice"]
		self.players = {}

		for id, info in object["players"].items():
			player = self.players[int(id)] = classes[info["class"]](client.get_user(info["user"]))
			player.power_active = info["power_active"]
			player.index = info["index"]
			player.variables = info["variables"]

	def save(self):
		if self.mainclass.objects.save_exists("games"):
			object = self.mainclass.objects.load_object("games")
		else:
			object = {}

		object[self.channel.id] = self.serialize()
		self.mainclass.objects.save_object("games", object)

	def delete_save(self):
		if self.mainclass.objects.save_exists("games"):
			object = self.mainclass.objects.load_object("games")
			if str(self.channel.id) in object:
				object.pop(str(self.channel.id))

			self.mainclass.objects.save_object("games", object)
		else:
			print("no save")

  # Module créé par Le Codex#9836
