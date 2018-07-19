import utils.perms
import settings.licorne

async def Licorne(client, message) :
    if message.content == "/licorne" and await utils.perms.hasrole(message.author, settings.licorne.licorneAuth) :
        a = 7/0
