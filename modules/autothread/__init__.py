import discord
import humanize
from time import time
from modules.base import BaseClassPython

class MainClass(BaseClassPython):
	name = "AutoThread"
	help = {
		"description": "Crée automatiquement un thread par message, en fonction du channel",
		"commands": {
			"{prefix}{command} enable": "Active la création automatique de threads dans le channel actuel (mode manuel par défaut)",
			"{prefix}{command} disable": "Désactive la création automatique de threads",
			"{prefix}{command} list": "Affiche la liste des salons enregistrés (avec la date du dernier nettoyage) dans le module",
			"{prefix}{command} clean": "Supprime tous les threads 'vides' (avec un seul message) du salon",
			"{prefix}{command} setclean": "Modifie le mode de nettoyage et sa périodicité. Argument: `manual | <period>` avec `<period>` un nombre entier de secondes supérieur ou égal à 60"
	}}

	def __init__(self, client):
		super().__init__(client)
		self.config["auth_everyone"] = False
		self.config["configured"] = True
		self.config["help_active"] = True
		self.config["command_text"] = "autothread"
		self.config["color"] = 0x840052 # Kernel's unique color
		
		self.ongoing_clean = False

		if self.objects.save_exists("athchannels_db"):
			self.athchannels = self.objects.load_object("athchannels_db")
		else:
			self.athchannels = dict()
	
	async def on_ready(self):
		pass
		
	async def on_message(self, message):
		await super().on_message(message)
		
		# Ignoring bot messages and commands
		if message.author.bot or message.content.startswith(self.client.config["prefix"]):
			return
			
		if str(message.channel.id) in self.athchannels:
			
			# Checks current time, compare it to the latest timestamp
			current_time = time()
			
			if self.athchannels[str(message.channel.id)]["clean_mode"] == "auto":
				# Automatic clean
				if current_time - self.athchannels[str(message.channel.id)]["lcts"] > self.athchannels[str(message.channel.id)]["clean_period"] and not self.ongoing_clean:
					self.ongoing_clean = True

					await message.channel.send("`autothread clean` | Nettoyage automatique démarré.")
					# "C'est en étant fainéant qu'on sauve la planète." ~ JDG Daemon Summoner
					await self.com_clean(message, list(), dict())

					self.ongoing_clean = False

			try:
				await message.create_thread(name=f"Thread {message.author.name}-{str(message.id)[-5:]}")
			except (ValueError, discord.HTTPException, discord.Forbidden) as e:
				# If something goes wrong, don't do anything
				return
	
	async def on_guild_channel_delete(self, channel):

		if str(channel.id) in self.athchannels:
			self.athchannels.pop(str(message.channel.id))
			self.saveATHChannels()
	
	async def com_enable(self, message, args, kwargs):
		if str(message.channel.id) not in self.athchannels:

			self.athchannels[str(message.channel.id)] = {"clean_mode" : "manual", "clean_period" : -1, "lcts" : 0}
			self.saveATHChannels()

			await message.channel.send("Salon ajouté.")
		else:
			await message.channel.send("Autothread est déjà actif dans ce salon.")

	async def com_disable(self, message, args, kwargs):
		if str(message.channel.id) in self.athchannels:
			
			self.athchannels.pop(str(message.channel.id))
			self.saveATHChannels()
			
			await message.channel.send("Salon retiré.")
		else:
			await message.channel.send("Le salon n'est pas enregistré dans Autothread.")
      
	async def com_list(self, message, args, kwargs):

		channel_list = ""
		for chan_id in self.athchannels:
			chan_entry = self.athchannels[chan_id]
			match chan_entry["clean_mode"]:
				case "manual":
					channel_list += "<#{0}> (mode manuel)\n".format(chan_id)
				case "auto":
					channel_list += "<#{0}> (mode auto, période: `{1}`, LCTS: <t:{2}:R>)\n".format(chan_id,
						humanize.time.precisedelta(chan_entry["clean_period"]),
						chan_entry["lcts"])
				case _:
					channel_list += "<#{0}> (mode inconnu)\n"

		await message.channel.send(f"`autothread` | **Salons enregistrés ({len(self.athchannels)})** \n" + channel_list)
	
	async def com_setclean(self, message, args, kwargs):
		if str(message.channel.id) in self.athchannels:

			if args[1] == "manual":
				self.athchannels[str(message.channel.id)] = {"clean_mode" : "manual", "clean_period" : -1, "lcts" : 0}
				self.saveATHChannels()
				await message.channel.send("`autothread` | Nettoyage automatique désactivé (mode manuel)")
				return

			else:
				try:
					new_period = int(args[1])
					if new_period < 60:
						raise ValueError

				except ValueError:
					await message.channel.send("L'argument spécifié n'est pas un nombre supérieur ou égal à 60 (ou `manual`)")
					return

				else:
					self.athchannels[str(message.channel.id)] = {"clean_mode" : "auto", "clean_period" : new_period, "lcts" : int(time())}
					self.saveATHChannels()

					await message.channel.send(f"`autothread` | Nouvelle période de nettoyage automatique : `{humanize.time.precisedelta(new_period)}`")

		else:
			await message.channel.send("Le salon n'est pas enregistré dans Autothread.")

	async def com_clean(self, message, args, kwargs):

		if str(message.channel.id) in self.athchannels:
			async with message.channel.typing():
				deleted_threads = 0
				current_threads = message.channel.threads
				for thread in current_threads:
					# Deleting threads only if they have one message
					messages = [msg async for msg in thread.history(limit=5)]

					if not len(messages) >= 2:
						deleted_threads += 1
						await thread.delete()

				# Updating LCTS for current channel
				self.athchannels[str(message.channel.id)]["lcts"] = int(time())
				self.saveATHChannels()
				await message.channel.send(f"`autothread clean` | Threads supprimés : {deleted_threads}")
		else:
			await message.channel.send("Le salon n'est pas enregistré dans Autothread.")

	def saveATHChannels(self):
		self.objects.save_object("athchannels_db", self.athchannels)
