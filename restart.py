import settings
async def hasrole(member, roleidlist):
	for role in member.roles :
		for roleid in roleidlist:
			if role.id == roleid :
				return True
	return False
async def restart_py(client, message):
	if (not (message.author == client.user)) and await hasrole(message.author, settings.c_restart.restartAuth):
		if str(message.content) == "/restart" :
			await client.logout()
		elif str(message.content) == "/restart py" :
			await client.delete_message(message)
			await client.send_message(message.channel, message.author.mention + ", Le module Python va redémarrer...")
			await client.logout()
