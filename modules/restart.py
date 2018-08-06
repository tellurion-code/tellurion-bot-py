import asyncio

class MainClass():
    def __init__(self, client, modules, owners):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.events=['on_message'] #events list
        self.command="/restart" #command prefix (can be empty to catch every single messages)

        self.name="Restart"
        self.description="Module gérant les redémarrages du bot"
        self.interactive=True
        self.authlist=[431043517217898496]
        self.color=0x000000
        self.help="""\
 /restart
"""
    async def on_message(self, message):
        args=message.content.split(" ")
        if args[0]=='/restart':
            await message.channel.send(message.author.mention + ", le bot va redémarrer...")
            await self.client.logout()
        else:
            await self.modules['help'][1].send_help(message.channel, self)
