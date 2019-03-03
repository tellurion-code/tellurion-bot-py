import os
import traceback

import discord

from .base import BaseClass


class MainClass(BaseClass):
    name = "Modules"
    super_users = [431043517217898496]
    color = 0x000000
    help_active = True
    help = {
        "description": "Module gérant les modules du bot",
        "commands": {
            "`{prefix}modules list`": "Liste les modules",
            "`{prefix}modules enable <module>`": "Active le module `<module>`",
            "`{prefix}modules disable <module>`": "Désactive le module `<module>`",
            # "`{prefix}modules reload <module>`": "Reload le module `<module>`",
        }
    }
    command_text = "modules"

    async def com_enable(self, message, args, kwargs):
        args = args[1:]
        if len(args) == 0:
            await message.channel.send("Vous devez spécifier au moins un module")
            return
        if len(args) == 1 and args[0] == "*":
            for module in set([name[:-3] for name in os.listdir('modules') if name not in ["base.py", "__pycache__"]]):
                e = self.client.load_module(module)
                if e:
                    await message.channel.send("Une erreur a eu lieu pendant le chargement du module {module}".format(module=module))
            await self.com_list(message, args, kwargs)
            return
        for arg in args:
            e = self.client.load_module(arg)
            if e:
                await message.channel.send("Une erreur a eu lieu pendant le chargement du module {module}".format(module=arg))
        await self.com_list(message, args, kwargs)

    async def com_disable(self, message, args, kwargs):
        args = args[1:]
        if len(args) == 0:
            await message.channel.send("Vous devez spécifier au moins un module")
            return
        for arg in args:
            print(arg)
            e = self.client.unload_module(arg)
            if e:
                await message.channel.send("Une erreur a eu lieu pendant le déchargement du module {module}".format(module=arg))
        await self.com_list(message, [], [])


    async def com_list(self, message, args, kwargs):
        list_files = set([name[:-3] for name in os.listdir('modules') if name not in ["base.py", "__pycache__"]])
        activated = set(self.client.config["modules"])
        activated_string = "\n+ " + "\n+ ".join(activated)
        deactivated_string = "- " + "\n- ".join(list_files.difference(activated))
        embed = discord.Embed(title="[Modules] - Modules list",
                              description="```diff\n{activated}\n{deactivated}```".format(
                                  activated=activated_string,
                                  deactivated=deactivated_string)
                              )
        await message.channel.send(embed=embed)
