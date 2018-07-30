import asyncio
import discord
class MainClass():
    def __init__(self, client, modules, saves):
        self.client = client
        self.modules = modules
        self.saves = saves
        self.events=['on_message'] #events list
        self.command="/help" #command prefix (can be empty to catch every single messages)

        self.name="Aide"
        self.description="Module d'aide"
        self.color=0x3c9653
        self.help="""
 /help list
 => Affiche une liste des modules ainsi qu'une description
 
 /help <nom du module>
 => Affiche l'aide spécifique d'un module.
"""[1::]
    async def on_message(self, message):
        args=message.content.split(' ')
        if len(args)==2 and args[1]=='list':
            embed=discord.Embed(title="[Aide] - Liste des modules", color=self.color)
            for moduleName in list(self.modules.keys()):
                embed.add_field(name=moduleName, value=self.modules[moduleName][1].description)
            await message.channel.send(embed=embed)
        elif len(args)==2 and args[1] in list(self.modules.keys()):
            await message.channel.send(embed=discord.Embed(title="[{0}] - Aide".format(args[1]), description=self.modules[args[1]][1].help, color=self.modules[args[1]][1].color))
