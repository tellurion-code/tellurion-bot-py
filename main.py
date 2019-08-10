#!/usr/bin/python3
import asyncio
import concurrent
import importlib
import json
import logging
import logging.config
import os
import signal
import socket
import traceback
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict

import discord
from packaging.version import Version

from errors import IncompatibleModule

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
    def type(self) -> str:
        """
        Return module type. It can be python or lua

        :return: Module type
        :rtype: str
        """
        if not os.path.exists(os.path.join("modules", self.name, "version.json")):
            return ""
        with open(os.path.join("modules", self.name, "version.json")) as file:
            versions = json.load(file)
        return versions["type"]

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
        if "type" not in versions.keys():
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
log_communication = logging.getLogger('communication')


def load_modules_info():
    for mod in os.listdir("modules"):
        Module(mod)


class LBI(discord.Client):
    base_path = "data"
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
            "owners": [],
        }
        self.load_config()
        self.load_modules()

    def load_config(self, config_file="config/config.json"):
        if os.path.exists(config_file):
            with open(config_file, 'rt') as f:
                config = json.load(f)
            self.config.update(config)
            self.info("Config successfully loaded.")
        else:
            with open(config_file, 'w') as f:
                json.dump(self.config, f)
            self.info("Config successfully created.")

    def save_config(self, config_file="config/config.json"):
        with open(config_file, "w") as f:
            json.dump(self.config, f)
        self.info("Config successfully saved.")

    @modules_edit
    def load_modules(self):
        self.info("Starts to load modules...")
        e = {}
        for module in self.config["modules"]:
            e.update({module: self.load_module(module)})
        self.info("Finished to load all modules.")
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
                if dep != "base":
                    self.load_module(dep)
        if MODULES[module].type == "python":
            try:
                self.info("Start loading module {module}...".format(module=module))
                imported = importlib.import_module('modules.' + module)
                importlib.reload(imported)
                initialized_class = imported.MainClass(self)
                self.modules.update({module: {"imported": imported, "initialized_class": initialized_class}})
                self.info("Module {module} successfully imported.".format(module=module))
                initialized_class.dispatch("load")
                if module not in self.config["modules"]:
                    self.config["modules"].append(module)
                    self.save_config()
            except AttributeError as e:
                self.error("Module {module} doesn't have MainClass.".format(module=module))
                return e
            return 0
        elif MODULES[module].type == "lua":
            self.info(f"Start loading module {module}...")
            imported = importlib.import_module('modules.base.BaseLua')
            importlib.reload(imported)
            initialized_class = imported.BaseClassLua(self, path=f"modules/{module}/main")
            self.modules.update({module: {"imported": imported, "initialized_class": initialized_class}})
            self.info(f"Module {module} successfully imported.")
            initialized_class.dispatch("load")
            if module not in self.config["modules"]:
                self.config["modules"].append(module)
                self.save_config()
            return 0

    @modules_edit
    def unload_module(self, module):
        self.info("Start unload module {module}...".format(module=module))
        try:
            if module in self.config["modules"]:
                self.config["modules"].remove(module)
                self.save_config()
                self.unload_all()
                self.load_modules()
        except KeyError as e:
            self.error("Module {module} not loaded.").format(module=module)
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
    def dispatch(self, event, *args, **kwargs):
        # Dispatch to handle wait_* commands
        super().dispatch(event, *args, **kwargs)
        # Dispatch to modules
        for module in self.modules.values():
            module["initialized_class"].dispatch(event, *args, **kwargs)

    @event
    async def on_error(self, event_method, *args, **kwargs):
        # This event is special because it is call directly
        for module in self.modules.values():
            await module["initialized_class"].on_error(event_method, *args, **kwargs)


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

    async def get_role(self, id_):
        for guild in self.client.guilds:
            role = discord.utils.get(guild.roles, id=id_)
            if role:
                return role
        return None


client1 = LBI()


class Communication(asyncio.Protocol):
    debug = log_communication.debug
    info = log_communication.info
    warning = log_communication.warning
    error = log_communication.error
    critical = log_communication.critical
    name = "Communication"

    def __init__(self, client=client1):
        print("créé")
        self.client = client
        self.transport = None

    def connection_made(self, transport):
        print('%s: connection made' % self.name)
        self.transport = transport

    def data_received(self, data):
        print('%s: data received: %r' % (self.name, data))

    def eof_received(self):
        pass

    def connection_lost(self, exc):
        print('%s: connection lost: %s' % (self.name, exc))


communication = Communication(client1)


async def start_bot():
    await client1.start(os.environ.get("DISCORD_TOKEN"), max_messages=500000)


def execption_handler(loop, context):
    print('%s: %s' % ('Connection', context['exception']))
    traceback.print_exc()


print(os.path.join("/tmp", os.path.dirname(os.path.realpath(__file__))) + ".sock")

loop = asyncio.get_event_loop()
#loop.add_signal_handler(signal.SIGINT, loop.stop)
#loop.set_exception_handler(execption_handler)
t = loop.create_unix_server(Communication,
                            path=os.path.join("/tmp", os.path.dirname(os.path.realpath(__file__)) + ".sock"))
loop.run_until_complete(t)
loop.create_task(start_bot())
loop.run_forever()

# loop = asyncio.get_event_loop()
# loop.run_forever()
