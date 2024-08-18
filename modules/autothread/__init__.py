import discord
from time import time, gmtime, strftime
from modules.base import BaseClassPython

class MainClass(BaseClassPython):
	name = "AutoThread"
	help = {
		"description": "Crée automatiquement un thread par message, en fonction du channel",
		"commands": {
			"{prefix}{command} enable": "Active la création automatique de threads dans le channel actuel",
			"{prefix}{command} disable": "Désactive la création automatique de threads",
			"{prefix}{command} list": "Affiche la liste des salons enregistrés (avec la date du dernier nettoyage) dans le module",
			"{prefix}{command} clean": "Supprime tous les threads 'vides' (avec un seul message) du salon"
	}}
	
	active_channels = []

	def __init__(self, client):
		super().__init__(client)
		self.config["auth_everyone"] = False
		self.config["configured"] = True
		self.config["help_active"] = True
		self.config["command_text"] = "autothread"
		self.config["color"] = 0x840052 # Kernel's unique color
		
		self.ongoing_clean = False
		
		if self.objects.save_exists("active_channels"):
			self.active_channels = self.objects.load_object("active_channels")
		
		
		if self.objects.save_exists("lcts_db"):
			# LCTS_db: Last Clean TimeStamp database
			self.lcts_db = self.objects.load_object("lcts_db")
		else:
			self.lcts_db = dict()
	
	async def on_ready(self):
		
		# Initialize LCTS_db if it is not already loaded
		# with current time for all active channels
		if len(self.lcts_db) == 0:
			for chan_id in self.active_channels:
				self.lcts_db[chan_id] = time()
				
			self.saveLCTS()
			
		
	async def on_message(self, message):
		await super().on_message(message)
		
		# Ignoring bot messages and commands
		if message.author.bot or message.content.startswith(self.client.config["prefix"]):
			return
			
		if str(message.channel.id) in self.active_channels:
			
			# Checks current time, compare it to the latest timestamp
			current_time = time()
			
			# Weekly automatic clean
			if current_time - self.lcts_db[str(message.channel.id)] > 86400*7 and not self.ongoing_clean:
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
		if str(channel.id) in self.active_channels:
			self.active_channels.remove(str(channel.id))
			self.saveChannels()
			
			self.lcts_db.pop(str(channel.id))
			self.saveLCTS()
	
	async def com_enable(self, message, args, kwargs):
		if str(message.channel.id) not in self.active_channels:
		
			# Adding the channel to active channels and LCTS-db
			self.active_channels.append(str(message.channel.id))
			self.saveChannels()
			
			self.lcts_db[str(message.channel.id)] = time()
			self.saveLCTS()
			
			await message.channel.send("Salon ajouté.")
		else:
			await message.channel.send("Autothread est déjà actif dans ce salon.")
			
	async def com_disable(self, message, args, kwargs):
		if str(message.channel.id) in self.active_channels:
			
			# Removing the channel from active channels and LCTS-db
			self.active_channels.remove(str(message.channel.id))
			self.saveChannels()
			
			self.lcts_db.pop(str(message.channel.id))
			self.saveLCTS()
			
			await message.channel.send("Salon retiré.")
		else:
			await message.channel.send("Le salon n'est pas enregistré dans Autothread.")
	
	async def com_list(self, message, args, kwargs):
		
		channel_list = ""
		for chan_id in self.active_channels:
			channel_list += "<#{0}> (LCTS: {1})\n".format(chan_id, strftime("%d-%m-%Y %H:%M:%S", gmtime(self.lcts_db[chan_id])))
			
		await message.channel.send(f"`autothread` | **Salons enregistrés ({len(self.active_channels)})** \n" + channel_list)
	
	async def com_clean(self, message, args, kwargs):
		
		if str(message.channel.id) in self.active_channels:
			async with message.channel.typing():
				deleted_threads = 0
				current_threads = message.channel.threads
				for thread in current_threads:
					# Deleting threads only if they have one message
					try:
						messages = [msg async for msg in thread.history(limit=5)]
					except (discord.Forbidden, discord.HTTPException) as e:
						await message.channel.send(f"`autothread clean` | Une erreur a été capturée :\n ```{e}```")
					else:
						if not len(messages) >= 2:
							deleted_threads += 1
							await thread.delete()
				
				# Updating LCTS for current channel
				self.lcts_db[str(message.channel.id)] = time()
				self.saveLCTS()
				await message.channel.send(f"`autothread clean` | Threads supprimés : {deleted_threads}")
		else:
			await message.channel.send("Le salon n'est pas enregistré dans Autothread.")
		

	def saveChannels(self):
		self.objects.save_object("active_channels", self.active_channels)
	
	def saveLCTS(self):
		self.objects.save_object("lcts_db", self.lcts_db)
	
