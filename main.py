#!/usr/bin/python3
import discord #pip3 install --user discord[voice]
import asyncio
import os
import pickle

import settings
import modules
import utils.perms
#init
client = discord.Client(max_messages=100000)
hitlerGame=modules.hitler.HitlerSave()
ekiller = modules.ekiller.Ekiller()
ekiller2 = modules.ekiller2.Ekiller()
avalonGame=modules.avalon.AvalonSave()
#funcs
@client.event
async def on_ready():
    if settings.login.enabled:
        await modules.login.print_user(client)
    if settings.newuser.enabled:
        await modules.newuser.initscan(client)
@client.event
async def on_message(message):
    allowed=True
    try:
        allowed=(not await utils.perms.hasrole(message.author, settings.eviewer)) or ( not settings.restriction ) or message.author.id in settings.owners
    except:
        pass
    if allowed :
        if settings.archive.enabled:
            await modules.archive.specific(client, message)
            await modules.archive.everyOfGuild(client, message)
        if settings.dellog.enabled:
            await modules.dellog.send_logs(client, message)
        if settings.restart.enabled:
            await modules.restart.restart_py(client, message)
        if settings.hitler.enabled:
            await modules.hitler.commandHandler(client, message, hitlerGame)
        if settings.roles.enabled:
            await modules.roles.AddRole(client, message)
        if settings.licorne.enabled:
            await modules.licorne.Licorne(client, message)
        if settings.ekiller.enabled:
            await modules.ekiller.commandHandler(client, message, ekiller)
        if settings.ekiller2.enabled:
            await modules.ekiller2.commandHandler(client, message, ekiller2)
        if settings.testing.enabled:
            await modules.testing.testsHandler(client, message)
        if settings.avalon.enabled:
            await modules.avalon.commandHandler(client, message, avalonGame)

@client.event
async def on_message_delete(message):
    if settings.dellog.enabled:
        await modules.dellog.log_deleted(client, message)

@client.event
async def on_reaction_add(reaction, user):
    if settings.hitler.enabled:
        await modules.hitler.voteHandler(client, reaction, user, hitlerGame)
    if settings.avalon.enabled:
        await modules.avalon.reactionHandler(client, reaction, user, avalonGame, 'add')

@client.event
async def on_reaction_remove(reaction, user):
    if settings.avalon.enabled:
        await modules.avalon.reactionHandler(client, reaction, user, avalonGame, 'remove')
@client.event
async def on_error(event, *args, **kwargs):
    if settings.embederror.enabled :
        await modules.embederror.sendError(client, event, *args, **kwargs)

@client.event
async def on_member_join(member):
    if settings.newuser.enabled:
        await modules.newuser.addrole(client, member)

#run
client.run(os.environ['DISCORD_TOKEN'])
