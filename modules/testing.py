import pygit2
import utils.perms
import settings.testing
from subprocess import call
async def testsHandler(client, message) :
	if message.content == "/testing start" and await utils.perms.hasrole(message.author, settings.testing.testingAuth) and pygit2.Repository('.').head.shorthand=="master" :
		call(['bash', '/home/epenser/runtest'])
	if message.content == "/testing stop" and await utils.perms.hasrole(message.author, settings.testing.testingAuth) and pygit2.Repository('.').head.shorthand=="testing" :
		await client.logout()
