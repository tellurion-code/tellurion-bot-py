#!/usr/bin/python3
import discord #pip3 install --user discord[voice]
import asyncio
import os

import settings
import modules
import utils.perms
#init
client = discord.Client(max_messages=100000)
hitlerGame=modules.hitler.HitlerSave()
#funcs
@client.event
async def on_ready():
	if settings.login.enabled:
		await modules.login.print_user(client)

@client.event
async def on_message(message):
	if (not await utils.perms.hasrole(message.author, settings.eviewer)) or ( not settings.restriction ) or message.author.id in settings.owners:
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
@client.event
async def on_message_delete(message):
	if settings.dellog.enabled:
		await modules.dellog.log_deleted(client, message)

@client.event
async def on_reaction_add(reaction, user):
	if settings.hitler.enabled:
		await modules.hitler.voteHandler(client, reaction, user, hitlerGame)

@client.event
async def on_error(event, *args, **kwargs):
	if settings.embederror.enabled :
		await modules.embederror.sendError(client, event, *args, **kwargs)

#run
client.run(os.environ['DISCORD_TOKEN'])
