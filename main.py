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
if modules.saving.saveExists("hitlerGame"):
    hitlerGame=modules.saving.loadObject("hitlerGame")
else:
    hitlerGame=modules.hitler.HitlerSave()
if modules.saving.saveExists("ekiller"):
    ekiller=modules.saving.loadObject("ekiller")
else:
    ekiller= modules.ekiller.Ekiller()
if modules.saving.saveExists("ekiller2"):
    ekiller2=modules.saving.loadObject("ekiller2")
else:
    ekiller2= modules.ekiller2.Ekiller()
if modules.saving.saveExists("avalonGame"):
    avalonGame=modules.saving.loadObject("avalonGame")
else:
    avalonGame=modules.avalon.AvalonSave()

#funcs
@client.event
async def on_ready():
    if settings.login.enabled:
        await modules.login.print_user(client)
    if settings.newuser.enabled:
        await modules.newuser.initscan(client)
    if settings.avalon.enabled:
        if avalonGame.status=='composition':
            playerstr=""
            for i in range(len(avalonGame.actors)):
                playerstr+=" {0} `{1}`\n".format(avalonGame.emotes[i], avalonGame.actors[i]['user'].display_name + '#' + str(avalonGame.actors[i]['user'].discriminator))
            for i in range(len(avalonGame.actors)):
                if i==avalonGame.leader:
                    avalonGame.leadmsg = await client.send_message(avalonGame.actors[i]['user'], embed=discord.Embed(title="[AVALON] - Composition de l'équipe - Quête n°" + str(len(avalonGame.quests) + 1), description="Vous êtes le leader, vous devez choisir une équipe. Ajoutez les réactions correspondantes, puis validez.\n\nListe des joueurs :\n{0}".format(playerstr), color=0xddc860))
            for emote in avalonGame.emotes[:len(avalonGame.actors):]:
                await client.add_reaction(avalonGame.leadmsg, emote)
            await avalonGame.updateTeam(client)
        if avalonGame.status=='voting':
            await avalonGame.voteStage(client)
        if avalonGame.status=='expedition':
            await expeditionStart(client)
        if avalonGame.status=='assassination':
            await assassinationStart(client)
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
