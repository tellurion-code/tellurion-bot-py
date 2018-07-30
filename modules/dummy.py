#dummy module
import asyncio

class MainClass():
    def __init__(self, client, modules, saves):
        self.client = client
        self.modules = modules
        self.saves = saves
        self.events=['on_message'] #events list
        self.command="/dummy" #command prefix (can be empty to catch every single messages)

        self.name="Dummy"
        self.description="Module d'exemple"
        self.help="""
 Aucune fonction.
"""[1::]
    async def on_message(self, message):
        print(message.content)
