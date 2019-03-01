#dummy module
import asyncio
from subprocess import call
class MainClass():
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events=['on_message'] #events list
        self.command="%sgit"%self.prefix #command prefix (can be empty to catch every single messages)

        self.name="Git"
        self.description="Module de gestion de Git"
        self.interactive=True
        self.authlist=[]
        self.color=0xdc0000
        self.help="""\
 </prefix>git update
 => Execute les commandes suivantes dans le dossier en cours:
 ```BASH
 git fetch --all
 git reset --hard origin/master```
"""
    async def on_message(self, message):
        args=message.content.split(' ')
        if len(args)==2 and args[1]=='update':
            call('git fetch --all'.split(' '))
            call('git reset --hard origin/testing'.split(' '))
            await message.channel.send(message.author.mention+", Le dépôt a été mis à jour (fetch + reset --hard).")
        else:
            await self.modules['help'][1].send_help(message.channel, self)
