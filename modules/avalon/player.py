import discord
import random

from modules.reaction_message.reaction_message import ReactionMessage

import modules.avalon.globals as global_values


class Player:
	role = ""
	last_vote = ""
	last_choice = ""
	inspected = False
	vote_message = None
	info_message = None
	quest_choices = ["success", "failure"]

	def __init__(self, game, user):
		self.game = game
		self.user = user

	async def game_start(self):
		await self.post_game_start()

	async def send_role_info(self, interaction):
		await self.team_game_start()

		# blaise = [x for x in self.game.players if x.role == "blaise"]
		# if len(blaise):
		#	 self.embed.add_field(name = "Père Blaise",
		#	   value = "`" + str(blaise[0].user) + "``")

		await interaction.respond(type=4, embed=self.embed)

	async def post_game_start(self):
		pass

	async def send_choice(self):
		async def cast_choice(reactions):
			self.last_choice = self.quest_choices[reactions[self.user.id][0]]
			await self.game.check_quest_end()

		async def cond_player(reactions):
			return len(reactions[self.user.id]) == 1

		self.vote_message = ReactionMessage(
			cond_player,
			cast_choice,
			temporary=False
		)

		await self.vote_message.send(
			self.user,
			"Quête",
			"Êtes-vous pour la réussite de la Quête?",
			global_values.color,
			[str(global_values.quest_choices["names"][x]) for x in self.quest_choices],
			validation_emoji="⭕",
			silent=True,
			emojis=[global_values.quest_choices["emojis"][x] for x in self.quest_choices]
		)

## GOOD TEAM ##

class Good(Player):
	allegiance = "good"
	role = "good"
	color = 0x2e64fe

	async def team_game_start(self):
		await self._game_start()

		galaad = [global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "`" for i, x in enumerate(self.game.order) if self.game.players[x].role in ["galaad", "accolon"]]
		if len(galaad):
			self.embed.add_field(
				name="🙋 Galaad",
				value='\n'.join(galaad))

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🟦",
			description="Vous êtes un Fidèle Vassal d'Arthur (Gentil). Vous devez faire réussir 3 Quêtes.",
			color=self.color)


class Merlin(Good):
	role = "merlin"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🧙‍♂️",
			description="Vous êtes Merlin. Vous devez faire réussir 3 Quêtes et ne pas vous révéler. Vous connaissez les méchants.",
			color=self.color)

		evils = [global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "`" for i, x in enumerate(self.game.order) if self.game.players[x].allegiance == "evil" and self.game.players[x].role != "mordred" or self.game.players[x].role == "karadoc"]
		if len(evils):
			self.embed.add_field(
				name="Vos ennemis :",
				value='\n'.join(evils))


class Percival(Good):
	role = "percival"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🤴",
			description="Vous êtes Perceval. Vous devez faire réussir 3 Quêtes et protéger Merlin. Vous connaissez Merlin et Morgane.",
			color=self.color)

		mages = [global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "`" for i, x in enumerate(self.game.order) if self.game.players[x].role in ["merlin", "morgane"]]
		if len(mages):
			self.embed.add_field(
				name="Les mages :",
				value='\n'.join(mages))


class Gawain(Good):
	role = "gawain"
	quest_choices = ["success", "reverse"]

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle ️🛡️",
			description="Vous êtes Gauvain. Vous devez faire réussir 3 Quêtes. Vous avez la possibilité d'inverser le résultat de la Quête si vous êtes dedans.",
			color=self.color)


class Karadoc(Good):
	role = "karadoc"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle ️🥴",
			description="Vous êtes Karadoc. Vous devez faire réussir 3 Quêtes et protéger Merlin. Merlin vous voit comme un méchant.",
			color=self.color)


class Galaad(Good):
	role = "galaad"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle ️🙋",
			description="Vous êtes Galaad. Vous devez faire réussir 3 Quêtes. Les gentils vous connaissent.",
			color=self.color)


