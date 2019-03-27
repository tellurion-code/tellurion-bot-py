#!/usr/bin/python3
import importlib
import os
import traceback

import discord

client = discord.Client()
prefix = '/'
modules = {}  # format : {'modulename':[module, initializedclass]}
owners = [281166473102098433] #non-staff Should **not** be on this list on the master branch


async def auth(user, module_name):
    if user.id in owners:
        return True
    try:
        modules[module_name][1].authlist
    except:
        return True
    for guild in client.guilds:
        if guild.get_member(user.id):
            for roleid in modules[module_name][1].authlist:
                if roleid in [r.id for r in guild.get_member(user.id).roles]:
                    return True


@client.event
async def on_ready():
    print("Bienvenue, {0.user}, l'heure est venue d'e-penser.".format(client))
    panic = False
    error = None

    async def panic_load():
        print("--PANIC LOAD--")
        panic = True
        modules = {}
        for filename in os.listdir('modules'):
            if filename.endswith('.py'):
                try:
                    modules.update({filename[:-3:]: [importlib.import_module('modules.' + filename[:-3:])]})
                    print("Module {0} chargé.".format(filename[:-3:]))
                except:
                    print("[ERROR] Le module {0} n'a pas pu être chargé.".format(filename))
        # initialisation
        for module_name in list(modules.keys()):
            try:
                modules[module_name].append(modules[module_name][0].MainClass(client, modules, owners, prefix))
                print("Module {0} initialisé.".format(module_name))
            except:
                print("[ERROR] Le module {0} n'a pas pu être initialisé.".format(module_name))
                modules.pop(module_name, None)

    if 'modules.py' in os.listdir('modules'):
        try:
            modules.update({'modules': [importlib.import_module('modules.' + 'modules')]})
            print("Module {0} chargé.".format('modules'))
            try:
                modules['modules'].append(modules['modules'][0].MainClass(client, modules, owners, prefix))
                print("Module {0} initialisé.".format('modules'))
                try:
                    await modules['modules'][1].on_ready()
                except Exception as e:
                    error = e
            except Exception as e:
                print("[ERROR] Le module {0} n'a pas pu être initialisé.".format('modules'))
                await panic_load()
                error = e
        except Exception as e:
            print("[ERROR] Le module {0} n'a pas pu être chargé.".format('modules.py'))
            await panic_load()
            error = e
    else:
        await panic_load()

    if panic:
        for moduleName in list(modules.keys()):
            if 'on_ready' in modules[moduleName][1].events:
                await modules[moduleName][1].on_ready()
    else:
        for moduleName in list(modules.keys()):
            if (not moduleName == 'modules') and 'on_ready' in modules[moduleName][1].events:
                await modules[moduleName][1].on_ready()
    if error:
        raise error


@client.event
async def on_error(event, *args, **kwargs):
    print(traceback.format_exc())
    for moduleName in list(modules.keys()):
        if 'on_error' in modules[moduleName][1].events:
            await modules[moduleName][1].on_error(event, *args, **kwargs)


@client.event
async def on_socket_raw_receive(msg):
    for moduleName in list(modules.keys()):
        if 'on_socket_raw_receive' in modules[moduleName][1].events:
            await modules[moduleName][1].on_socket_raw_receive(msg)


@client.event
async def on_socket_raw_send(payload):
    for moduleName in list(modules.keys()):
        if 'on_socket_raw_send' in modules[moduleName][1].events:
            await modules[moduleName][1].on_socket_raw_send(payload)


@client.event
async def on_typing(channel, user, when):
    for moduleName in list(modules.keys()):
        if 'on_typing' in modules[moduleName][1].events:
            await modules[moduleName][1].on_typing(channel, user, when)


@client.event
async def on_message(message):
    for moduleName in list(modules.keys()):
        if 'on_message' in modules[moduleName][1].events and message.content.startswith(modules[moduleName][1].command):
            if await auth(message.author, moduleName):
                await modules[moduleName][1].on_message(message)


