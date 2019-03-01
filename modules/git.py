#dummy module
import asyncio
import os
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
 => Execute les commandes suivantes dans le dossier du bot:
 ```BASH
 git fetch --all
 git reset --hard origin/<branch_name>```
"""
    async def on_message(self, message):
        args=message.content.split(' ')
        if len(args)==2 and args[1]=='update':
            with os.popen('git fetch --all') as stdin:
                await message.channel.send(stdin.read())
            with os.popen('git symbolic-ref HEAD 2>/dev/null') as stdin:
                branch=stdin.read().replace('refs/heads/', '')
            with os.popen('git reset --hard origin/%s'%branch) as stdin:
                await message.channel.send(stdin.read())
            await message.channel.send(message.author.mention+", Le dépôt a été mis à jour (fetch + reset --hard).")
        else:
            await self.modules['help'][1].send_help(message.channel, self)
