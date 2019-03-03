#!/usr/bin/python3
import importlib
import json
import logging
import logging.config
import os
import traceback

import discord

from modules.base import BaseClass


def setup_logging(default_path='config/log_config.json', default_level=logging.INFO, env_key='LOG_CFG'):
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


setup_logging()

log_discord = logging.getLogger('discord')
log_nokola_tesla = logging.getLogger('nikola_tesla')

debug = log_nokola_tesla.debug
info = log_nokola_tesla.info
warning = log_nokola_tesla.warning
error = log_nokola_tesla.error
critical = log_nokola_tesla.critical


class NikolaTesla(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            info("Config successfully loaded")
        else:
            with open(config_file, 'w') as f:
                json.dump(self.config, f)
            info("Config successfully created")

    def save_config(self, config_file="config/config.json"):
        with open(config_file, "w") as f:
            json.dump(self.config, f)
        info("Config successfully saved")

    def load_modules(self):
        info("Starts to load modules...")
        e = {}
        for module in self.config["modules"]:
            e.update({module: self.load_module(module)})
        info("Finished to load all modules")
        return e

    def load_module(self, module):
        info("Start loading module {module}...".format(module=module))
        try:
            imported = importlib.import_module('modules.' + module)
            try:
                initialized_class = imported.MainClass(self)
                if isinstance(initialized_class, BaseClass):
                    self.modules.update({module: {"imported": imported, "initialized_class": initialized_class}})
                    info("Module {module} successfully imported".format(module=module))
                    initialized_class.on_load()
                    if module not in self.config["modules"]:
                        self.config["modules"].append(module)
                        self.save_config()
                else:
                    error("Module MainClass doesn't inherited from BaseClass")
                    return ValueError("MainClass doesn't inherit from BaseClass")
            except AttributeError as e:
                error("Module {module} doesn't have a MainClass".format(module=module))
                return e
        except ImportError as e:
            error("Module {module} doesn't exists".format(module=module))
            return e
        except Exception as e:
            error("Failed to import module {module}".format(module=module))
            return e

    def unload_module(self, module):
        info("Start unload module {module}...".format(module=module))
        try:
            del self.modules[module]
            if module in self.config["modules"]:
                self.config["modules"].remove(module)
                self.save_config()
        except KeyError as e:
            error("Module {module} not loaded".format(module=module))
            return e

    async def on_socket_raw_receive(self, message):
        for module in self.modules.values():
            await module["initialized_class"].on_socket_raw_receive(message)

    async def on_socket_raw_send(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_socket_raw_send(payload)

    async def on_typing(self, channel, user, when):
        for module in self.modules.values():
            await module["initialized_class"].on_typing(channel, user, when)

    async def on_message(self, message):
        try:
            for module in self.modules.values():
                await module["initialized_class"]._on_message(message)
        except RuntimeError:
            info("Liste des modules changée pendant l'execution d'un on_message")

    async def on_message_delete(self, message):
        for module in self.modules.values():
            await module["initialized_class"].on_message_delete(message)

    async def on_raw_message_delete(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_message_delete(payload)

    async def on_raw_bulk_message_delete(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_bulk_message_delete(payload)

    async def on_message_edit(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_message_edit(before, after)

    async def on_raw_message_edit(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_message_edit(payload)

    async def on_reaction_add(self, reaction, user):
        for module in self.modules.values():
            await module["initialized_class"].on_reaction_add(reaction, user)

    async def on_raw_reaction_add(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_reaction_add(payload)

    async def on_reaction_remove(self, reaction, user):
        for module in self.modules.values():
            await module["initialized_class"].on_reaction_remove(reaction, user)

    async def on_raw_reaction_remove(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_reaction_remove(payload)

    async def on_reaction_clear(self, message, reactions):
        for module in self.modules.values():
            await module["initialized_class"].on_reaction_clear(message, reactions)

    async def on_raw_reaction_clear(self, payload):
        for module in self.modules.values():
            await module["initialized_class"].on_raw_reaction_clear(payload)

    async def on_private_channel_delete(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_delete(channel)

    async def on_private_channel_create(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_create(channel)

    async def on_private_channel_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_update(before, after)

    async def on_private_channel_pins_update(self, channel, last_pin):
        for module in self.modules.values():
            await module["initialized_class"].on_private_channel_pins_update(channel, last_pin)

    async def on_guild_channel_delete(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_delete(channel)

    async def on_guild_channel_create(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_create(channel)

    async def on_guild_channel_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_update(before, after)

    async def on_guild_channel_pins_update(self, channel, last_pin):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_channel_pins_update(channel, last_pin)

    async def on_member_join(self, member):
        for module in self.modules.values():
            await module["initialized_class"].on_member_join(member)

    async def on_member_remove(self, member):
        for module in self.modules.values():
            await module["initialized_class"].on_member_remove(member)

    async def on_member_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_member_update(before, after)

    async def on_guild_join(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_join(guild)

    async def on_guild_remove(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_remove(guild)

    async def on_guild_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_update(before, after)

    async def on_guild_role_create(self, role):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_role_create(role)

    async def on_guild_role_delete(self, role):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_role_delete(role)

    async def on_guild_role_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_role_update(before, after)

    async def on_guild_emojis_update(self, guild, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_emojis_update(guild, before, after)

    async def on_guild_available(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_available(guild)

    async def on_guild_unavailable(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_unavailable(guild)

    async def on_voice_state_update(self, member, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_voice_state_update(member, before, after)

    async def on_member_ban(self, guild, user):
        for module in self.modules.values():
            await module["initialized_class"].on_member_ban(guild, user)

    async def on_member_unban(self, guild, user):
        for module in self.modules.values():
            await module["initialized_class"].on_member_unban(guild, user)

    async def on_group_join(self, channel, user):
        for module in self.modules.values():
            await module["initialized_class"].on_group_join(channel, user)

    async def on_group_remove(self, channel, user):
        for module in self.modules.values():
            await module["initialized_class"].on_group_remove(channel, user)

    async def on_relationship_add(self, relationship):
        for module in self.modules.values():
            await module["initialized_class"].on_relationship_add(relationship)

    async def on_relationship_remove(self, relationship):
        for module in self.modules.values():
            await module["initialized_class"].on_relationship_remove(relationship)

    async def on_relationship_update(self, before, after):
        for module in self.modules.values():
            await module["initialized_class"].on_relationship_update(before, after)

    async def on_connect(self):
        for module in self.modules.values():
            await module["initialized_class"].on_connect()

    async def on_shard_ready(self):
        for module in self.modules.values():
            await module["initialized_class"].on_shard_ready()

    async def on_resumed(self):
        for module in self.modules.values():
            await module["initialized_class"].on_resumed()

    async def on_error(self, event, *args, **kwargs):
        print(event, *args, **kwargs)
        print(traceback.format_exc())
        for module in self.modules.values():
            await module["initialized_class"].on_error(event, *args, **kwargs)

    async def on_guild_integrations_update(self, guild):
        for module in self.modules.values():
            await module["initialized_class"].on_guild_integrations_update(guild)

    async def on_webhooks_update(self, channel):
        for module in self.modules.values():
            await module["initialized_class"].on_webhooks_update(channel)


client = NikolaTesla()
# prefix = '/'
# modules = {}  # format : {'modulename':[module, initializedclass]}
# owners = [281166473102098433]
#
#
# async def auth(user, module_name):
#     if user.id in owners:
#         return True
#     try:
#         modules[module_name][1].authlist
#     except ValueError:
#         return True
#     for guild in client.guilds:
#         if guild.get_member(user.id):
#             for roleid in modules[module_name][1].authlist:
#                 if roleid in [r.id for r in guild.get_member(user.id).roles]:
#                     return True
client.run(os.environ['DISCORD_TOKEN'], max_messages=500000)
