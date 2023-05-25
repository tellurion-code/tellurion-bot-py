import discord
from modules.base import BaseClassPython

class MainClass(BaseClassPython):
	name = "AutoThread"
	help = {
		"description": "Crée automatiquement un thread par message, en fonction du channel",
		"commands": {
			"{prefix}{command} enable": "Active la création automatique de threads dans le channel actuel",
			"{prefix}{command} disable": "Désactive la création automatique de threads",
			"{prefix}{command} list": "Affiche la liste des salons enregistrés dans le module",
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
		
		if self.objects.save_exists("active_channels"):
			self.active_channels = self.objects.load_object("active_channels")
	
	async def on_ready(self):
		# TODO: support Alset disruptions...
		pass
		
	async def on_message(self, message):
		await super().on_message(message)
		
		# Ignoring bot messages and commands
		if message.author.bot or message.content.startswith(self.client.config["prefix"]):
			return
			
		if str(message.channel.id) in self.active_channels:
			await message.create_thread(name=f"Thread {message.author.name}-{str(message.id)[-5:]}")
	
	async def on_guild_channel_delete(self, channel):
		if str(channel.id) in self.active_channels:
			self.active_channels.remove(str(channel.id))
	
	async def com_enable(self, message, args, kwargs):
		if str(message.channel.id) not in self.active_channels:
			self.active_channels.append(str(message.channel.id))
			self.saveChannels()
			await message.channel.send("Salon ajouté.")
		else:
			await message.channel.send("AutoThread est déjà actif dans ce salon.")
			
	async def com_disable(self, message, args, kwargs):
		if str(message.channel.id) in self.active_channels:
			self.active_channels.remove(str(message.channel.id))
			self.saveChannels()
			await message.channel.send("Salon retiré.")
		else:
			await message.channel.send("Le salon n'est pas enregistré dans AutoThread.")
	
	async def com_list(self, message, args, kwargs):
		
		channel_list = ""
		for chan_id in self.active_channels:
			channel_list += "<#{0}>\n".format(chan_id)
			
		await message.channel.send(f"`autothread` | **Salons enregistrés ({len(self.active_channels)})** \n" + channel_list)
	
	async def com_clean(self, message, args, kwargs):
		# Possible evolution : automatically clean all channels on a regular basis
		
		if str(message.channel.id) in self.active_channels:
			deleted_threads = 0
			for thread in message.channel.threads:
				# Deleting threads only if they have one message
				messages = [msg async for msg in thread.history(limit=5)]
				if not len(messages) >= 2:
					deleted_threads += 1
					await thread.delete()
					
			await message.channel.send(f"`autothread clean` | Threads supprimés : {deleted_threads}")
		else:
			await message.channel.send("Le salon n'est pas enregistré dans AutoThread.")
		

	def saveChannels(self):
		self.objects.save_object("active_channels", self.active_channels)
	
