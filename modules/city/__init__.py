import discord

from modules.city.player import Player
from modules.city.game import Game
from modules.reaction_message.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.city.globals as global_values
global_values.init()


class MainClass(BaseClassPython):
	name = "City"
	help = {
		"description": "Module du jeu City",
		"commands": {
			"`{prefix}{command} create`": "Crée une partie",
			"`{prefix}{command} reset`": "Reinitialise la partie",
			"`{prefix}{command} rules`": "Affiche les règles"
		}
	}
	help_active = True
	command_text = "city"
	color = global_values.color

	def __init__(self, client):
		super().__init__(client)
		self.config["name"] = self.name
		self.config["command_text"] = self.command_text
		self.config["color"] = self.color
		self.config["help_active"] = self.help_active
		self.config["configured"] = True
		self.config["auth_everyone"] = True

	async def on_ready(self):
		# if self.objects.save_exists("globals"):
		# 	object = self.objects.load_object("globals")
		# 	globals.debug = object["debug"]
		#
		# if self.objects.save_exists("games"):
		# 	games = self.objects.load_object("games")
		# 	for game in games.values():
		# 		globals.games[game["channel"]] = Game(self)
		# 		await globals.games[game["channel"]].reload(game, self.client)
		pass

	async def command(self, message, args, kwargs):
		if len(args):
			if args[0] == "join't":
				await message.channel.send(message.author.mention + " n'a pas rejoint la partie")

	async def com_create(self, message, args, kwargs):
		if message.channel.id in global_values.games:
			await message.channel.send("Il y a déjà une partie en cours dans ce channel")
		else:
			global_values.games[message.channel.id] = Game(self,message=message)
			await global_values.games[message.channel.id].on_creation(message)

	# Réitinitialise et supprime la partie
	async def com_reset(self, message, args, kwargs):
		if message.channel.id in global_values.games:
			async def confirm(reactions):
				if reactions[message.author.id][0] == 0:
					await message.channel.send("La partie a été réinitialisée")

					if globals.games[message.channel.id].game_message:
						await globals.games[message.channel.id].game_message.delete()

					globals.games[message.channel.id].delete_save()
					del global_values.games[message.channel.id]

			async def cond(reactions):
				if message.author.id in reactions:
					return len(reactions[message.author.id]) == 1
				else:
					return False

			await ReactionMessage(
				cond,
				confirm,
				check=lambda r, u: u.id == message.author.id
			).send(
				message.channel,
				"Êtes vous sûr.e de vouloir réinitialiser la partie?",
				"",
				self.color,
				["Oui", "Non"],
				emojis=["✅", "❎"],
				validation_emoji="⭕"
			)
		else:
			await message.channel.send("Il n'y a pas de partie en cours")

	# Active le debug: enlève la limitation de terme, et le nombre minimal de joueurs
	async def com_debug(self, message, args, kwargs):
		if message.author.id == 240947137750237185:
			global_values.debug = not global_values.debug
			await message.channel.send("Debug: " + str(global_values.debug))

			# if self.objects.save_exists("globals"):
			# 	save = self.objects.load_object("globals")
			# else:
			# 	save = {}
			#
			# save["debug"] = global_values.debug
			# self.objects.save_object("globals", save)

	async def com_rules(self, message, args, kwargs):
		embed = discord.Embed(
			title=":small_orange_diamond: Règles de City :small_orange_diamond:",
			color=global_values.color
		)

		embed.add_field(name=":small_blue_diamond: Début de partie :small_blue_diamond:", inline=False, value="""
Le jeu se déroule sur un plateau de 25 cases en 5x5. Chaque joueur commence à un nombre égal de cases en sa possession,réparties aléatoirement sur le terrain (le surplus va au dernier joueur).
		""")

		embed.add_field(name=":small_blue_diamond: Déroulement d’un tour :small_blue_diamond:", inline=False, value="""
Le joueur clique sur une case soit qui lui appartient, soit adjacente à une case qui lui appartient (les diagonales ne comptent pas):
- S'il choisit une case qui lui appartient, il crée une unité (🧍) sur cette case. Cette unité ne peut pas se déplacer avant le prochain tour. S'il y a déjà une unité, il l'améliore si possible (🧍 devient 🤺, 🤺 devient 🏇).
- S'il choisit une case adverse et a une unité adjacente, et qu'il n'y a pas d'unité de force égale ou supérieure sur la case, elle se déplace sur la case et la capture. Chaque unité ne peut se déplacer qu'une fois par tour.
		""")

		embed.add_field(name=":small_blue_diamond: Coûts :small_blue_diamond:", inline=False, value="""
Chaque unité a un coût:
- **🧍 Paysan:** 2 cases
- **🤺 Chevalier:** 4 cases
- **🏇 Cavalier:** 6 cases
Le coût total des unités est retiré au nombre de cases qui appartienne au joueur au début du tour. Si le résultat est négatif, il devra choisir des unités à tuer pour leur coût de maintien jusqu'à ce qu'il soit positif.
		""")

		embed.add_field(name=":small_blue_diamond: But du jeu :small_blue_diamond:", inline=False, value="""
Le joueur qui contrôle toutes les cases du plateau gagne.
		""")

		await message.channel.send(embed=embed)
