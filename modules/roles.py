import settings.roles
import discord
async def AddRole(client, message) :
	args = message.content.split(" ")
	if args[0] == "/role" or args[0] == "/roles" :
		if len(args) > 2 :
			await client.send_message(message.channel, message.author.mention + "\n ```\nusage :\n/roles list(e)\n/roles <nom du rôle>```")
		if args[1] == "liste" or args[1] == "list" :
			response = "```\nListe des roles disponnibles :\n"
			for nom, id in settings.roles.RoleList.items() :
				response += nom + "\n"
			await client.send_message(message.channel, message.author.mention + response + "\n```")
		else :
			try :
				if discord.utils.get(message.server.roles, id=settings.roles.RoleList[args[1]]) in message.author.roles :
					await client.remove_roles(message.author, discord.utils.get(message.server.roles, id=settings.roles.RoleList[args[1]]))
					await client.send_message(message.author, message.author.mention + ", vous avez perdu le rôle " + args[1] +".")
				else :
					await client.add_roles(message.author, discord.utils.get(message.server.roles, id=settings.roles.RoleList[args[1]]))
					await client.send_message(message.author, message.author.mention + ", vous avez reçu le rôle " + args[1] +".")
			except :
				pass
