import asyncio

class MainClass():
    def __init__(self, client, modules, saves):
        self.client = client
        self.modules = modules
        self.saves = saves
        self.events=['on_message'] #events list
        self.command="/restart" #command prefix (can be empty to catch every single messages)

        self.name="Dummy"
        self.description="Module d'exemple"
        self.interactive=True
        self.color=0x000000
        self.help="""\
 /restart
"""
    async def on_message(self, message):
        args=message.content.split(" ")
        if args[0]=='/restart':
            await message.channel.send(message.author.mention + ", le bot va redémarrer...")
            await self.client.logout()
