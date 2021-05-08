# Module Kersig-JDPI pour Alset Alokin.
# Code original : (c) Kernel, hébergé sur kersig
# Portage sur Alset Alokin : Kernel, via le modèle de module élaboré par Le Codex
#Note : ce module ne peut être activé que si les fichiers binaires initiaux 
#se trouvent dans le même répertoire que le script. Ces fichiers doivent être générés 
#au moyen du script original.

import os
import pickle
import discord
from random import shuffle
from modules.base import BaseClassPython

KERNEL_ID = 689010001137893458
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split('')

def load_game():

	players_file_exists = os.path.exists("./jdpi_playerfile")
	tracks_file_exists = os.path.exists("./jdpi_tracksfile")
	contributors_file_exists = os.path.exists("./jdpi_contributorsfile")
	couple_file_exists = os.path.exists("./jdpi_couplefile")

	if players_file_exists and tracks_file_exists and contributors_file_exists and couple_file_exists:
		with open('jdpi_playerfile', 'rb') as file:
			depick = pickle.Unpickler(file)
			jdpi_players = depick.load()

		with open('jdpi_tracksfile', 'rb') as file:
			depick = pickle.Unpickler(file)
			jdpi_tracks = depick.load()

		with open('jdpi_contributorsfile', 'rb') as file:
			depick = pickle.Unpickler(file)
			jdpi_contributors = depick.load()

		with open('jdpi_couplefile', 'rb') as file:
			depick = pickle.Unpickler(file)
			jdpi_couples = depick.load()

	else:
		raise FileNotFoundError("Un (ou plusieurs) fichier(s) manque(nt) à l'appel.")

	return jdpi_players,jdpi_tracks,jdpi_contributors,jdpi_couples

class JDPIPlayer():
	"""Classe codant chaque joueur."""

	def __init__(self,userid,name,discordhash):

		self.USER_ID = userid
		self.USER_NAME = '{}#{}'.format(name,discordhash)

		self.remaining_tries = 5
		self.corrected_tries_remaining = 3
		self.try_number = 0
		self.tries_summary = [None for i in range(self.remaining_tries)]
		self.corrected_tries_summary = [None for i in range(self.corrected_tries_remaining)]

		self.score = 0

	def __repr__(self):
		return "<JDPI Player Object, user={}, RT={}, CTR={}, ID={}>".format(self.USER_NAME,self.remaining_tries,self.corrected_tries_remaining,self.USER_ID)

class Void():
	"""Classe représentant l'objet vide."""
	pass

#Contient la liste des joueurs actifs, stockés sur la forme d'un objet JDPIPlayer, s'appuyant sur les attributs 
#fournis par l'objet User renvoyé par message.author:
# id - numéro d'identification
# name - pseudo discord
# discriminator - hash discord
# bot - booléen indiquant s'il s'agit d'un bot.

jdpi_players,jdpi_tracks,jdpi_contributors,jdpi_couples = load_game()
#print(loaded_game)
jdpi_total_tries = 5
jdpi_corrected_tries = 3

#Construction de la chaîne correspondant à  la combinaison gagnante
jdpi_match = ""
for i in range(len(jdpi_contributors)):
	singlematch = "{}-".format(ALPHABET[i])
	singlematch += str(jdpi_tracks.index([(jdpi_contributors[i],t) for t in jdpi_tracks if (jdpi_contributors[i],t) in jdpi_couples][0][1])+1)
	if i != len(jdpi_contributors)-1:
		jdpi_match += singlematch+','
	else:
		jdpi_match += singlematch

jdpi_components = jdpi_match.split(',')