@client.event
async def on_message_delete(message):
    for moduleName in list(modules.keys()):
        if 'on_message_delete' in modules[moduleName][1].events:
            await modules[moduleName][1].on_message_delete(message)


@client.event
async def on_raw_message_delete(payload):
    for moduleName in list(modules.keys()):
        if 'on_raw_message_delete' in modules[moduleName][1].events:
            await modules[moduleName][1].on_raw_message_delete(payload)


@client.event
async def on_raw_bulk_message_delete(payload):
    for moduleName in list(modules.keys()):
        if 'on_raw_bulk_message_delete' in modules[moduleName][1].events:
            await modules[moduleName][1].on_raw_bulk_message_delete(payload)


@client.event
async def on_message_edit(before, after):
    for moduleName in list(modules.keys()):
        if 'on_message_edit' in modules[moduleName][1].events:
            await modules[moduleName][1].on_message_edit(before, after)


@client.event
async def on_raw_message_edit(payload):
    for moduleName in list(modules.keys()):
        if 'on_raw_message_edit' in modules[moduleName][1].events:
            await modules[moduleName][1].on_raw_message_edit(payload)


@client.event
async def on_reaction_add(reaction, user):
    for moduleName in list(modules.keys()):
        if 'on_reaction_add' in modules[moduleName][1].events:
            await modules[moduleName][1].on_reaction_add(reaction, user)


@client.event
async def on_raw_reaction_add(payload):
    for moduleName in list(modules.keys()):
        if 'on_raw_reaction_add' in modules[moduleName][1].events:
            await modules[moduleName][1].on_raw_reaction_add(payload)


@client.event
async def on_reaction_remove(reaction, user):
    for moduleName in list(modules.keys()):
        if 'on_reaction_remove' in modules[moduleName][1].events:
            await modules[moduleName][1].on_reaction_remove(reaction, user)


@client.event
async def on_raw_reaction_remove(payload):
    for moduleName in list(modules.keys()):
        if 'on_raw_reaction_remove' in modules[moduleName][1].events:
            await modules[moduleName][1].on_raw_reaction_remove(payload)


@client.event
async def on_reaction_clear(message, reactions):
    for moduleName in list(modules.keys()):
        if 'on_reaction_clear' in modules[moduleName][1].events:
            await modules[moduleName][1].on_reaction_clear(message, reactions)


@client.event
async def on_raw_reaction_clear(payload):
    for moduleName in list(modules.keys()):
        if 'on_raw_reaction_clear' in modules[moduleName][1].events:
            await modules[moduleName][1].on_raw_reaction_clear(payload)


@client.event
async def on_private_channel_delete(channel):
    for moduleName in list(modules.keys()):
        if 'on_private_channel_delete' in modules[moduleName][1].events:
            await modules[moduleName][1].on_private_channel_delete(channel)


@client.event
async def on_private_channel_create(channel):
    for moduleName in list(modules.keys()):
        if 'on_private_channel_create' in modules[moduleName][1].events:
            await modules[moduleName][1].on_private_channel_create(channel)


@client.event
async def on_private_channel_update(before, after):
    for moduleName in list(modules.keys()):
        if 'on_private_channel_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_private_channel_update(before, after)


@client.event
async def on_private_channel_pins_update(channel, last_pin):
    for moduleName in list(modules.keys()):
        if 'on_private_channel_pins_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_private_channel_pins_update(channel, last_pin)


@client.event
async def on_guild_channel_delete(channel):
    for moduleName in list(modules.keys()):
        if 'on_guild_channel_delete' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_channel_delete(channel)


@client.event
async def on_guild_channel_create(channel):
    for moduleName in list(modules.keys()):
        if 'on_guild_channel_create' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_channel_create(channel)


@client.event
async def on_guild_channel_update(before, after):
    for moduleName in list(modules.keys()):
        if 'on_guild_channel_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_channel_update(before, after)


