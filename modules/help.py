import discord

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "Aide"
    help_active = True
    help = {
        "description": "Module d'aide",
        "commands": {
            "`{prefix}help list`": "Affiche une liste des modules ainsi qu'une desription",
            "`{prefix}help <module>": "Affiche l'aide sépcifique d'un module",
            "`{prefix}help all`": "Affiche l'aide de tous les modules"
        }
    }
    color = 0x3c9653
    command_text = "help"

    async def com_list(self, message, args, kwargs):
        embed = discord.Embed(title="[Aide] - Liste des modules", color=self.color)
        for moduleName in list(self.client.modules.keys()):
            if self.client.modules[moduleName]["class"].help_active and \
                    self.auth(message.author, moduleName):
                embed.add_field(
                    name=moduleName.capitalize(),
                    value=self.client.modules[moduleName]["class"].help["description"])
        await message.channel.send(embed=embed)

    async def on_message(self, message):
        args = message.content.lower().split(' ')
        if len(args) == 2 and args[1] == 'list':
            pass
        elif len(args) == 2 and args[1] in list(self.modules.keys()) and \
                self.modules[args[1]][1].interactive and \
                self.auth(message.author, args[1]):
            await message.channel.send(embed=discord.Embed(title="[{0}] - Aide".format(args[1].capitalize()),
                                                           description=self.modules[args[1]][1].help.replace(
                                                               "</prefix>", self.prefix),
                                                           color=self.modules[args[1]][1].color)
                                       )
        elif len(args) == 2 and args[1] == 'all':
            async with message.channel.typing():
                for moduleName in list(self.modules.keys()):
                    if self.modules[moduleName][1].interactive and \
                            self.auth(message.author, moduleName):
                        await message.channel.send(
                            embed=discord.Embed(title="[{0}] - Aide".format(moduleName.capitalize()),
                                                description=self.modules[moduleName][1].help.replace("</prefix>",
                                                                                                     self.prefix),
                                                color=self.modules[moduleName][1].color)
                        )
        else:
            await self.modules['help'][1].send_help(message.channel, self)

    async def send_help(self, channel, module):
        moduleName = None
        for name, list_module_instance in self.modules.items():
            if module == list_module_instance[1]:
                moduleName = name
                break
        await channel.send(embed=discord.Embed(title="[{0}] - Aide".format(moduleName.capitalize()),
                                               description=self.modules[moduleName][1].help.replace("</prefix>",
                                                                                                    self.prefix),
                                               color=self.modules[moduleName][1].color))
