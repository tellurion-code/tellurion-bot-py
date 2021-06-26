import discord
import random
import math
import copy

import modules.city.globals as global_values

class Unit:
	def __init__(self, owner):
		self.owner = owner
		self.level = 0
		self.used = False
		self.decoration = random.choice(global_values.tile_decorations)

class Player:
	name = "🚫 Sans-Pouvoir"
	description = "N'a pas de pouvoir spécial"
	index = -1
	power_active = False
	revenue = 0
	bank = 0

	def __init__(self, game, user):
		self.game = game
		self.user = user
		self.variables = {}

	def spawn(self, amount, index):
		if amount:
			for i in range(amount):
				while True:
					x = random.randrange(5)
					y = random.randrange(5)

					if self.game.map[y][x] == None:
						break

				self.game.map[y][x] = Unit(self.index)
		else:
			for y in range(5):
				for x in range(5):
					if self.game.map[y][x] == None:
						self.game.map[y][x] = Unit(self.index)
						amount += 1

		self.index = index
		self.bank = amount * 2 + self.game.costs["creation"] * int(.5 + index*.5 if index else 0)

	def update_revenue(self, update_bank=False):
		self.revenue = 0

		for y in range(5):
			for x in range(5):
				if self.game.map[y][x].owner == self.index:
					self.revenue += 1

		if update_bank:
			self.bank += self.revenue

	def on_turn_start(self):
		self.update_revenue(True)

		for y in range(5):
			for x in range(5):
				if self.game.map[y][x].owner == self.index:
					self.game.map[y][x].used = False

	def on_turn_end(self, game):
		pass

	def active_power(self, game):
		pass