class Uther(Good):
	role = "uther"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle ️👨‍🦳",
			description="Vous êtes Uther. Vous devez faire réussir 3 Quêtes. Vous pouvez choisir un joueur dont vous connaîtrez le rôle.",
			color=self.color)

	async def post_game_start(self):
		valid_candidates = [x for x in self.game.order if x != self.user.id]
		emojis = [global_values.number_emojis[self.game.order.index(x)] for x in valid_candidates]
		choices = ["`" + str(self.game.players[x].user) + "`" for x in valid_candidates]

		async def inspect_role(reactions):
			inspected = self.game.players[valid_candidates[reactions[self.user.id][0]]]
			if self.game.game_rules["uther_learns_role"]:
				information = global_values.visual_roles[inspected.role]
			else:
				information = ("🟦 Gentil" if inspected.allegiance == "good" else "🟥 Méchant" if inspected.allegiance == "evil" else "🟩 Solo")

			await inspection_message.message.edit(embed=discord.Embed(
				title="🔍 Inspection",
				description="Vous avez inspecté `" + str(inspected.user) + "` qui se révèle être " + information,
				color=global_values.color))

		async def cond(reactions):
			return len(reactions[self.user.id]) == 1

		inspection_message = ReactionMessage(
			cond,
			inspect_role,
			temporary=False
		)

		await inspection_message.send(
			self.user,
			"Choisissez le joueur que vous souhaitez inspecter",
			"",
			global_values.color,
			choices,
			emoji=emojis
		)

class Arthur(Good):
	role = "arthur"
	quest_choices = ["success", "failure", "cancel"]

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 👑",
			description="Vous êtes Arthur. Vous devez faire réussir 3 Quêtes. Vous avez la possibilité d'annuler la Quête si vous êtes dedans.",
			color=self.color)


class Vortigern(Good):
	role = "vortigern"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 👴",
			description="Vous êtes Vortigern. Vous devez faire réussir 3 Quêtes. Vous pouvez choisir un joueur à qui vous allez vous révéler.",
			color=self.color)

	async def post_game_start(self):
		valid_candidates = [x for x in self.game.order if x != self.user.id]
		emojis = [global_values.number_emojis[self.game.order.index(x)] for x in valid_candidates]
		choices = ["`" + str(self.game.players[x].user) + "`" for x in valid_candidates]

		async def reveal_self(reactions):
			got_revelation = self.game.players[valid_candidates[reactions[self.user.id][0]]]

			await revelation_message.message.edit(embed=discord.Embed(
				title="📨 Révélation 📨",
				description="Vous vous êtes révélé à `" + str(got_revelation.user) + "`",
				color=global_values.color))

			await got_revelation.user.send(embed=discord.Embed(
				title="📨 Révélation 📨",
				description="`" + str(self.user) + "` s'est révélé à vous comme étant Vortigern",
				color=global_values.color))

		async def cond(reactions):
			return len(reactions[self.user.id]) == 1

		revelation_message = ReactionMessage(
			cond,
			reveal_self,
			temporary=False
		)

		await revelation_message.send(
			self.user,
			"Choisissez le joueur à qui vous voulez vous révéler",
			"",
			global_values.color,
			choices,
			emoji=emojis
		)


# class Blaise(Good):
#	 role = "blaise"
#
#	 async def _game_start(self):
#		 self.embed = discord.Embed(title = "Rôle ️✍️",
#			 description = "Vous êtes Blaise. Vous devez faire réussir 3 Quêtes. Tout le monde vous connait, et vousne pouvez pas être dans une Quête. A chaque Quête, vous connaissez le choix d'une personne au choix.",
#			 color = self.color
#		 )


## EVIL TEAM ##

