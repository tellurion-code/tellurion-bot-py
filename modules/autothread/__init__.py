import discord
from modules.base import BaseClassPython
from random import randrange

class MainClass(BaseClassPython):
	name = "AutoThread"
	help = {
		"description": "Crée automatiquement un thread par message, en fonction du channel",
		"commands": {
			"{prefix}{command} enable": "Active la création automatique de threads dans le channel actuel",
			"{prefix}{command} disable": "Désactive la création automatique de threads",
			"{prefix}{command} list": "Affiche la liste des channels actifs (debug)"
	}}
	active_channels = []

	def __init__(self, client):
		super().__init__(client)
		self.config["auth_everyone"] = True
		self.config["authorized_roles"] = []
		self.config["configured"] = True
		self.config["help_active"] = True
		self.config["command_text"] = "autothread"
		self.config["color"] = 0x57ab1e
		
	async def on_ready(self):
		#if self.objects.save_exists("active_channels"):
		#	self.active_channels = self.objects.load_object("active_channels")
		pass
	
	async def on_message(self, message):
		await super().on_message(message)
		if message.author.bot or message.content.startswith(self.client.config["prefix"]):
			# print("autothread: ignoring command/bot message")
			return
		if str(message.channel.id) in self.active_channels:
			await message.create_thread(name=f"Thread {message.author.name}-{randrange(18072)}")
	
	async def com_enable(self, message, args, kwargs):
		if str(message.channel.id) not in self.active_channels:
			self.active_channels.append(str(message.channel.id))
			#self.save_channels()
			await message.channel.send("Salon ajouté.")
		else:
			await message.channel.send("AutoThread est déjà actif dans ce salon.")
			
	async def com_disable(self, message, args, kwargs):
		if str(message.channel.id) in self.active_channels:
			self.active_channels.remove(str(message.channel.id))
			#self.save_channels()
			await message.channel.send("Salon retiré.")
		else:
			await message.channel.send("Le salon n'est pas enregistré dans AutoThread.")
	
	async def com_list(self, message, args, kwargs):
		
		channel_list = ""
		for chan_id in self.active_channels:
			channel_list += "<#{0}>\n".format(chan_id)
			
		await message.channel.send(f"`autothread` | **Salons enregistrés ({len(self.active_channels)})** \n" + channel_list)
		

	#def save_channels(self):
	#	self.mainclass.objects.save_object("active_channels", self.active_channels)
	
