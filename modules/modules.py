import discord
import asyncio
import os
import importlib
class MainClass():
    def __init__(self, client, modules, owners):
        self.states={}
        for moduleName in os.listdir('modules'):
            if moduleName.endswith(".py"):
                self.states.update({moduleName[:-3:]:'not loaded'})
        for moduleName in list(modules.keys()):
            if len(modules[moduleName]) == 2 :
                self.states.update({moduleName:'initialized'})
        self.client = client
        self.modules = modules
        self.owners = owners
        self.events=['on_message', 'on_ready'] #events list
        self.command="/modules" #command prefix (can be empty to catch every single messages)

        self.name="Modules"
        self.description="Module de gestion des modules"
        self.interactive=True
        self.authlist=[431043517217898496]
        self.color=0x8f3196
        self.help="""\
 /modules list
 => Liste les modules ainsi que leurs états
 
 /modules enable <module/modules>
 => Charge et active le / les modules spécifié(s)
 
 /modules disable <module/modules>
 => Désactive et décharge le / les modules spécifié(s)
 
 => <module/modules>
 ==> Unique module ou liste de module séparés par des virgules
"""
        self.states.update({'modules': 'initialized'})
    async def on_message(self, message):
        error=None
        args = message.content.split(" ")
        if len(args) == 2 and args[1]=='list':
            await message.channel.send(embed=discord.Embed(title="[Modules] - Modules list", description="```PYTHON\n{0}```".format(str(self.states).replace(',', '\n,'))))
        elif len(args) == 3 and args[1] in ['enable', 'disable', 'reload']:
            if args[1]=='enable':
                for moduleName in args[2].split(','):
                    if moduleName + '.py' in os.listdir('modules'):
                        try:
                            self.enable_module(moduleName)
                            await message.channel.send(message.author.mention + ", le module {0} a été activé".format(moduleName))
                        except Exception as e:
                            error=e
                            await message.channel.send(message.author.mention + ", le module {0} **n'a pas pu être activé**".format(moduleName))
                    else:
                        await message.channel.send(message.author.mention + ", le module {0} n'existe pas.".format(moduleName))
            elif args[1]=='disable':
                for moduleName in args[2].split(','):
                    if moduleName == 'modules':
                        await message.channel.send(message.author.mention + ", le module {0} ne peut pas être désactivé car il est nécéssaire pour gérer les modules.".format(moduleName))
                    else:
                        if moduleName + '.py' in os.listdir('modules'):
                            self.unload_module(moduleName)
                            await message.channel.send(message.author.mention + ", le module {0} a été désactivé.".format(moduleName))
                        else:
                            await message.channel.send(message.author.mention + ", le module {0} n'existe pas.".format(moduleName))
        else:
            await self.modules['help'][1].send_help(message.channel, self)
        if error:
            raise error
    async def on_ready(self):
        error=None
        for fileName in os.listdir('modules'):
            try:
                self.load_module(fileName[:-3:])
                self.init_module(fileName[:-3:])
            except Exception as e:
                error=e
        if error:
            raise error
    def enable_module(self, moduleName):
        self.load_module(moduleName)
        self.init_module(moduleName)

    def load_module(self, moduleName):
        if moduleName + ".py" in os.listdir('modules'):
            if not moduleName in list(self.states.keys()) or self.states[moduleName] == 'not loaded':
                try:
                    self.modules.update({moduleName:[importlib.import_module('modules.' + moduleName)]})
                    print("Module {0} chargé.".format(moduleName))
                    self.states[moduleName] = 'loaded'
                except:
                    print("[ERROR] Le module {0} n'a pas pu être chargé.".format(moduleName))
                    self.unload_module(moduleName)
                    raise
    def init_module(self, moduleName):
        if moduleName + ".py" in os.listdir('modules'):
            if self.states[moduleName] == 'loaded':
                try:
                    self.modules[moduleName].append(self.modules[moduleName][0].MainClass(self.client, self.modules, self.owners))
                    print("Module {0} initialisé.".format(moduleName))
                    self.states[moduleName] = 'initialized'
                except:
                    print("[ERROR] Le module {0} n'a pas pu être initialisé.".format(moduleName))
                    self.unload_module(moduleName)
                    raise
    def unload_module(self, moduleName):
        if moduleName + ".py" in os.listdir('modules'):
            self.states[moduleName] = 'not loaded'
            self.modules.pop(moduleName, None)
            print("Module {0} déchargé.".format(moduleName))
