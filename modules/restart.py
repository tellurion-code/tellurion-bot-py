import settings.restart
import utils.perms
async def restart_py(client, message):
	if (not (message.author == client.user)) and (message.content.startswith("/restart") and await utils.perms.hasrole(message.author, settings.restart.restartAuth)):
		if str(message.content) == "/restart" :
			await client.delete_message(message)
			await client.logout()
		elif str(message.content) == "/restart py" :
			await client.delete_message(message)
			await client.send_message(message.channel, message.author.mention + ", Le module Python va redémarrer...")
			await client.logout()
