import discord


class MainClass:
    def auth(self, user, moduleName):
        if user.id in self.owners:
            return True
        try:
            self.modules[moduleName][1].authlist
        except:
            return True
        for guild in self.client.guilds:
            if guild.get_member(user.id):
                for role_id in self.modules[moduleName][1].authlist:
                    if role_id in [r.id for r in guild.get_member(user.id).roles]:
                        return True

    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message']  # events list
        self.command = "%shelp" % self.prefix  # command_text prefix (can be empty to catch every single messages)

        self.name = "Aide"
        self.description = "Module d'aide"
        self.interactive = True
        self.color = 0x3c9653
        self.help = """\
 </prefix>help list
 => Affiche une liste des modules ainsi qu'une description
 
 </prefix>help <nom du module>
 => Affiche l'aide spécifique d'un module.
 
 </prefix>help all
 => Affiche les aides de tous les modules
"""

    async def on_message(self, message):
        args = message.content.lower().split(' ')
        if len(args) == 2 and args[1] == 'list':
            embed = discord.Embed(title="[Aide] - Liste des modules", color=self.color)
            for moduleName in list(self.modules.keys()):
                if self.modules[moduleName][1].interactive and \
                        self.auth(message.author, moduleName):
                    embed.add_field(name=moduleName.capitalize(), value=self.modules[moduleName][1].description)
            await message.channel.send(embed=embed)
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
