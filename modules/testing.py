import pygit2
import utils.perms
import settings.testing
from subprocess import call
import utils.usertools
async def testsHandler(client, message) :
    if message.content.startswith('/'):
        print(" [" + str(message.channel.name) + "]" + " " + str(message.timestamp.strftime('%Y-%m-%d %H:%M:%S')) +  " " + message.author.name + "#" + message.author.discriminator + "> " + str(message.content) + "\n")
    if message.content == "/testing start" and await utils.perms.hasrole(message.author, settings.testing.testingAuth) and pygit2.Repository('.').head.shorthand=="master":
        try:
            await client.delete_message(message)
        except:
            pass
        await client.send_message(message.channel, message.author.mention + ", Le module de **test** Python va démarrer...")
        call(['bash', '/home/epenser/runtest'])
    if message.content == "/testing stop" and await utils.perms.hasrole(message.author, settings.testing.testingAuth) and pygit2.Repository('.').head.shorthand=="testing":
        try:
            await client.delete_message(message)
        except:
            pass
        await client.send_message(message.channel, message.author.mention + ", Le module de **test** Python va s'arrêter...")
        await client.logout()
    if message.content == "/testing restart" and await utils.perms.hasrole(message.author, settings.testing.testingAuth):
        if pygit2.Repository('.').head.shorthand=="testing" :
            try:
                await client.delete_message(message)
            except:
                pass
            await client.send_message(message.channel, message.author.mention + ", Le module de **test** Python va redémarrer...")
            call(['bash', '/home/epenser/runtest'])
            await client.logout()
    if message.content == "/testing clear_cache": and await utils.perms.hasrole(message.author, settings.testing.testingAuth)
        utils.usertools.UserById.clear_cache()
