# -*-coding:utf-8 -*
#!/usr/bin/python3

import random
import datetime
import time
from subprocess import call
import discord

import utils.perms
import utils.usertools
import settings.ekiller2
import settings.dellog

try:
    call(['mkdir', 'tmp'])
except:
    pass

async def commandHandler(client, message, ekiller):

    try:
        if message.content.startswith("/ekiller") and (not await utils.perms.hasrole(message.author, settings.ekiller.auth)):
            await client.send_message(message.channel, message.author.mention + ", vous n'avez pas la permission d'effectuer cette commande.")
            return
    except:
        if message.content.startswith("/ekiller"):
            await client.send_message(message.channel, message.author.mention + ", Une erreur s'est produite. \n\nPS: les commandes ayant un rapport avec ekiller doivent être éffectuées sur le serveur.")
            raise

    if message.content == "/ekiller start":
        await start(client, message, ekiller)

    elif message.content.startswith("/ekiller join"):
        await join(client, message, ekiller)

    elif message.content == "/ekiller quit":
        await quit(client, message, ekiller)

    elif message.content.startswith("/ekiller kick"):
        await kick(client, message, ekiller)

    elif message.content == "/ekiller players":
        await players(client, message, ekiller)

    elif message.content == "/ekiller reset":
        await reset(client, message, ekiller)

    elif message.content == "/ekiller logs":
        await logs(client, message)

    elif message.content == "/ekiller help":
        await help(client, message)

    elif message.content == "/ekiller debug":
        await debug(client, message, ekiller)

async def start(client, message, ekiller):
    game = []
    players = []
    words = []
    for (id, word) in ekiller.buffer:
        member = await utils.usertools.UserByID(client, id)
        players.append(member)
        words.append(word)
    random.shuffle(players)
    players.append(players[0])
    random.shuffle(words)
    for i in range(len(players)-1):
        dic = {"ekiller":str(players[i].id)+'#'+players[i].name, "target":str(players[i+1].id)+'#'+players[i+1].name, "word":words[i]}
        game.append(dic)
        embed = discord.Embed(title="E-KILLER", description="Votre cible est : " + players[i+1].display_name + "\nLe mot est : `" + words[i] + "`\n\nBonne chance à vous.", color=0x0000ff)
        await client.send_message(players[i], embed=embed)
    embed = discord.Embed(title="E-KILLER", description="Liste des joueurs :\n" + str([p.display_name for p in ekiller.players]) + "\n\n Bonne chance à tous !", color=0x0000ff)
    await client.send_message(message.channel, embed=embed)
    with open("tmp/ekillerLog.txt", "a") as ekillerlogfile:
        ekillerlogfile.write(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " [" + str(game) + "]\n")

async def join(client, message, ekiller):
    args = message.content.split(' ')
    if len(args) == 3:
        if message.author.id in dict(ekiller.buffer):
            await client.send_message(message.channel, message.author.mention + ", vous faites déjà parti des participants.")
        else:
            ekiller.buffer.append((message.author.id, args[2]))
            await client.send_message(message.channel, message.author.mention + ", vous avez bien été ajouté à la liste des participants.")
    else:
        await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique mot que vous souhaitez ajouter à la liste : `/ekiller join <word>`")

async def quit(client, message, ekiller):
    if message.author.id in dict(ekiller.buffer):
        ekiller.buffer = [(id,word) for (id,word) in ekiller.buffer if id!=message.author.id]
        await client.send_message(message.channel, message.author.mention + ", vous avez bien été retiré de la liste des participants.")
    else:
        await client.send_message(message.channel, message.author.mention + ", vous ne faites pas parti des participants.")

async def kick(client, message, ekiller):
    args = message.content.split(' ')
    if len(args) == 4:
        ids = args[3].split(',')
        for id in ids:
            member = await utils.usertools.UserByID(client, id)
            if not member:
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` n'existe pas.".format(id))
            elif id not in dict(ekiller.buffer):
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` ne participe pas.".format(member.display_name))
            else:
                ekiller.buffer = [(idd, word) for (idd, word) in ekiller.buffer if idd != id]
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` a bien été retiré.".format(member.display_name))
    else:
        await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique id ou une liste d'ids séparés par une virgule.")

async def players(client, message, ekiller):
    players = []
    for (id, word) in ekiller.buffer:
        member = await utils.usertools.UserByID(client, id)
        players.append(member.display_name)
    await client.send_message(message.channel, "Liste des joueurs :")
    await client.send_message(message.channel, "```PYTHON\n" + str(players) + "\n```")

async def reset(client, message, ekiller):
    ekiller.buffer = []
    await client.send_message(message.channel, message.author.mention + ", le jeu a bien été réinitialisé.")

async def logs(client, message):
    if not (message.author == client.user) and await utils.perms.hasrole(message.author, settings.dellog.logsAuth):
        try:
            await client.delete_message(message)
            await client.send_file(message.author, "tmp/ekillerLog.txt")
        except:
            await client.send_message(message.author, "```FAILED```")

async def help(client, message):
    text = "Liste des commandes :\n\n"
    text += "/ekiller join <word>\nRejoindre la partie et ajouter le mot <word> à la liste de mots\n\n"
    text += "/ekiller quit\nQuitter la partie la partie\n\n"
    text += "/ekiller players\nAfficher la liste des participants\n\n"
    text += "/ekiller start\nLancer la partie\n\n"
    text += "/ekiller help\nAffiche cette aide\n\n"
    embed = discord.Embed(title="E-KILLER", description=text, color=0x0000ff)
    await client.send_message(message.channel, embed=embed)

async def debug(client, message, ekiller):
        await client.send_message(message.channel, message.author.mention + "```PYTHON\n" + str(ekiller.buffer) + "\n```")


class Ekiller2:

    def __init__(self):
        self.buffer = []
