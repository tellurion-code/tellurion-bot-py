import discord
import random
import math

from modules.avalon.player import Player, Good, Evil
from modules.buttons.button import ComponentMessage

import modules.avalon.globals as global_values

classes = {"good": Good, "evil": Evil}
classes.update({c.__name__.lower(): c for t in [Good, Evil] for c in t.__subclasses__()})
# print(classes)

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
		self.turn = -1  # Le tour (index du leader) en cours, -1 = pas commencé
		self.round = 0  # Quête en cours
		self.team = {}  # Equipe qui part en quête. Contient les indices d'ordre et les id
		self.quests = []  # Réussite (-1) ou échec (0) des quêtes. Chiffre supérieur à 0 = pas faite
		self.refused = 0  # Nombre de gouvernements refusés
		self.info_message = None
		self.played = []  # Dernière cartes jouées
		self.roles = []  # Rôles
		self.phase = "team_selection"
		self.lady_of_the_lake = 0  # Index du joueur qui a la Dame du Lac
		self.game_rules = {
			"lancelot_know_evil": False,
			"evil_know_lancelot": True,
			"4th_quest_two_failures": True,
			"uther_learns_role": False,
			"lady_of_the_lake": False,
			"agravain_know_oberon": False
		}

	async def reload(self, object, client):
		# await self.deserialize(object, client)
		#
		# if object["state"]["type"] == "send_team_choice":
		#	 await self.send_team_choice()
		# elif object["state"]["type"] == "quest":
		#	 await self.send_players_quest_choice()
		# elif object["state"]["type"] == "next_turn":
		#	 await self.next_turn()
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

			await self.start_game()

		def enough_players():
			if global_values.debug:
				return {
					"bool": True,
					"reason": "Démarrer"
				}

			if len(self.players) < 5:
				return {
					"bool": False,
					"reason": "Pas assez de joueurs"
				}
			elif len(self.players) > 10:
				return {
					"bool": False,
					"reason": "Trop de joueurs"
				}
			elif len(self.roles) and len(self.players) != len(self.roles):
				return {
					"bool": False,
					"reason": "Nombre de joueurs différent du nombre de rôles (" + str(len(self.roles)) + ")"
				}
			else:
				return {
					"bool": True,
					"reason": "Démarrer"
				}

		self.info_message = ComponentMessage(
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
						"cond": lambda i: i.user.id == message.author.id and enough_players()["bool"],
						"label": "Pas assez de joueurs",
						"style": 2,
						"disabled": True
					}
				]
			]
		)

		embed = discord.Embed(
			title="Partie d'Avalon | Joueurs (1) :",
			description='\n'.join(["`" + str(x.user) + "`" for x in self.players.values()]),
			color=global_values.color
		)

		await self.info_message.send(
			message.channel,
			embed=embed
		)

		async def update_join_message(interaction):
			self.info_message.components[0][1].style = 3 if enough_players()["bool"] else 2
			self.info_message.components[0][1].label = enough_players()["reason"]
			self.info_message.components[0][1].disabled = not enough_players()["bool"]

			embed.title = "Partie d'Avalon | Joueurs (" + str(len(self.players)) + ") :"
			embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.players.values()])

			await interaction.respond(
				type=7,
				embed=embed,
				components=self.info_message.components
			)

	async def start_game(self):
		self.turn = -1

		quests = [
			[],  # 0
			[],  # 1
			[1, 1, 2, 2, 2],  # 2, Debug
			[1, 2, 2, 2, 2],  # 3
			[2, 2, 2, 2, 2],  # 4
			[2, 3, 2, 3, 3],  # 5
			[2, 3, 4, 3, 4],  # 6
			[2, 3, 3, 4, 4],  # 7
			[3, 4, 4, 5, 5],  # 8
			[3, 4, 4, 5, 5],  # 9
			[3, 4, 4, 5, 5]  # 10
		]

		self.quests = quests[len(self.players)]

		roles = [
			[],  # 0?
			["good"],  # 1
			["good", "evil"],  # 2, Debug
			["good", "good", "evil"],  # 3
			["good", "good", "good", "evil"],  # 4
			["merlin", "percival", "good", "morgane", "assassin"],  # 5
			["merlin", "percival", "good", "good", "morgane", "assassin"],  # 6
			["merlin", "percival", "good", "good", "evil", "morgane", "assassin"],  # 7
			["merlin", "percival", "good", "good", "good", "evil", "morgane", "assassin"],  # 8
			["merlin", "percival", "good", "good", "good", "good", "evil", "morgane", "assassin"],  # 9
			["merlin", "percival", "good", "good", "good", "good", "evil", "evil", "morgane", "assassin"],  # 10
		]

		if len(self.roles) == 0:
			self.roles = roles[len(self.players)]

		for player_id in self.players:
			self.order.append(player_id)

		random.shuffle(self.order)
		random.shuffle(self.roles)

		for i in range(len(self.order)):
			self.players[self.order[i]] = classes[self.roles[i]](self, self.players[self.order[i]].user)

		for i in range(len(self.order)):
			await self.players[self.order[i]].game_start()

		random.shuffle(self.roles)

		self.lady_of_the_lake = len(self.players) - 1

		await self.start_turn(None)

	# Envoies le résumé de la partie aux joueurs + le channel
	def get_info_embed(self, **kwargs):
		info = kwargs["info"] if "info" in kwargs else None
		color = kwargs["color"] if "color" in kwargs else global_values.color

		embed = discord.Embed(
			title="[AVALON] Tour de `" + str(self.players[self.order[self.turn]].user) + "` 👑",
			description="",
			color=color
		)

		embed.add_field(
			name="Quêtes :",
			value=" ".join([global_values.number_emojis[x - 1] if x > 0 else (str(global_values.quest_choices["emojis"]["success"]) if x else str(global_values.quest_choices["emojis"]["failure"])) for x in self.quests])
		)

		embed.add_field(
			name="Equipes refusées :",
			value="🟧 " * self.refused + "🔸 " * (5 - self.refused)
		)

		embed.add_field(
			name="Chevaliers :",
			value='\n'.join([(("📩" if self.phase == "team_selection" else (str(global_values.vote_choices["emojis"][self.players[x].last_vote]))) if len(self.players[x].last_vote) else "✉️") + global_values.number_emojis[i] + " `" + str(self.players[x].user) + "` " + ("👑" if self.turn == i else "") + ("🌊" if self.lady_of_the_lake == i and self.game_rules["lady_of_the_lake"] else "") for i, x in enumerate(self.order)]),
			inline=False
		)

		if len(self.team):
			embed.add_field(
				name="Participants à la Quête :",
				value='\n'.join([(global_values.number_emojis[i] + ' `' + str(self.players[x].user) + '`') for i, x in self.team.items()]),
				inline=False
			)

		if self.round == 3 and len(self.players) >= 7 and self.game_rules["4th_quest_two_failures"]:
			embed.add_field(
				name="4e Quête",
				value="⚠️ **Quête échouée à partir de deux échecs** ⚠️\n",
				inline=False
			)

		if info:
			embed.add_field(name=info["name"], value=info["value"])

		return embed

	async def send_info(self, **kwargs):
		mode = kwargs["mode"] if "mode" in kwargs else "replace"
		components = None
		if "components" in kwargs:
			components = kwargs["components"]
			components.append([{
				"effect": lambda b, i: self.players[i.user.id].send_role_info(i),
				"cond": lambda i: i.user.id in self.players,
				"label": "Voir son rôle",
				"style": 2
			}])

		embed = self.get_info_embed(**kwargs)
		if mode == "replace":
			self.info_message.embed = embed
			await self.info_message.update(components)
		elif mode == "set":
			if self.info_message:
				await self.info_message.delete()

			self.info_message = ComponentMessage(components, temporary=False)
			await self.info_message.send(self.channel, embed=embed)

	async def start_turn(self, message):
		self.phase = "team_selection"
		self.turn = (self.turn + 1) % len(self.order)

		for player in self.players.values():
			player.last_vote = ""
			player.last_choice = ""

		self.team = {}

		await self.send_team_choice(message)

		# self.save({"type":"send_team_choice"})

	# Est aussi un début de tour, envoies le choix de team
	async def send_team_choice(self, message):
		leader = self.players[self.order[self.turn]]  # Tour actuel

		valid_candidates = [x for i, x in enumerate(self.order)]
		num_player_rows = math.ceil(len(valid_candidates)/5)

		async def select_or_unselect(button, interaction):
			if button.index in self.team:
				del self.team[button.index]
				button.style = 2
			else:
				self.team[button.index] = self.order[button.index]
				button.style = 1

			confirm_button = self.info_message.components[num_player_rows][0]
			if len(self.team) == self.quests[self.round]:
				confirm_button.disabled = False
				confirm_button.label = "Confirmer l'équipe"
				confirm_button.style = 3
			else:
				confirm_button.disabled = True
				confirm_button.label = "Nombre de membres invalide"
				confirm_button.style = 2

			await interaction.respond(type=6)
			await self.info_message.message.edit(components=self.info_message.components)

		async def confirm_team(button, interaction):
			await interaction.respond(type=6)

			await self.send_players_vote_choice()

		components = []
		for y in range(num_player_rows):
			components.append([])
			for x in range(5):
				if 5 * y + x == len(valid_candidates):
					break

				components[len(components) - 1].append({
					"effect": select_or_unselect,
					"cond": lambda i: i.user.id == self.order[self.turn],
					"label": str(self.players[valid_candidates[5 * y + x]].user),
					"style": 2
				})

		components.append([{
			"effect": confirm_team,
			"cond": lambda i: i.user.id == self.order[self.turn],
			"label": "Nombre de membres invalide",
			"style": 2,
			"disabled": True
		}])

		await self.send_info(mode="set", info=message, components=components)

	async def send_players_vote_choice(self):
		choices = [x for x in global_values.vote_choices["names"].keys()]

		async def cast_vote(button, interaction):
			last_vote = choices[button.index]
			self.players[interaction.user.id].last_vote = last_vote

			await interaction.respond(type=4, content="Vous avez voté " + str(global_values.vote_choices["emojis"][last_vote]) + " " + global_values.vote_choices["names"][last_vote])
			await self.info_message.message.edit(embed=self.get_info_embed())
			await self.check_vote_end()

		components = [[]]
		for choice in choices:
			components[0].append({
				"effect": cast_vote,
				"cond": lambda i: i.user.id in self.players,
				"label": global_values.vote_choices["names"][choice],
				"style": global_values.vote_choices["styles"][choice]
			})

		await self.send_info(components=components)

	# Appelé à chaque fois qu'un joueur vote. Vérifie les votes manquants puis la majorité
	# TODO: Trouvez pourquoi il est call 2 fois d'affilée parfois
	async def check_vote_end(self):
		missing = False

		for player_id in self.order:
			player = self.players[player_id]

			if not len(player.last_vote):
				missing = True

		if not missing and self.phase == "team_selection":
			self.phase = "vote_for_team"

			for_votes = len([self.players[x] for x in self.order if self.players[x].last_vote == "for"])

			for player_id in self.order:
				player = self.players[player_id]

			# Change la couleur du message en fonction
			# await self.send_info(color = 0x00ff00 if for_votes > len(self.order)/2 else 0xff0000)

			if for_votes > len(self.order)/2:
				await self.send_players_quest_choice()

				# self.save({"type":"quest"})
			else:
				await self.send_info(
					info={
						"name": "Equipe refusée",
						"value": "Le prochain leader va proposer une nouvelle composition."
					})

				self.refused += 1

				if self.refused == 5:
					await self.end_game(False, "5 Equipes refusées")
				else:
					await self.next_turn()

	async def send_players_quest_choice(self):
		choices = []
		for id in self.team.values():
			for choice in self.players[id].quest_choices:
				if choice not in choices:
					choices.append(choice)

		async def cast_choice(button, interaction):
			last_choice = choices[button.index]
			self.players[interaction.user.id].last_choice = last_choice

			await interaction.respond(type=4, content="Vous avez choisi " + str(global_values.quest_choices["emojis"][last_choice]) + " " + global_values.quest_choices["names"][last_choice])
			await self.check_quest_end()

		components = [[]]
		for choice in choices:
			components[0].append({
				"effect": cast_choice,
				"cond": lambda i: i.user.id in self.team.values(),
				"label": global_values.quest_choices["names"][choice],
				"emoji": global_values.quest_choices["emojis"][choice],
				"style": global_values.quest_choices["styles"][choice]
			})

		await self.send_info(
			info={
				"name": "Equipe acceptée",
				"value": "Les membres vont partir en quête et décider de la faire réussir ou échouer."
			},
			components=components,
			color=0x2e64fe
		)

	async def check_quest_end(self):
		missing = False

		for player_id in self.team.values():
			player = self.players[player_id]

			if not len(player.last_choice):
				missing = True

		if not missing and self.phase == "vote_for_team":
			self.phase = "quest"

			for player_id in self.team.values():
				player = self.players[player_id]

				if player.vote_message:
					await player.vote_message.message.delete()

				if player.last_choice == "sabotage":
					for id in self.team.values():
						self.players[id].last_choice = "failure"

			self.played = [self.players[x].last_choice for x in self.team.values()]
			random.shuffle(self.played)

			cancelled = len([x for x in self.played if x == "cancel"])
			fails = len([x for x in self.played if x == "failure"])
			reverses = len([x for x in self.played if x == "reverse"])

			if not cancelled:
				success = fails < (2 if self.round == 3 and len(self.players) >= 7 and self.game_rules["4th_quest_two_failures"] else 1)
				if reverses == 1:
					success = not success

				self.quests[self.round] = -1 if success else 0

				await self.send_info(
					info={
						"name": ((str(global_values.quest_choices["emojis"]["success"]) + " Quête réussie " + str(global_values.quest_choices["emojis"]["success"])) if success else (str(global_values.quest_choices["emojis"]["failure"]) + " Quête échouée " + str(global_values.quest_choices["emojis"]["failure"]))),
						"value": "Choix : " + " ".join([str(global_values.quest_choices["emojis"][x]) for x in self.played])
					},
					color=0x76ee00 if success else 0xef223f)

				self.round += 1
				self.refused = 0

				if len([x for x in self.quests if x == 0]) == 3:
					await self.end_game(False, "3 Quêtes échouées")
				elif len([x for x in self.quests if x == -1]) == 3:
					if len([x for x in self.players.values() if x.role == "assassin"]):
						valid_candidates = [x for x in self.order if self.players[x].allegiance != "evil"]
						num_player_rows = math.ceil(len(valid_candidates)/5)

						async def kill(button, interaction):
							killed = self.players[valid_candidates[button.index]]

							if killed.role == "merlin":
								await self.end_game(False, "assassinat de Merlin (`" + str(killed.user) + "`)")
							elif killed.role == "elias":
								await self.end_game(global_values.visual_roles[killed.role], "usurpation (`" + str(killed.user) + "`)")
							else:
								await self.end_game(True, "3 Quêtes réussies (Assassinat de `" + str(killed.user) + "` qui était " + global_values.visual_roles[killed.role] + ")")

						await self.info_message.delete()
						components = []
						for y in range(num_player_rows):
							components.append([])
							for x in range(5):
								if 5 * y + x == len(valid_candidates):
									break

								components[len(components) - 1].append({
									"effect": kill,
									"cond": lambda i: i.user.id in self.players and self.players[i.user.id].role == "assassin",
									"label": str(self.players[valid_candidates[5 * y + x]].user),
									"style": 2
								})

						self.info_message = ComponentMessage(components)

						await self.info_message.send(
							self.channel,
							embed=discord.Embed(
								title="Assassinat",
								description="3 Quêtes ont été réussies. Les méchants vont maintenant délibérer sur quelle personne l'Assassin va tuer.\n**Que les gentils coupent leurs micros.**",
								color=global_values.color
							)
						)
					else:
						await self.end_game(True, "3 Quêtes réussies")
				else:
					await self.next_turn()
			else:
				for player_id in self.team.values():
					if "cancel" in self.players[player_id].quest_choices:
						self.players[player_id].quest_choices.remove("cancel")

				await self.send_info(
					info={
						"name": str(global_values.quest_choices["emojis"]["cancel"]) + " Quête annulée " + str(global_values.quest_choices["emojis"]["cancel"]),
						"value": "**Arthur a décidé d'annuler la quête.** Le prochain leader va proposer une nouvelle composition."
					}
				)

				self.refused += 1

				await self.next_turn()

	# Passe au prochain tour
	async def next_turn(self, message=None):
		if self.game_rules["lady_of_the_lake"] and self.round >= 2:
			lady = self.players[self.order[self.lady_of_the_lake]]

			valid_candidates = [x for i, x in enumerate(self.order) if x != lady.user.id]
			emojis = [global_values.number_emojis[self.order.index(x)] for x in valid_candidates]
			choices = ["`" + str(self.players[x].user) + "`" for x in valid_candidates]

			async def inspect(reactions):
				inspected = self.players[valid_candidates[reactions[lady.user.id][0]]]

				self.lady_of_the_lake = self.order.index(inspected.user.id)

				await lady_choice_message.message.edit(embed=discord.Embed(
					title="🔎 Inspection 🔎",
					description="L'allégeance de `" + str(inspected.user) + "` est " + ("🟦 Gentil" if inspected.allegiance == "good" else "🟥 Méchant" if inspected.allegiance == "evil" else "🟩 Solo"),
					color=global_values.color))

				await self.start_turn({
					"name": "🔎 Inspection 🔎",
					"value": "La Dame du Lac (`" + str(lady.user) + "`) a inspecté l'allégeance de `" + str(inspected.user) + "`"})

			async def cond(reactions):
				return len(reactions[self.order[self.lady_of_the_lake]]) == 1

			lady_choice_message = ReactionMessage(
				cond,
				inspect,
				temporary=False
			)

			await lady_choice_message.send(
				lady.user,
				"Choisissez qui vous souhaitez inspecter",
				"",
				0x2e64fe,
				choices,
				emojis=emojis
			)

			# self.save({"type":"next_turn"})
		else:
			await self.start_turn(message)

	# Fin de partie, envoies le message de fin et détruit la partie
	async def end_game(self, good_wins, cause):
		if good_wins is True:
			embed = discord.Embed(title="[AVALON] Victoire des Gentils 🟦 par " + cause + " !", color=0x2e64fe)
		elif good_wins is False:
			embed = discord.Embed(title="[AVALON] Victoire des Méchants 🟥 par " + cause + " !", color=0xef223f)
		else:
			embed = discord.Embed(title="[AVALON] Victoire " + ("d'" if good_wins[:1] in ["E", "A", "I", "O", "U", "Y"] else "de ") + good_wins + " par " + cause  + " !", color=0x76ee00)

		embed.description = "**Joueurs :**\n" + '\n'.join([global_values.number_emojis[i] + " `" + str(self.players[x].user) + "` : " + global_values.visual_roles[self.players[x].role] for i, x in enumerate(self.order)])

		await self.info_message.delete()

		await self.channel.send(embed=embed)
		self.delete_save()
		del global_values.games[self.channel.id]

	def serialize(self, state):
		object = {
			"channel": self.channel.id,
			"order": self.order,
			"turn": self.turn,
			"round": self.round,
			"team": self.team,
			"refused": self.refused,
			"quests": self.quests,
			"info_message": self.info_message.id if self.info_message else None,
			"played": self.played,
			"lady_of_the_lake": self.lady_of_the_lake,
			"roles": self.roles,
			"phase": self.phase,
			"gamerules": self.game_rules,
			"players": {},
			"state": state
		}

		for id, player in self.players.items():
			object["players"][id] = {
				"role": player.role,
				"last_vote": player.last_vote,
				"inspected": player.inspected,
				"quest_choices": player.quest_choices,
				"info_message": player.info_message.id if player.info_message else None,
				"user": player.user.id
			}

		return object

	async def deserialize(self, object, client):
		self.channel = client.get_channel(object["channel"])
		self.order = object["order"]
		self.turn = int(object["turn"])
		self.round = int(object["round"])
		self.quests = object["quests"]
		self.roles = object["roles"]
		self.phase = object["phase"]
		self.game_rules = object["gamerules"]
		self.refused = int(object["refused"])
		self.info_message = await self.channel.fetch_message(object["info_message"]) if object["info_message"] else None
		self.played = object["played"]
		self.lady_of_the_lake = object["lady_of_the_lake"]
		self.players = {}
		self.team = {}

		for i, id in object["team"].items():
			self.team[int(i)] = int(id)

		for id, info in object["players"].items():
			player = self.players[int(id)] = classes[info["role"]](client.get_user(info["user"]))
			player.last_vote = info["last_vote"]
			player.inspected = info["inspected"]
			player.quest_choices = info["quest_choices"]
			player.info_message = await player.user.fetch_message(info["info_message"]) if info["info_message"] else None

	def save(self, state):
		if self.mainclass.objects.save_exists("games"):
			object = self.mainclass.objects.load_object("games")
		else:
			object = {}

		object[self.channel.id] = self.serialize(state)
		self.mainclass.objects.save_object("games", object)

	def delete_save(self):
		if self.mainclass.objects.save_exists("games"):
			object = self.mainclass.objects.load_object("games")
			if str(self.channel.id) in object:
				object.pop(str(self.channel.id))

			self.mainclass.objects.save_object("games", object)
		else:
			print("no save")

 #  Module créé par Le Codex#9836
