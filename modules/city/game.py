import discord
import random
import math
import copy

from modules.buttons.button import ComponentMessage
from modules.city.player import Player

import modules.city.globals as global_values

classes = {"player": Player}
classes.update({c.__name__.lower(): c for c in Player.__subclasses__()})

class Game:
	def __init__(self, mainclass, **kwargs):
		message = kwargs["message"] if "message" in kwargs else None
		self.mainclass = mainclass

		if message:
			self.channel = message.channel
			self.players = {
				message.author.id: Player(self, message.author)
			}  # Dict pour rapidement accéder aux infos
		else:
			self.channel = None
			self.players = {}

		self.order = []  # Ordre des id des joueurs
		self.turn = -1  # Le tour (index du joueur en cours) en cours, -1 = pas commencé
		self.round = 1  # Le nombre de tours de table complets
		self.map = []  # Carte où la partie se déroule
		self.game_message = None
		self.controls_message = None
		self.costs = {
			"creation": [4, 4, 4],
			"upkeep": [0, 3, 6, 9],
			"destruction": [2, 4, 6]
		}

	async def reload(self, object, client):
		pass

	async def on_creation(self, message):
		async def join_or_leave(button, interaction):
			if interaction.user.id not in self.players:
				self.players[interaction.user.id] = Player(self, interaction.user)
			else:
				del self.players[interaction.user.id]

			await update_join_message(interaction)

		async def start(button, interaction):
			await interaction.respond(type=6)
			await self.game_message.delete()

			for player in self.players.values():
				self.order.append(player.user.id)

			random.shuffle(self.order)

			for i, id in enumerate(self.order):
				self.players[id].index = i

			for y in range(5):
				self.map.append([])
				for x in range(5):
					self.map[y].append(None)

			amount = math.floor(25 / len(self.order))
			for i, id in enumerate(self.order):
				self.players[id].spawn(amount if i < len(self.order) - 1 else 0)

			self.turn = 0
			self.players[self.order[self.turn]].on_turn_start()

			await self.send_info()

		def enough_players():
			return len(self.players) >= 2 or global_values.debug

		self.game_message = ComponentMessage(
			[
				[
					{
						"effect": join_or_leave,
						"cond": lambda i: True,
						"label": "Rejoindre ou partir",
						"style": 1
					},
					{
						"effect": start,
						"cond": lambda i: i.user.id == message.author.id and enough_players(),
						"label": "Pas assez de joueurs",
						"style": 2,
						"disabled": True
					}
				]
			]
		)

		embed = discord.Embed(
			title="Partie de City | Joueurs (1) :",
			description='\n'.join(["`" + str(x.user) + "`" for x in self.players.values()]),
			color=global_values.color
		)

		await self.game_message.send(
			message.channel,
			embed=embed
		)

		async def update_join_message(interaction):
			self.game_message.components[0][1].style = 3 if enough_players() else 2
			self.game_message.components[0][1].label = "Démarrer" if enough_players() else "Pas assez de joueurs"
			self.game_message.components[0][1].disabled = False if enough_players() else True

			embed.title = "Partie de City | Joueurs (" + str(len(self.players)) + ") :"
			embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.players.values()])

			await interaction.respond(
				type=7,
				embed=embed,
				components=self.game_message.components
			)

	def get_embed(self):
		embed = discord.Embed(
			title="[CITY] Tour de `" + str(self.players[self.order[self.turn]].user) + "`",
			description='\n'.join([global_values.tile_colors[i] + " `" + str(self.players[x].user) + "`: " + str(self.players[x].bank) + (" :coin:" if self.players[x].bank >= 0 else " ❌") + " (**+" + str(self.players[x].revenue) + " -" + str(self.players[x].cost) + "**)" for i, x in enumerate(self.order)]),
			color=global_values.player_colors[self.turn]
		)

		return embed

	async def respond_to_interaction(self, interaction):
		await interaction.respond(type=7)

		self.game_message.embed = self.get_embed()
		components = self.generate_components()
		for y, row in enumerate(components):
			for x, component in enumerate(row):
				button = self.game_message.components[y][x]

				button.emoji = component["emoji"]
				button.style = component["style"]
				button.disabled = component["disabled"]

		await self.game_message.update()

	async def click_tile(self, button, interaction):
		x = button.index % 5
		y = math.floor(button.index/5)
		unit = self.map[y][x]
		current = self.players[self.order[self.turn]]

		if current.bank < 0:
			unit.level = 0
		else:
			if unit.owner == self.turn:
				# current.bank -= self.costs["creation"][unit.level]
				unit.level += 1
			else:
				unit2 = None
				level = unit.level
				for r in range(4):
					dx = int(math.cos(r * math.pi/2))
					dy = int(math.sin(r * math.pi/2))

					if x + dx >= 0 and x + dx < 5 and y + dy >= 0 and y + dy < 5:
						if self.map[y + dy][x + dx].owner == self.turn and self.map[y + dy][x + dx].level > level and not self.map[y + dy][x + dx].used:
							unit2 = self.map[y + dy][x + dx]
							level = unit2.level

				unit.level = unit2.level
				unit.owner = self.turn
				unit.used = True
				unit2.level = 0

		current.update_revenue(True)
		await self.respond_to_interaction(interaction)

	def generate_components(self):
		def check_disabled(x, y):
			if self.players[self.order[self.turn]].bank < 0:
				return not (self.map[y][x].owner == self.turn and self.map[y][x].level)
			else:
				if self.map[y][x].owner == self.turn:
					return self.map[y][x].level == 3 # or self.players[self.order[self.turn]].bank < self.costs["creation"][self.map[y][x].level]

				if self.round == 1:
					return True

				for r in range(4):
					dx = int(math.cos(r * math.pi/2))
					dy = int(math.sin(r * math.pi/2))

					if x + dx >= 0 and x + dx < 5 and y + dy >= 0 and y + dy < 5:
						if self.map[y + dy][x + dx].owner == self.turn and self.map[y + dy][x + dx].level > self.map[y][x].level and not self.map[y + dy][x + dx].used:
							return False

				return True

		components = []
		for y in range(5):
			components.append([])
			for x in range(5):
				unit = self.map[y][x]

				components[len(components) - 1].append({
					"effect": self.click_tile,
					"cond": lambda i: i.user.id == self.order[self.turn],
					"emoji": global_values.unit_emojis[unit.level - 1] if unit.level else global_values.tile_colors[unit.owner],
					"style": [4, 1, 3, 2][unit.owner],
					"disabled": check_disabled(x, y)
				})

		return components

	async def send_info(self):
		embed = self.get_embed()
		components = self.generate_components()

		self.game_message = ComponentMessage(components, temporary=False)

		await self.game_message.send(
			self.channel,
			embed=embed
		)

		async def pass_turn(button, interaction):
			await self.next_turn()
			await self.respond_to_interaction(interaction)

		self.controls_message = ComponentMessage(
			[
				[
					{
						"effect": pass_turn,
						"cond": lambda i: i.user.id == self.order[self.turn],
						"label": "Passer le tour",
						"style": 3
					}
				]
			]
		)

		await self.controls_message.send(
			self.channel,
			content="Contrôles supplémentaires"
		)

	async def next_turn(self):
		self.turn = (self.turn + 1) % len(self.order)
		if (self.turn == 0):
			self.round += 1

		self.players[self.order[self.turn]].on_turn_start()

	async def deserialize(self, object, client):
		self.channel = client.get_channel(object["channel"])
		self.order = object["order"]
		self.turn = int(object["turn"])
		self.round = int(object["round"])
		self.map = list(object["map"])
		self.hill = list(object["hill"])
		self.ranges = object["ranges"]
		self.last_choice = object["last_choice"]
		self.players = {}

		for id, info in object["players"].items():
			player = self.players[int(id)] = classes[info["class"]](client.get_user(info["user"]))
			player.power_active = info["power_active"]
			player.index = info["index"]
			player.variables = info["variables"]
			player.score = info["score"]

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
