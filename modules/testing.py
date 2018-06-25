import pygit2
import utils.perms
import settings.testing
from subprocess import call
async def testsHandler(client, message) :
	if message.content == "/testing start" and await utils.perms.hasrole(message.author, settings.testing.testingAuth) and pygit2.Repository('.').head.shorthand=="master" :
		await client.delete_message(message)
		await client.send_message(message.channel, message.author.mention + ", Le module de **test** Python va démarrer...")
		call(['bash', '/home/epenser/runtest'])
	if message.content == "/testing stop" and await utils.perms.hasrole(message.author, settings.testing.testingAuth) and pygit2.Repository('.').head.shorthand=="testing" :
		await client.delete_message(message)
		await client.send_message(message.channel, message.author.mention + ", Le module de **test** Python va s'arrêter...")
		await client.logout()
	if message.content == "/testing restart" and await utils.perms.hasrole(message.author, settings.testing.testingAuth) :
		if pygit2.Repository('.').head.shorthand=="testing" :
			await client.delete_message(message)
			await client.send_message(message.channel, message.author.mention + ", Le module de **test** Python va redémarrer...")
			await client.logout()
		if pygit2.Repository('.').head.shorthand=="master" :
			call(['bash', '/home/epenser/runtest'])
