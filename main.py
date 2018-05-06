#!/usr/bin/python3
import discord
import asyncio
import settings
import modules
import os
client = discord.Client(max_messages=100000)
@client.event
async def on_ready():
	if settings.login.enabled:
		await modules.login.print_user(client)

@client.event
async def on_message(message):
	if settings.archive.enabled:
		await modules.archive.specific(client, message)
		await modules.archive.everyOfGuild(client, message)
	
	if settings.dellog.enabled:
		await modules.dellog.send_logs(client, message)
	
	if settings.restart.enabled:
		await modules.restart.restart_py(client, message)

@client.event
async def on_message_delete(message):
	if settings.dellog.enabled:
		await modules.dellog.log_deleted(client, message)
client.run(os.environ['DISCORD_TOKEN'])