class Evil(Player):
	allegiance = "evil"
	role = "evil"
	evils = []
	color = 0xef223f

	async def team_game_start(self):
		await self._game_start()

		evils = [global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "`" for i, x in enumerate(self.game.order) if self.game.players[x].allegiance == "evil" and self.game.players[x].role != "oberon"]
		if len(evils):
			self.embed.add_field(
				name="Vos co-équipiers :",
				value='\n'.join(evils))

		if self.game.game_rules["evil_know_lancelot"]:
			lancelot = [global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "`" for i, x in enumerate(self.game.order) if self.game.players[x].role == "lancelot"]
			if len(lancelot):
				self.embed.add_field(
					name="Lancelot ⚔️️",
					value='\n'.join(lancelot))

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🟥",
			description="Vous êtes un Serviteur de Mordred (Méchant). Vous devez faire échouer 3 Quêtes.",
			color=self.color)


class Assassin(Evil):
	role = "assassin"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🗡️",
			description="Vous êtes l'Assassin. Vous devez faire échouer 3 Quêtes ou trouver Merlin et l'assassiner.",
			color=self.color)


class Morgane(Evil):
	role = "morgane"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🧙‍♀️",
			description="Vous êtes Morgane. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Vous apparaissez aux yeux de Perceval.",
			color=self.color)


class Mordred(Evil):
	role = "mordred"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 😈",
			description="Vous êtes Mordred. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Merlin ne vous connait pas.",
			color=self.color)


class Oberon(Evil):
	role = "oberon"

	async def team_game_start(self):
		await self._game_start()

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 😶",
			description="Vous êtes Oberon. Vous devez faire échouer 3 Quêtes. Vous ne connaissez pas les méchants et les méchants ne vous connaisent pas.",
			color=self.color)


class Lancelot(Evil):
	role = "lancelot"
	quest_choices = ["success", "reverse"]

	async def team_game_start(self):
		await self._game_start()

		if self.game.game_rules["lancelot_know_evil"]:
			evils = [global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "`" for i, x in enumerate(self.game.order) if self.game.players[x].allegiance == "evil" and self.game.players[x].role != "oberon" and self.game.players[x].user.id != self.user.id]
			if len(evils):
				self.embed.add_field(
					name="Un de vos co-équipiers :",
					value=random.choice(evils))

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle ⚔️️",
			description="Vous êtes Lancelot. Vous devez faire échouer 3 Quêtes. Vous avez la possibilité d'inverser le résultat de la Quête si vous êtes dedans. Vous ne connaissez uniquement un méchant aléatoire mais les méchants vous connaisent en tant que Lancelot.",
			color=self.color)


class Accolon(Evil):
	role = "accolon"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🤘",
			description="Vous êtes Accolon. Vous devez faire échouer 3 Quêtes. Les gentils vous voient aux côtés de Galaad.",
			color=self.color)


class Kay(Evil):
	role = "kay"
	quest_choices = ["success", "failure", "sabotage"]

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🧐",
			description="Vous êtes Sir Kay. Vous devez faire échouer 3 Quêtes. Vous aves la possibilité de changer tous les choix de la Quête en Echec si vous êtes dedans.",
			color=self.color)


class Agravain(Evil):
	role = "agravain"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🔮",
			description="Vous êtes Agravain. Vous devez faire échouer 3 Quêtes. Vous connaissez les rôles de vos co-équipiers.",
			color=self.color)

		self.embed.add_field(
			name="Rôles",
			value='\n'.join([global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "` : " + global_values.visual_roles[self.game.players[x].role] for i, x in enumerate(self.game.order) if self.game.players[x].allegiance == "evil" and (not self.game.players[x].role == "oberon" or self.game.game_rules["agravain_know_oberon"])]))


class Solo(Player):
	allegiance = "solo"
	color = 0x76ee00

	async def team_game_start(self):
		await self._game_start()


class Elias(Solo):
	role = "elias"

	async def _game_start(self):
		self.embed = discord.Embed(
			title="Rôle 🧙",
			description="Vous êtes Elias. Vous devez vous faire assassiner pour prendre la place de Merlin. Vous connaissez Merlin.",
			color=self.color
		)

		merlin = [global_values.number_emojis[i] + " `" + str(self.game.players[x].user) + "`" for i, x in enumerate(self.game.order) if self.game.players[x].role == "merlin"]
		if len(merlin):
			self.embed.add_field(
				name="Merlin :",
				value=random.choice(merlin))
