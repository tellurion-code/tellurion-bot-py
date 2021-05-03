import discord
import random
import math
import copy

from modules.reaction_message.reaction_message import ReactionMessage

import modules.hill.globals as global_values


class Player:
	name = "🚫 Sans-Pouvoir"
	description = "N'a pas de pouvoir spécial"
	index = -1
	score = 0
	power_active = False
	recruitment = []

	def __init__(self, user):
		self.user = user
		self.variables = {}

	def spawn(self, game, x, y, r):
		game.map[y][x] = self.index
		game.map[y + int(math.sin(r))][x + int(math.cos(r))] = self.index
		game.map[y + 2 * int(math.sin(r))][x + 2 * int(math.cos(r))] = self.index
		game.map[y + int(math.sin(r + math.pi/2))][x + int(math.cos(r + math.pi/2))] = self.index
		game.map[y + 2 * int(math.sin(r + math.pi/2))][x + 2 * int(math.cos(r + math.pi/2))] = self.index
		game.map[y + int(math.sin(r)) + int(math.sin(r + math.pi/2))][x + int(math.cos(r)) + int(math.cos(r + math.pi/2))] = self.index

	def move(self, game, dx, dy, summary):
		y = game.ranges[1] if dy == 1 else -1

		dir = [
			1 if dx == 0 else -dx,
			1 if dy == 0 else -dy
		]

		while True:
			y += dir[1]
			x = game.ranges[0] - 1 if dx == 1 else 0

			if not game.inside(x, y):
				break

			while True:
				if game.map[y][x] == game.turn:
					if game.inside(x + dx, y + dy):
						new_tile = game.map[y + dy][x + dx]
						game.map[y][x] = new_tile
						game.map[y + dy][x + dx] = game.turn
					elif game.map[y - dy][x - dx] == -1:
						self.recruitment.append([x - dx, y - dy])

				x += dir[0]
				if not game.inside(x, y):
					break

	def on_turn_start(self, game):
		pass

	def on_turn_end(self, game):
		for pos in self.recruitment:
			game.map[pos[1]][pos[0]] = game.turn

		for pos in game.hill:
			if game.map[pos[1]][pos[0]] == game.turn:
				self.score += 1

		self.recruitment.clear()

	def active_power(self, game):
		pass
