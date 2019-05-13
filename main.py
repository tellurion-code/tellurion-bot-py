#!/usr/bin/python3
import asyncio
import concurrent
import importlib
import json
import logging
import logging.config
import os
import traceback
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict

import discord
from packaging.version import Version

from errors import IncompatibleModule
from modules.base import BaseClass

__version__ = "0.1.0"


class Module:
    name: str

    def __init__(self, name: str):
        """
        Init module

        :param name: Module name
        :type name: str
        """
        self.name = name
        MODULES.update({self.name: self})

    @property
    def exists(self) -> bool:
        """
        Check if module exists

        :return: True if module is present in modules folders
        :rtype: bool
        """
        if not os.path.isdir(os.path.join("modules", self.name)):
            return False
        return True

    @property
    def complete(self) -> bool:
        """
        Check if module is complete

        :return: True if module is compatible
        :rtype: Boolean
        """
        # Check if version.json exists
        if not os.path.exists(os.path.join("modules", self.name, "version.json")):
            return False
        with open(os.path.join("modules", self.name, "version.json")) as file:
            versions = json.load(file)
        if "version" not in versions.keys():
            return False
        if "dependencies" not in versions.keys():
            return False
        if "bot_version" not in versions.keys():
            return False
        return True

    @property
    def version(self) -> Version:
        """
        Returns module version

        :return: current module version
        :rtype: Version
        """
        with open(os.path.join("modules", self.name, "version.json")) as file:
            versions = json.load(file)
        return Version(versions["version"])

    @property
    def bot_version(self) -> dict:
        """
        returns the min and max version of the bot that is compatible with the module

        :return: Min and max version for bot
        :rtype: dict
        :raises IncompatibleModule: If bot_version is not properly formated (there must be min and max keys)
        """
        with open(os.path.join("modules", self.name, "version.json")) as file:
            versions = json.load(file)
        try:
            return {"min": Version(versions["bot_version"]["min"]),
                    "max": Version(versions["bot_version"]["max"])}
        except KeyError:
            raise IncompatibleModule(f"Module {self.name} is not compatible with bot (version.json does not "
                                     f"contain bot_version.max or bot_version.min item)")

    @property
    def dependencies(self) -> dict:
        """
        return list of dependencies version

        :return: list of dependencies version
        :rtype: dict
        :raises IncompatibleModule: If bot_version is not properly formated (there must be min and max keys for each
        dependencies)
        """
        with open(os.path.join("modules", self.name, "version.json")) as file:
            versions = json.load(file)
        try:
            deps = {}
            for name, dep in versions["dependencies"].items():
                dep_ver = {"min": Version(dep["min"]),
                           "max": Version(dep["max"])}
                deps.update({name: dep_ver})
            return deps
        except KeyError:
            raise IncompatibleModule(f"Module {self.name} is not compatible with bot (version.json does not "
                                     f"contain dependencies.modulename.max or dependencies.modulename.min item)")

    @property
    def compatible(self) -> bool:
        """
        Check if module is compatible with current installation

        :return: True if all dependencies are okays
        :rtype: bool
        """
        # Check bot version
        bot_ver = Version(__version__)
        if bot_ver < self.bot_version["min"]:
            return False
        if bot_ver > self.bot_version["max"]:
            return False
        for name, dep in self.dependencies.items():
            if name not in MODULES.keys():
                Module(name)
            if MODULES[name].version < dep["min"]:
                return False
            if MODULES[name].version > dep["max"]:
                return False
        return True


MODULES: Dict[str, Module] = {}


def setup_logging(default_path='config/log_config.json', default_level=logging.INFO, env_key='LBI_LOG_CONFIG'):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def modules_edit(func):
    def wrapper(self, *args, **kwargs):
        print(func.__name__, ":", self.reloading)
        if self.reloading:
            return func(self, *args, **kwargs)
        else:
            self.reloading = True
            a = func(self, *args, **kwargs)
            self.reloading = False
            return a

    return wrapper


def event(func):
    def wrapper(self, *args, **kwargs):
        if self.reloading:
            return lambda: None
        else:
            return func(self, *args, **kwargs)

    return wrapper


setup_logging()

log_discord = logging.getLogger('discord')
log_LBI = logging.getLogger('LBI')

debug = log_LBI.debug
info = log_LBI.info
warning = log_LBI.warning
error = log_LBI.error
critical = log_LBI.critical


def load_modules_info():
    for mod in os.listdir("modules"):
        Module(mod)