@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    for moduleName in list(modules.keys()):
        if 'on_guild_channel_pins_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_channel_pins_update(channel, last_pin)


@client.event
async def on_member_join(member):
    for moduleName in list(modules.keys()):
        if 'on_member_join' in modules[moduleName][1].events:
            await modules[moduleName][1].on_member_join(member)


@client.event
async def on_member_remove(member):
    for moduleName in list(modules.keys()):
        if 'on_member_remove' in modules[moduleName][1].events:
            await modules[moduleName][1].on_member_remove(member)


@client.event
async def on_member_update(before, after):
    for moduleName in list(modules.keys()):
        if 'on_member_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_member_update(before, after)


@client.event
async def on_guild_join(guild):
    for moduleName in list(modules.keys()):
        if 'on_guild_join' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_join(guild)


@client.event
async def on_guild_remove(guild):
    for moduleName in list(modules.keys()):
        if 'on_guild_remove' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_remove(guild)


@client.event
async def on_guild_update(before, after):
    for moduleName in list(modules.keys()):
        if 'on_guild_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_update(before, after)


@client.event
async def on_guild_role_create(role):
    for moduleName in list(modules.keys()):
        if 'on_guild_role_create' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_role_create(role)


@client.event
async def on_guild_role_delete(role):
    for moduleName in list(modules.keys()):
        if 'on_guild_role_delete' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_role_delete(role)


@client.event
async def on_guild_role_update(before, after):
    for moduleName in list(modules.keys()):
        if 'on_guild_role_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_role_update(before, after)


@client.event
async def on_guild_emojis_update(guild, before, after):
    for moduleName in list(modules.keys()):
        if 'on_guild_emojis_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_emojis_update(guild, before, after)


@client.event
async def on_guild_available(guild):
    for moduleName in list(modules.keys()):
        if 'on_guild_available' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_available(guild)


@client.event
async def on_guild_unavailable(guild):
    for moduleName in list(modules.keys()):
        if 'on_guild_unavailable' in modules[moduleName][1].events:
            await modules[moduleName][1].on_guild_unavailable(guild)


@client.event
async def on_voice_state_update(member, before, after):
    for moduleName in list(modules.keys()):
        if 'on_voice_state_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_voice_state_update(member, before, after)


@client.event
async def on_member_ban(guild, user):
    for moduleName in list(modules.keys()):
        if 'on_member_ban' in modules[moduleName][1].events:
            await modules[moduleName][1].on_member_ban(guild, user)


@client.event
async def on_member_unban(guild, user):
    for moduleName in list(modules.keys()):
        if 'on_member_unban' in modules[moduleName][1].events:
            await modules[moduleName][1].on_member_unban(guild, user)


@client.event
async def on_group_join(channel, user):
    for moduleName in list(modules.keys()):
        if 'on_group_join' in modules[moduleName][1].events:
            await modules[moduleName][1].on_group_join(channel, user)


@client.event
async def on_group_remove(channel, user):
    for moduleName in list(modules.keys()):
        if 'on_group_remove' in modules[moduleName][1].events:
            await modules[moduleName][1].on_group_remove(channel, user)


@client.event
async def on_relationship_add(relationship):
    for moduleName in list(modules.keys()):
        if 'on_relationship_add' in modules[moduleName][1].events:
            await modules[moduleName][1].on_relationship_add(relationship)


@client.event
async def on_relationship_remove(relationship):
    for moduleName in list(modules.keys()):
        if 'on_relationship_remove' in modules[moduleName][1].events:
            await modules[moduleName][1].on_relationship_remove(relationship)


@client.event
async def on_relationship_update(before, after):
    for moduleName in list(modules.keys()):
        if 'on_relationship_update' in modules[moduleName][1].events:
            await modules[moduleName][1].on_relationship_update(before, after)


client.run(os.environ['DISCORD_TOKEN'])
