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
        self.interactive=True
        self.color=0x3c9653
        self.help="""\
 /help list
 => Affiche une liste des modules ainsi qu'une description
 
 /help <nom du module>
 => Affiche l'aide spécifique d'un module.
 
 /help all
 => Affiche les aides de tous les modules
"""
    async def on_message(self, message):
        args=message.content.lower().split(' ')
        if len(args)==2 and args[1]=='list':
            embed=discord.Embed(title="[Aide] - Liste des modules", color=self.color)
            for moduleName in list(self.modules.keys()):
                if self.modules[moduleName][1].interactive:
                    embed.add_field(name=moduleName.capitalize(), value=self.modules[moduleName][1].description)
            await message.channel.send(embed=embed)
        elif len(args)==2 and args[1] in list(self.modules.keys()) and self.modules[args[1]][1].interactive:
            await message.channel.send(embed=discord.Embed(title="[{0}] - Aide".format(args[1].capitalize()), description=self.modules[args[1]][1].help, color=self.modules[args[1]][1].color))
        elif len(args)==2 and args[1]=='all':
            for moduleName in list(self.modules.keys()):
                if self.modules[moduleName][1].interactive:
                    await message.channel.send(embed=discord.Embed(title="[{0}] - Aide".format(moduleName.capitalize()), description=self.modules[moduleName][1].help, color=self.modules[moduleName][1].color))
        else:
            await self.modules['help'][1].send_help(message.channel, self)

    async def send_help(self, channel, module):
        moduleName=None
        for name, listpck in self.modules.items():
            if module == listpck[1]:
                moduleName=name
                break
        await channel.send(embed=discord.Embed(title="[{0}] - Aide".format(moduleName.capitalize()), description=self.modules[moduleName][1].help, color=self.modules[moduleName][1].color))