class LBI(discord.Client):
    base_path = "storage"
    debug = log_LBI.debug
    info = log_LBI.info
    warning = log_LBI.warning
    error = log_LBI.error
    critical = log_LBI.critical

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reloading = False
        self.id = ClientById(self)
        self.ready = False
        # Content: {"module_name": {"module": imported module, "class": initialized class}}
        self.modules = {}
        self.config = {
            "modules": ["modules"],
            "prefix": "%",
        }
        self.owners = [281166473102098433, 318866596502306816]
        self.load_config()
        self.load_modules()

    def load_config(self, config_file="config/config.json"):
        if os.path.exists(config_file):
            with open(config_file, 'rt') as f:
                config = json.load(f)
            self.config.update(config)
            info("Config successfully loaded.")
        else:
            with open(config_file, 'w') as f:
                json.dump(self.config, f)
            info("Config successfully created.")

    def save_config(self, config_file="config/config.json"):
        with open(config_file, "w") as f:
            json.dump(self.config, f)
        info("Config successfully saved.")

    @modules_edit
    def load_modules(self):
        info("Starts to load modules...")
        e = {}
        for module in self.config["modules"]:
            e.update({module: self.load_module(module)})
        info("Finished to load all modules.")
        return e

    @modules_edit
    def load_module(self, module):
        """

        Status codes:
            - 0: Module loaded
            - 1: Module not in modules folder
            - 2: Module incomplete
            - 3: Module incompatible

        :param module: Module name
        :return: Status code
        """

        # Check module compatibility
        load_modules_info()
        if not MODULES.get(module):
            return 1
        if not MODULES[module].exists:
            return 1
        if not MODULES[module].complete:
            return 2
        if not MODULES[module].compatible:
            return 3
        deps = MODULES[module].dependencies
        for dep in deps.keys():
            if dep not in self.modules.keys():
                self.load_module(dep)
        try:
            info("Start loading module {module}...".format(module=module))
            imported = importlib.import_module('modules.' + module)
            importlib.reload(imported)
            initialized_class = imported.MainClass(self)
            self.modules.update({module: {"imported": imported, "initialized_class": initialized_class}})
            info("Module {module} successfully imported.".format(module=module))
            initialized_class.on_load()
            if module not in self.config["modules"]:
                self.config["modules"].append(module)
                self.save_config()
        except AttributeError as e:
            error("Module {module} doesn't have MainClass.".format(module=module))
            return e
        return 0

    @modules_edit
    def unload_module(self, module):
        info("Start unload module {module}...".format(module=module))
        try:
            if module in self.config["modules"]:
                self.config["modules"].remove(module)
                self.save_config()
                self.unload_all()
                self.load_modules()
        except KeyError as e:
            error("Module {module} not loaded.").format(module=module)
            return e

    @modules_edit
    def reload(self):
        del self.modules
        self.load_modules()

    @modules_edit
    def unload_all(self):
        del self.modules
        self.modules = {}

    @event
    async def on_ready(self):
        for module in self.modules.values():
            await module["initialized_class"].on_ready()

    @event
    async def on_socket_raw_receive(self, message):
        for module in self.modules.values():
            await module["initialized_class"].on_socket_raw_receive(message)

    @event
    async def on_socket_raw_send(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_socket_raw_send(payload)

    @event
    async def on_typing(self, channel, user, when):
        for module in self.modules.values():
            await module["initialized_class"].on_typing(channel, user, when)

    @event
    async def on_message(self, message):
        print(message.content)
        try:
            for module in self.modules.values():
                await module["initialized_class"]._on_message(message)
        except RuntimeError:
            info("Liste des modules changée pendant l'execution d'un on_message")

    @event
    async def on_message_delete(self, message):
        for module in self.modules.values():
            await module["initialized_class"].on_message_delete(message)

    @event
    async def on_raw_message_delete(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_message_delete(payload)

    @event
    async def on_raw_bulk_message_delete(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_bulk_message_delete(payload)

    @event
    async def on_message_edit(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_message_edit(before, after)

    @event
    async def on_raw_message_edit(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_message_edit(payload)

    @event
    async def on_reaction_add(self, reaction, user):
        for module in self.modules.values():
            await module["initialized_class"].on_reaction_add(reaction, user)

    @event
    async def on_raw_reaction_add(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_reaction_add(payload)

    @event
    async def on_reaction_remove(self, reaction, user):
        for module in self.modules.values():
            await module["initialized_class"].on_reaction_remove(reaction, user)

    @event
    async def on_raw_reaction_remove(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_reaction_remove(payload)

    @event
    async def on_reaction_clear(self, message, reactions):
        for module in self.modules.values():
            await module["initialized_class"].on_reaction_clear(message, reactions)

    @event
    async def on_raw_reaction_clear(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_reaction_clear(payload)

    @event
    async def on_private_channel_delete(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_delete(channel)

    @event
    async def on_private_channel_create(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_create(channel)

    @event
    async def on_private_channel_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_update(before, after)

    @event
    async def on_private_channel_pins_update(self, channel, last_pin):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_pins_update(channel, last_pin)

    @event
    async def on_guild_channel_delete(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_delete(channel)

    @event
    async def on_guild_channel_create(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_create(channel)

    @event
    async def on_guild_channel_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_update(before, after)

    @event
    async def on_guild_channel_pins_update(self, channel, last_pin):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_pins_update(channel, last_pin)

    @event
    async def on_member_join(self, member):
        for module in self.modules.values():
            await module["initialized_class"].on_member_join(member)

    @event
    async def on_member_remove(self, member):
        for module in self.modules.values():
            await module["initialized_class"].on_member_remove(member)

    @event
    async def on_member_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_member_update(before, after)

    @event
    async def on_guild_join(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_join(guild)

    @event
    async def on_guild_remove(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_remove(guild)

    @event
    async def on_guild_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_update(before, after)

    @event
    async def on_guild_role_create(self, role):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_role_create(role)

    @event
    async def on_guild_role_delete(self, role):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_role_delete(role)

    @event
    async def on_guild_role_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_role_update(before, after)

    @event
    async def on_guild_emojis_update(self, guild, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_emojis_update(guild, before, after)

    @event
    async def on_guild_available(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_available(guild)

    @event
    async def on_guild_unavailable(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_unavailable(guild)

    @event
    async def on_voice_state_update(self, member, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_voice_state_update(member, before, after)

    @event
    async def on_member_ban(self, guild, user):
        for module in self.modules.values():
            await module["initialized_class"].on_member_ban(guild, user)

    @event
    async def on_member_unban(self, guild, user):
        for module in self.modules.values():
            await module["initialized_class"].on_member_unban(guild, user)

    @event
    async def on_group_join(self, channel, user):
        for module in self.modules.values():
            await module["initialized_class"].on_group_join(channel, user)

    @event
    async def on_group_remove(self, channel, user):
        for module in self.modules.values():
            await module["initialized_class"].on_group_remove(channel, user)

    @event
    async def on_relationship_add(self, relationship):
        for module in self.modules.values():
            await module["initialized_class"].on_relationship_add(relationship)

    @event
    async def on_relationship_remove(self, relationship):
        for module in self.modules.values():
            await module["initialized_class"].on_relationship_remove(relationship)

    @event
    async def on_relationship_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_relationship_update(before, after)

    @event
    async def on_connect(self):
        for module in self.modules.values():
            await module["initialized_class"].on_connect()

    @event
    async def on_shard_ready(self):
        for module in self.modules.values():
            await module["initialized_class"].on_shard_ready()

    @event
    async def on_resumed(self):
        print("resumed")
        for module in self.modules.values():
            await module["initialized_class"].on_resumed()

    @event
    async def on_error(self, event_, *args, **kwargs):
        print(event_, *args, **kwargs)
        print(traceback.format_exc())
        for module in self.modules.values():
            await module["initialized_class"].on_error(event_, *args, **kwargs)

    @event
    async def on_guild_integrations_update(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_integrations_update(guild)

    @event
    async def on_webhooks_update(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_webhooks_update(channel)

    @event
    async def on_toto(self, data):
        print(data)


class ClientById:
    client: LBI

    def __init__(self, client_):
        self.client = client_

    async def fetch_message(self, id_, *args, **kwargs):
        """Find a message by id

        :param id_: Id of message to find
        :type id_: int

        :raises discord.NotFound: This exception is raised when a message is not found (or not accessible by bot)

        :rtype: discord.Message
        :return: discord.Message instance if message is found.
        """
        msg = None
        for channel in self.client.get_all_channels():
            try:
                return await channel.fetch_message(id_, *args, **kwargs)
            except discord.NotFound:
                continue
        if msg is None:
            raise discord.NotFound(None, "Message not found")

    async def edit_message(self, id_, *args, **kwargs):
        """Edit message by id_

        :param id_: Id of the message to edit
        :type id_: int"""
        message = await self.fetch_message(id_)
        return await message.edit(**kwargs)

    async def remove_reaction(self, id_message, *args, **kwargs):
        """Remove reaction from message by id

        :param id_message: Id of message
        :type id_message: int"""
        message = await self.fetch_message(id_message)
        return await message.remove_reaction(*args, **kwargs)

    async def send_message(self, id_, *args, **kwargs):
        """Send message by channel id

        :param id_: Id of channel where to send message
        :type id_: int"""
        channel = self.client.get_channel(id_)
        return channel.send(*args, **kwargs)


client = LBI()


def read_sock():
    print("connect")
    import socket, os
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        os.remove("/tmp/bot.sock")  # TODO: Changer le nom du socket car il en faut un par bot
    except OSError:
        pass
    s.bind("/tmp/bot.sock")  # TODO: Voir ici aussi
    s.listen(1)
    conn, addr = s.accept()
    while 1:
        data = conn.recv(1024)
        print(data)
        content = data.decode("utf8")
        if content.startswith("send"):
            print("okip")
            client.dispatch("toto", data)
        conn.send(data)


async def start_bot():
    await client.start('TOKEN', max_messages=500000)


async def stop_bot():
    await client.logout()


async def main():
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool, start_bot)
        await loop.run_in_executor(pool, read_sock)

asyncio.run(main())