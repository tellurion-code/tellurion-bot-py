#!/usr/bin/python3
from modules import *
@client.event
async def on_ready():
	await login.print_user(client)

@client.event
async def on_message(message):
	if settings.c_archive.enabled:
		await archive.specific(client, message)
		await archive.everyOfGuild(client, message)
	if settings.c_dellog.enabled:
		await dellog.send_logs(client, message)
	if settings.c_restart.enabled:
		await restart.restart_py(client, message)
@client.event
async def on_message_delete(message):
	if settings.c_dellog.enabled:
		await dellog.log_deleted(client, message)
client.run(os.environ['DISCORD_TOKEN'])
