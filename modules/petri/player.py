import discord
import random
import math
import copy

from modules.reaction_message.reaction_message import ReactionMessage

import modules.petri.globals as global_values


class Player:
	name = "🚫 Sans-Pouvoir"
	description = "N'a pas de pouvoir spécial"
	index = -1
	power_active = False

	def __init__(self, user):
		self.user = user
		self.variables = {}

	def spawn(self, game, map, x, y):
		map[y][x] = self.index

	def move(self, game, new_map, dx, dy, summary):
		for y in range(game.ranges[1]):
			for x in range(game.ranges[0]):
				if game.map[y][x] == game.turn and game.inside(x + dx, y + dy):
					new_tile = game.map[y + dy][x + dx]
					if new_tile == -1:
						new_map[y + dy][x + dx] = game.turn
					elif new_tile >= 0 and new_tile != game.turn:
						owner = game.players[game.order[new_tile]]

						attack = self.get_power(game, x, y, -dx, -dy)
						defense = owner.get_power(game, x + dx, y + dy, dx, dy)

						diff = attack - defense
						diff += self.on_attack(game, attack, defense, new_tile)
						diff += owner.on_defense(game, attack, defense)

						if diff > 0:
							new_map[y + dy][x + dx] = game.turn
							summary.append(global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️ 🗡️ " + global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "`")
						elif diff == 0:
							new_map[y + dy][x + dx] = -1
							summary.append(global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️ ⚔️️ " + global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "`")
						else:
							summary.append(global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "` 🛡️ " + global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️")

	def get_power(self, game, x, y, dx, dy):
		power = 0
		tdx, tdy = 0, 0
		while game.map[y + tdy][x + tdx] == self.index:
			power += 1
			tdx += dx
			tdy += dy
			if not game.inside(x + tdx, y + tdy):
				break

		return power

	def on_attack(self, game, attack, defense, defender):
		return 0

	def on_defense(self, game, attack, defense):
		return 0

	def on_turn_start(self, game):
		pass

	def on_turn_end(self, game):
		pass

	def active_power(self, game):
		pass


class Defender(Player):
	name = "🛡️ Défenseur"
	description = "Ne perd pas d'unités lors d'une égalité en défense"

	def on_defense(self, game, attack, defense):
		return (-1 if attack == defense else 0)


class Attacker(Player):
	name = "🗡️ Attaquant"
	description = "Capture l'unité au lieu de la détruire lors d'une égalité en attaque"

	def on_attack(self, game, attack, defense, defender):
		return (1 if attack == defense else 0)


class Architect(Player):
	name = "🧱 Architecte"
	description = "Les murs qu'il touche font partie de ses unités"

	def test_for_wall(self, game, x, y):
		for dx2 in range(-1, 2):
			for dy2 in range(-1, 2):
				if game.inside(x + dx2, y + dy2):
					if game.map[y + dy2][x + dx2] == game.turn and abs(dx2 + dy2) == 1:
						return True

		return False

	def move(self, game, new_map, dx, dy, summary):
		for y in range(game.ranges[1]):
			for x in range(game.ranges[0]):
				valid = False
				if game.map[y][x] == -2:
					valid = self.test_for_wall(game, x, y)

				if (game.map[y][x] == game.turn or valid) and game.inside(x + dx, y + dy):
					new_tile = game.map[y + dy][x + dx]
					if new_tile == -1:
						new_map[y + dy][x + dx] = game.turn
					elif new_tile >= 0 and new_tile != game.turn:
						owner = game.players[game.order[new_tile]]

						attack = self.get_power(game, x, y, -dx, -dy)
						defense = owner.get_power(game, x + dx, y + dy, dx, dy)

						diff = attack - defense
						diff += self.on_attack(game, attack, defense, new_tile)
						diff += owner.on_defense(game, attack, defense)

						if diff > 0:
							new_map[y + dy][x + dx] = game.turn
							summary.append(global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️ 🗡️ " + global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "`")
						elif diff == 0:
							new_map[y + dy][x + dx] = -1
							summary.append(global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️ ⚔️️ " + global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "`")
						else:
							summary.append(global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "` 🛡️ " + global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️")

	# def get_power(self, game, x, y, dx, dy):
	#	 power = 0
	#	 tdx, tdy = 0, 0
	#	 while game.map[y + tdy][x + tdx] == self.index or game.map[y + tdy][x + tdx] == -2:
	#		 power += 1
	#		 tdx += dx
	#		 tdy += dy
	#		 if not game.inside(x + tdx, y + tdy):
	#			 break
	#
	#	 return power


# class Swarm(Player):
#	 name = "🐝 Essaim"
#	 description = "Commence avec deux unités en diagonale"
#
#	 def spawn(self, game, map, x, y):
#		 # map[y][x] = self.index
#
#		 done = False
#		 for i in range(0, 3):
#			 r = math.pi/2 * i
#			 nx1 = int(x + math.cos(r))
#			 ny1 = int(y + math.sin(r))
#			 nx2 = int(x + math.cos(r + math.pi/2))
#			 ny2 = int(y + math.sin(r + math.pi/2))
#			 if game.inside(nx1, ny2) and game.inside(nx2, ny2) and map[ny1][nx1] == -1 and map[ny2][nx2] == -1:
#				 map[ny1][nx1] = self.index
#				 map[ny2][nx2] = self.index
#				 done = True
#				 break
#
#		 if not done:
#			 map[y + 1][x] = self.index
#			 map[y][x + 1] = self.index


class Racer(Player):
	name = "👾 Glitcheur"
	description = "Peut prendre une fois dans la partie un second tour juste après le sien"
	power_active = True
	steal_turn = False

	def active_power(self, game):
		self.power_active = False
		self.steal_turn = True

		return {
			"name": "️👾 Pouvoir du Glitcheur",
			"value": "Le prochain tour sera le vôtre"
		}

	def on_turn_end(self, game):
		if self.steal_turn:
			self.steal_turn = False
			game.turn = (self.index - 1)%len(game.players)


# class Demolisher(Player):
#	 name = "🧨 Démolisseur"
#	 description = "Capture tous les murs qu'il encercle à la fin de son tour (diagonales non nécessaires)"
#
#	 def on_turn_end(self, game):
#		 def check_circling(x, y):
#			 amount = 0
#			 for dy in range(-1, 2):
#				 for dx in range(-1, 2):
#					 if game.inside(x + dx, y + dy):
#						 if game.map[y + dy][x + dx] != self.index and dx != dy:
#							 amount += 1
#
#			 return (amount >= 3)
#
#		 for y in range(game.ranges[1]):
#			 for x in range(game.ranges[0]):
#				 if game.map[y][x] == -2:
#					 if check_circling(x, y):
#						 game.map[y][x] = self.index


class Pacifist(Player):
	name = "🕊️ Pacifiste"
	description = "A un bonus de 2 en défense contre les joueurs qu'il n'a pas attaqué"

	def __init__(self, user):
		super().__init__(user)
		self.variables = {
			"peace_with": []
		}

	def spawn(self, game, map, x, y):
		map[y][x] = self.index

		self.variables["peace_with"] = [i for i in range(len(game.order))]

	def on_defense(self, game, attack, defense):
		return (-2 if game.turn in self.variables["peace_with"] else 0)

	def on_attack(self, game, attack, defense, defender):
		if defender in self.variables["peace_with"]:
			self.variables["peace_with"].remove(defender)

		return 0


class Isolated(Player):
	name = "🏚️ Isolé"
	description = "Ne perd pas les combats où il a une seule unité en défense"

	def on_defense(self, game, attack, defense):
		return (-math.inf if defense == 1 else 0)

class General(Player):
	name = "🚩 Général"
	description = "Peut doubler la valeur de ses unités pour deux manches"
	power_active = True

	def __init__(self, user):
		super().__init__(user)
		self.variables = {
			"turn": 0
		}

	def active_power(self, game):
		self.power_active = False
		self.variables["turn"] = 1

		return {
			"name": "🚩 Pouvoir du Général",
			"value": "Vos unités valent double pendant les deux prochaines manches"
		}

	def on_turn_start(self, game):
		self.variables["turn"] += 1 if self.variables["turn"] else 0
		if self.variables["turn"] == 3:
			self.variables["turn"] = 0

	def get_power(self, game, x, y, dx, dy):
		return (2 if self.variables["turn"] else 1) * super().get_power(game, x, y, dx, dy)


class Topologist(Player):
	name = "🍩 Topologiste"
	description = "Considère les bords du terrain comme adjacents"

	def move(self, game, new_map, dx, dy, summary):
		for y in range(game.ranges[1]):
			for x in range(game.ranges[0]):
				nx = (x + dx) % game.ranges[0]
				ny = (y + dy) % game.ranges[1]
				if game.map[y][x] == game.turn:
					new_tile = game.map[ny][nx]
					if new_tile == -1:
						new_map[ny][nx] = game.turn
					elif new_tile >= 0 and new_tile != game.turn:
						owner = game.players[game.order[new_tile]]

						attack = self.get_power(game, x, y, -dx, -dy)
						defense = owner.get_power(game, nx, ny, dx, dy)

						diff = attack - defense
						diff += self.on_attack(game, attack, defense, new_tile)
						diff += owner.on_defense(game, attack, defense)

						if diff > 0:
							new_map[ny][nx] = game.turn
							summary.append(global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️ 🗡️ " + global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "`")
						elif diff == 0:
							new_map[ny][nx] = -1
							summary.append(global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️ ⚔️️ " + global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "`")
						else:
							summary.append(global_values.tile_colors[new_tile + 2] + " `" + str(owner.user) + "` 🛡️ " + global_values.tile_colors[game.turn + 2] + " `" + str(self.user) + "`️")

	def get_power(self, game, x, y, dx, dy):
		power = 0
		tx, ty = x, y
		while game.map[ty][tx] == self.index:
			power += 1
			tx = (tx + dx) % game.ranges[0]
			ty = (ty + dy) % game.ranges[1]
			if power > max(game.ranges[0], game.ranges[1]):
				break

		return power


# class Border(Player):
#	 name = "🗺️ Frontalier"
#	 description = "Peut détruire __toutes__ les unités (y compris les siennes) qui touchent ses frontières avec un autre joueur, une fois dans la partie"
#	 power_active = True
#
#	 def active_power(self, game):
#		 self.power_active = False
#		 amount = 0
#
#		 new_map = copy.deepcopy(game.map)
#		 for y in range(1, game.ranges[1] - 1):
#			 for x in range(1, game.ranges[0] - 1):
#				 if new_map[y][x] == game.turn:
#					 self_destruct = False
#					 for dy in range(-1, 2):
#						 for dx in range(-1, 2):
#							 if new_map[y + dy][x + dx] != game.turn and new_map[y + dy][x + dx] > -1 and dy != dx:
#								 new_map[y + dy][x + dx] = -1
#								 amount += 1
#								 self_destruct = True
#					 if self_destruct:
#						 new_map[y][x] = -1
#						 amount += 1
#
#		 game.map = new_map
#
#		 return {
#			 "name": "️🗺️ Pouvoir du Frontalier",
#			 "value": str(amount) + " unités détruites"
#		 }


# class Delayed(Player):
#	 name = "⏳ Délayé"
#	 description = "Arrive en jeu 3 tours après le début du jeu. Commence avec 12 unités"
#	 x, y = 0, 0
#
#	 def spawn(self, game, map, x, y):
#		 self.x, self.y = max(1, min(x, game.ranges[0]-2)), max(1, min(y, game.ranges[1]-1))
#
#	 def on_turn_end(self, game):
#		 if game.round == 4:
#			 for dx in range(-1, 3):
#				 for dy in range(-1, 2):
#					 game.map[self.x + dx][self.y + dy] = self.index
