import os

import discord
from aiohttp import ClientConnectorError

from modules.base import BaseClassPython
from modules.modules.api import Api


class MainClass(BaseClassPython):
    name = "modules"
    help_active = True
    command_text = "modules"
    color = 0x000000
    help = {
        "description": "Manage bot modules.",
        "commands": {
            "`{prefix}{command} list`": "List of available modules.",
            "`{prefix}{command} enable <module>`": "Enable module `<module>`.",
            "`{prefix}{command} disable <module>`": "Disable module `<module>`.",
            "`{prefix}{command} reload <module>`": "Reload module `<module>`",
            "`{prefix}{command} web_list`": "List all available modules from repository",
            # "`{prefix}{command} web_source`": "List all source repositories",
            # "`{prefix}{command} web_source remove <url>`": "Remove url from repository list",
            # "`{prefix}{command} web_source add <url>`": "Add url to repository list",
        }
    }

    def __init__(self, client):
        super().__init__(client)
        os.makedirs("modules", exist_ok=True)
        self.api = Api()

    @staticmethod
    def get_all_modules():
        all_items = os.listdir("modules")
        modules = []
        for item in all_items:
            if item not in ["__init__.py", "base", "__pycache__"]:
                if os.path.isfile(os.path.join("modules", item)):
                    modules.append(item[:-3])
                else:
                    modules.append(item)
        return set(modules)

    async def com_enable(self, message, args, kwargs):
        args = args[1:]
        if len(args) == 0:
            await message.channel.send("You must specify at least one module.")
            return
        if len(args) == 1 and args[0] == "*":
            for module in self.get_all_modules():
                e = self.client.load_module(module)
                if e:
                    await message.channel.send("An error occurred during the loading of the module {module}."
                                               .format(module=module))
            await self.com_list(message, args, kwargs)
            return
        for arg in args:
            e = self.client.load_module(arg)
            if e == 1:
                await message.channel.send(f"Module {arg} not exists.")
            if e == 2:
                await message.channel.send(f"Module {arg} is incompatible.")
            elif e:
                await message.channel.send(f"An error occurred during the loading of the module {arg}: {e}.")
        await self.com_list(message, args, kwargs)

    async def com_reload(self, message, args, kwargs):
        args = args[1:]
        if len(args) == 0:
            await message.channel.send("You must specify at least one module.")
            return
        if len(args) == 1 and args[0] == "*":
            for module in self.get_all_modules():
                e = self.client.unload_module(module)
                if e:
                    await message.channel.send(f"An error occurred during the loading of the module {module}.")
            await self.com_list(message, args, kwargs)
            return
        for arg in args:
            e = self.client.unload_module(arg)
            if e:
                await message.channel.send(f"An error occurred during the loading of the module {arg}.")
        await self.com_list(message, [], [])

    async def com_disable(self, message, args, kwargs):
        args = args[1:]
        if len(args) == 0:
            await message.channel.send("You must specify at least one module.")
            return
        if len(args) == 1 and args[0] == "*":
            for module in self.get_all_modules():
                e = self.client.unload_module(module)
                if e:
                    await message.channel.send(f"An error occurred during the loading of the module {module}.")
            await self.com_list(message, args, kwargs)
            return
        for arg in args:
            e = self.client.unload_module(arg)
            if e:
                await message.channel.send(f"An error occurred during the loading of the module {arg}: {e}.")
        await self.com_list(message, [], [])

    async def com_list(self, message, args, kwargs):
        list_files = self.get_all_modules()
        activated = set(self.client.config["modules"])
        if len(activated):
            activated_string = "\n+ " + "\n+ ".join(activated)
        else:
            activated_string = ""
        if len(activated) != len(list_files):
            deactivated_string = "\n- " + "\n- ".join(list_files.difference(activated))
        else:
            deactivated_string = ""
        embed = discord.Embed(title="[Modules] - Liste des modules",
                              description="```diff{activated}{deactivated}```".format(
                                  activated=activated_string,
                                  deactivated=deactivated_string)
                              )
        await message.channel.send(embed=embed)

    async def com_web_list(self, message, args, kwargs):
        try:
            modules = await self.api.list()
        except ClientConnectorError:
            await message.channel.send("Connection impossible au serveur.")
            return
        text = ""
        for module, versions in modules.items():
            text += module + " - " + ", ".join(versions)
        await message.channel.send(text)

    async def com_web_dl(self, message, args, kwargs):
        try:
            await self.api.download(args[1], args[2])
        except ClientConnectorError:
            await message.channel.send("Connection impossible au serveur.")
