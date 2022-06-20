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

	def check_for_moves(self, game):
		moves = []
		variables = copy.deepcopy(self.variables)
		for i in range(4):
			move = self.move(game, i, [])
			if move != game.map: moves.append(move)
			self.variables = copy.deepcopy(variables)

		return moves

	def play(self, game, index):
		# Gère les combats et les réplications
		summary = []
		new_map = self.move(game, index, summary)
		# variables = copy.deepcopy(self.variables)

		# if game.map != new_map:
		game.map = new_map
		summary.sort()
		return '\n'.join(summary)
		# else:
		#	self.variables = variables
		# 	return None

	def move(self, game, index, summary):
		dx = [-1, 0, 0 , 1][index]
		dy = [0, -1, 1 , 0][index]
		new_map = copy.deepcopy(game.map)

		self.move_tiles(game, new_map, dx, dy, summary)

		return new_map

	def move_tiles(self, game, new_map, dx, dy, summary):
		for y in range(game.ranges[1]):
			for x in range(game.ranges[0]):
				nx = x + dx
				ny = y + dy
				self.move_tile(game, new_map, x, y, nx, ny, dx, dy, summary)

	def move_tile(self, game, new_map, x, y, nx, ny, dx, dy, summary):
		if game.map[y][x] == game.turn and game.inside(nx, ny):
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
	description = "A un bonus de +1 en défense"

	def on_defense(self, game, attack, defense):
		return -1


class Attacker(Player):
	name = "🗡️ Attaquant"
	description = "A un bonus de +1 en attaque"

	def on_attack(self, game, attack, defense, defender):
		return 1


class Architect(Player):
	name = "🧱 Architecte"
	description = "Les murs qu'il touche font partie de ses unités pour les combats"

	def get_power(self, game, x, y, dx, dy):
		 power = 0
		 tdx, tdy = 0, 0
		 while game.map[y + tdy][x + tdx] == self.index or game.map[y + tdy][x + tdx] == -2:
			 power += 1
			 tdx += dx
			 tdy += dy
			 if not game.inside(x + tdx, y + tdy):
				 break

		 return power


class Swarm(Player):
	name = "🐝 Essaim"
	description = "Commence avec deux unités en plus en ligne"

	def spawn(self, game, map, x, y):
		map[y][x] = self.index

		d1 = random.randrange(2)
		d2 = 1 - d1

		if game.inside(x + d1, y + d2) and game.inside(x - d1, y - d2) and map[y + d2][x + d1] == -1 and map[y - d2][x - d1] == -1:
			map[y + d2][x + d1] = self.index
			map[y - d2][x - d1] = self.index
		else:
			map[y + d1][x + d2] = self.index
			map[y - d1][x - d2] = self.index


class Racer(Player):
	name = "👾 Glitcheur"
	description = "Une fois par partie, peut prendre un second tour juste après le sien"
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
	description = "Jusqu'au 21e tour, ne peut pas être attaqué par les joueurs qu'il n'a pas attaqué"

	def __init__(self, user):
		super().__init__(user)
		self.variables = { "war_with": [] }

	def spawn(self, game, map, x, y):
		map[y][x] = self.index
		self.variables["war_with"] = []

	def on_defense(self, game, attack, defense):
		return (-math.inf if (game.turn not in self.variables["war_with"] and game.round <= 20) else 0)

	def on_attack(self, game, attack, defense, defender):
		if defender not in self.variables["war_with"]:
			self.variables["war_with"].append(defender)

		return 0


class Isolated(Player):
	name = "🏚️ Isolé"
	description = "En combat, prend le max entre les unités derrière et la moyenne des unités de chaque côté"

	def get_power(self, game, x, y, dx, dy):
		behind = self.get_power_sub(game, x, y, dx, dy);
		left = self.get_power_sub(game, x, y, dy, dx);
		right = self.get_power_sub(game, x, y, -dy, -dx);

		return max(behind, (left + right) / 2);

	def get_power_sub(self, game, x, y, dx, dy):
		power = 0
		tdx, tdy = 0, 0
		while game.map[y + tdy][x + tdx] == self.index:
			power += 1
			tdx += dx
			tdy += dy
			if not game.inside(x + tdx, y + tdy):
				break

		return power

class General(Player):
	name = "🚩 Général"
	description = "Une fois par partie, peut doubler la valeur de ses unités pour deux manches"
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

	def move_tiles(self, game, new_map, dx, dy, summary):
		for y in range(game.ranges[1]):
			for x in range(game.ranges[0]):
				nx = (x + dx) % game.ranges[0]
				ny = (y + dy) % game.ranges[1]
				self.move_tile(game, new_map, x, y, nx, ny, dx, dy, summary)

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

class Liquid(Player):
	name = "💧 Liquide"
	description = "Se déplace dans la direction choisie avant de se répliquer. Ne perd pas d'unités s'il se déplace depuis un bord"

	def play(self, game, index):
		# Gère les combats et les réplications
		summary = []
		game.map = self.move(game, index, summary)
		game.map = self.destroy(game, index)
		new_map = self.move(game, index, summary)
		# variables = copy.deepcopy(self.variables)

		game.map = new_map
		summary.sort()
		return '\n'.join(summary)

	def destroy(self, game, index):
		dx = [-1, 0, 0 , 1][index]
		dy = [0, -1, 1 , 0][index]

		new_map = copy.deepcopy(game.map)
		for y in range(game.ranges[1]):
			for x in range(game.ranges[0]):
				if game.map[y][x] == self.index:
					nx = x - dx
					ny = y - dy
					if game.inside(nx, ny):
						if game.map[ny][nx] != self.index:
							new_map[y][x] = -1


		return new_map

class Navigator(Player):
	name = "🧭 Navigateur"
	description = "Trois fois par partie, peut se déplacer en diagonale"
	power_active = True
	move_diagonally = False

	def __init__(self, user):
		super().__init__(user)
		self.variables = {
			"uses_remaining": 3
		}

	def move(self, game, index, summary):
		if (self.move_diagonally):
			dx = [-1, 1, -1, 1][index]
			dy = [-1, -1, 1, 1][index]
		else:
			dx = [-1, 0, 0, 1][index]
			dy = [0, -1, 1, 0][index]

		self.move_diagonally = False
		new_map = copy.deepcopy(game.map)

		self.move_tiles(game, new_map, dx, dy, summary)

		return new_map

	def active_power(self, game):
		if (self.move_diagonally):
			return

		self.move_diagonally = True
		self.variables["uses_remaining"] -= 1
		if (self.variables["uses_remaining"] == 0):
			self.power_active = False

		return {
			"name": "🧭 Pouvoir du Navigatuer",
			"value": "Votre direction choisie sera tournée de 45° dans le sens horaire ce tour (" + str(self.variables["uses_remaining"]) + " restants)"
		}


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