class MainClass(BaseClassPython):
	name = "Jeu des pistes improbables"
	help = {
		"description": "Crée une partie du jeu des pistes improbables",
		"commands": {
			"{prefix}{command} join": "Rejoindre la partie si vous n'y êtes pas déjà.",
			"{prefix}{command} items": "Affiche la liste des musiques et participants.",
			"{prefix}{command} summary": "Résumé de vos essais",
			"{prefix}{command} submit <combinaison>": "Soumettre une combinaison (envoyez `%jdpi submit` pour voir les instructions de formattage)",
			#Commandes supplémentaires réservées :
			# %jdpi rankings : afficher les classements
		}
	}
	games = {}
	members = {}

	def __init__(self, client):
		super().__init__(client)
		self.config["auth_everyone"] = True
		self.config["configured"] = True
		self.config["help_active"] = True
		self.config["command_text"] = "jdpi"
		self.config["color"] = 0x00b3b3

	async def on_ready(self):
		pass

	async def com_items(self,message):
		"""Affiche la liste des participants et des sons"""

		music_field = ""

		for i in range(len(jdpi_tracks)):
			music_field += "{}) {}\n".format(i+1,jdpi_tracks[i])

		contributors_list = ""
		for i in range(len(jdpi_contributors)):
			contributors_list += "{}) `{}`\n".format(ALPHABET[i],jdpi_contributors[i])

		embed = discord.Embed(title="Jeu des pistes improbables - Liste des pistes/participants",color=0x00b3b3)
		embed.add_field(name="Participants",value=contributors_list)
		embed.add_field(name="Pistes", value=music_field)
		await message.channel.send(embed=embed)

	def jdpi_ingame_check(returnp=False):
		"""Vérifie si le joueur est dans la partie (ou pas)"""

		if not jdpi_players:
			found = False
			playerobj = Void()
		else:
			for p in jdpi_players:
				if p.USER_ID == message.author.id:
					playerobj = p
					found = True
					break
				else:
					found = False

		if not returnp:
			return found
		else:
			return (found,playerobj)

	async def com_join(self,message,args):
		"""Fonction permettant de rejoindre une partie."""

		found = jdpi_ingame_check()

		if found:
			embed = discord.Embed(title="Jeu des pistes improbables - Erreur",color=0xff0000)
			embed.add_field(name="Vous êtes déjà dans la partie",value="Allez jouer plutôt que de me solliciter inutilement ! :angry:")
			await message.channel.send(embed=embed)
		else:
			jdpi_players.append(JDPIPlayer(message.author.id,message.author.name,message.author.discriminator))
			print(jdpi_players)
			embed = discord.Embed(title="Jeu des pistes improbables",color=0x00b3b3)
			embed.add_field(name="Vous avez rejoint la partie.",value='Bonne chance !')
			await message.author.send(embed=embed)

	async def com_summary(self,message,args):
		"""Affiche le résumé d'un joueur."""

		found,player = jdpi_ingame_check(returnp=True)

		if not found:
			embed = discord.Embed(title="Jeu des pistes improbables - Erreur",color=0xff0000)
			embed.add_field(name="Vous n'êtes pas dans la partie",value='-_-')
			await message.channel.send(embed=embed)

		else:
			NA_display = lambda x: "n/d." if x == None else x
			summary_part1 = "`{}` | Meilleur score : `{}` | Essais restants : `{}` | Corrections restantes : `{}`".format(player.USER_NAME,player.score,player.remaining_tries,player.corrected_tries_remaining)
			summary_part2 = "**Essais :**\n"
			for i in range(jdpi_total_tries):
				summary_part2 += "n°{} : `{}`\n".format(i+1,NA_display(player.tries_summary[i]))

			summary_part3 = "**Essais corrigés :**\n"
			for i in range(jdpi_corrected_tries):
				summary_part3 += "n°{} : `{}`\n".format(i+1,NA_display(player.corrected_tries_summary[i]))
			summary_part3 += "`x` : correct | `-` : incorrect"

			embed = discord.Embed(title="Jeu des pistes improbables - Résumé",color=0x00b3b3)
			embed.add_field(name="Progression actuelle", value=summary_part1, inline=False)
			embed.add_field(name="Détail des essais",value=summary_part2+summary_part3,inline=False)

			await message.author.send(embed=embed)

	def jdpi_check_subformat(s):
		"""Fonction de vérification des combinaisons."""

		components = s.split(",")

		if len(components) != len(jdpi_components): #Test de longueur (il y a bien toutes les associations)
			return False

		try:
			for comp in components: #Test de chaque association (1 lettre + 1 entier)
				couple = comp.split("-")
				assert couple[0].isalpha()
				assert couple[1].isnumeric()

		except AssertionError:
			return False
		else:
			return True

	def jdpi_correction(comp_list:list):
		"""Fonction de correction"""

		correction_string = ""
		attempt_score = 0

		for i in range(len(comp_list)):
			if comp_list[i] == jdpi_components[i]:
				correction_string += 'x'
				attempt_score += 1
			else:
				correction_string += '-'

			if i != len(comp_list)-1:
				correction_string += '/'
			else:
				pass

		return correction_string,attempt_score

	def jdpi_player_update(p,score:int,attempt:str,corattempt:bool,correction:str):
		"""Le principe d'encapsulaquoi ? Je l'ai envoyé se faire foutre, tout simplement :)"""
		
		p.score = max(p.score,score)
		p.remaining_tries -= 1
		if corattempt:
			p.corrected_tries_remaining -= 1
			p.corrected_tries_summary[p.try_number] = correction

		p.tries_summary[p.try_number] = attempt
		p.try_number += 1

	def jdpi_backup():
		"""Sauvegarde des données du jeu (oui, je n'utilise pas de .json)."""

		with open('jdpi_playerfile','wb') as file:
			pick = pickle.Pickler(file)
			pick.dump(jdpi_players)

		with open('jdpi_tracksfile','wb') as file:
			pick = pickle.Pickler(file)
			pick.dump(jdpi_tracks)

		with open('jdpi_contributorsfile','wb') as file:
			pick = pickle.Pickler(file)
			pick.dump(jdpi_contributors)

		with open('jdpi_couplefile','wb') as file:
			pick = pickle.Pickler(file)
			pick.dump(jdpi_couples)


	async def com_submit(self, message, args):
		"""Commande de soumission de la combinaison."""

		c = args[1] if len(args) == 2 else ''

		found,player = jdpi_ingame_check(returnp=True)

		# Toujours pour les tests
		# print(c)

		if not found:
			embed = discord.Embed(title="Jeu des pistes improbables - Erreur",color=0xff0000)
			embed.add_field(name="Vous n'êtes pas dans la partie",value="-_-")
			await message.channel.send(embed=embed)

		elif c == '' or c == 'help':
			format_instructions = """
			...mais dans ce cas, il est bon de rappeler le formattage des combinaisons soumises :
			`A-1,B-2,C-3,B-4,...,Z-26`
			**~** Chaque association doit être composée **d'une lettre majuscule suivie d'un tiret et d'un entier.**
			**~** Deux associations sont séparées **d'une virgule, sans espaces.**
			**~** La combinaison **doit suivre l'ordre alphabétique** (sinon le bot comptera faux).
			**~** La combinaison est soumise **sans confirmation**, réfléchissez donc bien avant de presser la touche entrée.
			"""
			embed = discord.Embed(title="Jeu des pistes improbables - Soumettre une combinaison",color=0x0000aa)
			embed.add_field(name="Vous n'avez pas envoyé de combinaison (ou vous vous êtes trompé)...",value=format_instructions)
			await message.author.send(embed=embed)

		else:
			correctformat = jdpi_check_subformat(c)
			# print(correctformat)

			if not correctformat:
				embed = discord.Embed(title="Jeu des pistes improbables - Soumettre une combinaison",color=0xff0000)
				embed.add_field(name="La combinaison n'est au bon format ! :rage:",value="Tapez `/jdpi submit` pour (re)voir le format demandé...")
				await message.author.send(embed=embed)

			elif player.remaining_tries == 0:
				embed = discord.Embed(title="Jeu des pistes improbables - Soumettre une combinaison",color=0xfd9622)
				embed.add_field(name="Désolé...",value="Vous n'avez plus d'essais disponibles.\n Votre score final est de `{}` points.".format(player.score))
				await message.author.send(embed=embed)

			elif player.remaining_tries != 0:

				components = c.split(',')
				corstr,attscore = jdpi_correction(components)
				
				jdpi_player_update(player,attscore,c,bool(player.corrected_tries_remaining),corstr)
				jdpi_backup()

				embed = discord.Embed(title="Jeu des pistes improbables - Soumettre une combinaison",color=0x00aa00)
				embed.add_field(name="Votre combinaison a été acceptée ! :white_check_mark:",value="Il vous reste `{}` essai(s), dont `{}` corrigé(s).\n Vous pouvez voir le détail de vos essais avec `\jdpi summary`".format(player.remaining_tries,player.corrected_tries_remaining),inline=False)
				if bool(player.corrected_tries_remaining):
					embed.add_field(name="Correction de la combinaison", value="`x` : correct | `-`: incorrect\n `{}`".format(corstr),inline=False)

				await message.author.send(embed=embed)

	async def com_rankings(self,message,args):
		"""Commande qui m'est réservée pour l'affichage du classement. 
		(oui, je sais, c'est injuste, mais c'est comme ça, et puis, un peu de suspense, ça ne fait pas de mal x))"""

		if message.author.id != KERNEL_ID:
			embed = discord.Embed(title="Jeu des pistes improbables",color=0xff0000)
			embed.add_field(name="Je ne sais pas d'où vous connaissez l'existence de cette commande...",value="...mais si vous pensiez accéder aux classements, eh bien...")
			embed.set_image(url="https://media1.tenor.com/images/7238d0e792e0f485b636a0b5ca93f2c7/tenor.gif?itemid=14030913")
			await message.channel.send(embed=embed)

		elif not jdpi_players:
			embed = discord.Embed(title="Jeu des pistes improbables",color=0x0000ff)
			embed.add_field(name="Alors en fait...",value="...y a pas de joueurs pour le moment.")
			await message.channel.send(embed=embed)
			
		else:
			embed = discord.Embed(title="Jeu des pistes improbables",color=0x00b3b3)
			ranking = ""
			suffix = lambda x: "e" if x != 1 else "er"
			sorted_players_list = jdpi_players.copy()
			sorted_players_list.sort(key=lambda p:p.score,reverse=True)

			for i in range(len(sorted_players_list)):
				ranking += "{}{} : `{}` - `{}` point(s))\n".format(i+1,suffix(i+1),sorted_players_list[i].USER_NAME,sorted_players_list[i].score)

			embed.add_field(name="Classement",value=ranking)
			await message.author.send(embed=embed)
