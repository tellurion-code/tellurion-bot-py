import asyncio

class MainClass():
    def __init__(self, client, modules, saves):
        self.client = client
        self.modules = modules
        self.saves = saves
        self.events=['on_message'] #events list
        self.command="/modules" #command prefix (can be empty to catch every single messages)

        self.name="Modules"
        self.description="Module de gestion des modules"
        self.help="""
 /modules list
 => liste les modules ainsi que leur états
 
 /modules enable <nom du module>
 => Charge et active le module spécifié
 
 /modules disable <nom du module>
 => désactive et décharge le module spécifié
"""[1::]
    async def on_message(self, message):
        args = message.content.split(" ")
        
