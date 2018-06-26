# -*-coding:utf-8 -*
#!/usr/bin/python3

import random
import datetime
import time
from subprocess import call
import discord

import utils.perms
import utils.usertools
import settings.ekiller
import settings.dellog

try:
    call(['mkdir', 'tmp'])
except:
    pass

async def commandHandler(client, message, ekiller):

    try :
        if message.content.startswith("/ekiller") and (not await utils.perms.hasrole(message.author, settings.ekiller.auth)) :
            await client.send_message(message.channel, message.author.mention + ", vous n'avez pas la permission d'effectuer cette commande.")
            return
    except :
        if message.content.startswith("/ekiller") :
            await client.send_message(message.channel, message.author.mention + ", Une erreur s'est produite. \n\nPS: les commandes ayant un rapport avec ekiller doivent être éffectuées sur le serveur.")
            raise

    if message.content == "/ekiller start":
        await start(client, message, ekiller)

    elif message.content == "/ekiller join":
        await players_join(client, message, ekiller)

    elif message.content == "/ekiller quit":
        await players_quit(client, message, ekiller)

    elif message.content.startswith("/ekiller players add"):
        await players_add(client, message, ekiller)

    elif message.content.startswith("/ekiller players remove"):
        await players_remove(client, message, ekiller)

    elif message.content == "/ekiller players list":
        await players_list(client, message, ekiller)

    elif message.content == "/ekiller players reset":
        await players_reset(client, message, ekiller)

    elif message.content.startswith("/ekiller words add"):
        await words_add(client, message, ekiller)

    elif message.content.startswith("/ekiller words remove"):
        await words_remove(client, message, ekiller)

    elif message.content == "/ekiller words list":
        await words_list(client, message, ekiller)

    elif message.content == "/ekiller words reset":
        await words_reset(client, message, ekiller)

    elif message.content == "/ekiller logs":
        await logs(client, message)

    elif message.content == "/ekiller help":
        await help(client, message)


async def start(client, message, ekiller):
    game = []
    players = [p for p in ekiller.players]
    random.shuffle(players)
    players.append(players[0])
    for i in range(len(players)-1):
        word = random.choice(ekiller.words)
        dic = {"ekiller":players[i], "target":players[i+1], "word":word}
        game.append(dic)
        embed = discord.Embed(title="E-KILLER", description="Votre cible est : " + players[i+1].display_name + "\n\nLe mot est : `" + word + "`\n\nBonne chance à vous.", color=0x0000ff)
        await client.send_message(players[i], embed=embed)
    embed = discord.Embed(title="E-KILLER", description="Liste des joueurs :\n" + str([p.display_name for p in ekiller.players]) + "\n\n Bonne chance à tous !", color=0x0000ff)
    await client.send_message(message.channel, embed=embed)
    with open("tmp/ekillerLog.txt", "a") as ekillerlogfile:
        ekillerlogfile.write(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " [" + str(game) + "]\n")

async def players_join(client, message, ekiller):
    if message.author not in ekiller.players:
        ekiller.players.append(message.author)
    await client.send_message(message.channel, message.author.mention + ", vous avez bien été ajouté à la liste des participants.")

async def players_quit(client, message, ekiller):
    if message.author in ekiller.players:
        ekiller.players.remove(message.author)
    await client.send_message(message.channel, message.author.mention + ", vous avez bien été retiré de la liste des participants.")

async def players_add(client, message, ekiller):
    args = message.content.split(' ')
    if len(args) == 4:
        ids = args[3].split(',')
        for id in ids:
            member = await utils.usertools.UserByID(client, id)
            if not member:
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` n'existe pas.".format(member.display_name))
            elif member in ekiller.players:
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` participe déjà.".format(member.display_name))
            else:
                ekiller.players.append(member)
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` a bien été ajouté.".format(member.display_name))
    else:
        await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique id ou une liste d'ids séparés par une virgule.")

async def players_remove(client, message, ekiller):
    args = message.content.split(' ')
    if len(args) == 4:
        ids = args[3].split(',')
        for id in ids:
            member = await utils.usertools.UserByID(client, id)
            if not member:
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` n'existe pas.".format(member.display_name))
            elif member not in ekiller.players:
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` ne participe pas.".format(member.display_name))
            else:
                ekiller.players.remove(member)
                await client.send_message(message.channel, message.author.mention + ", le joueur `{0}` a bien été retiré.".format(member.display_name))
    else:
        await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique id ou une liste d'ids séparés par une virgule.")

async def players_list(client, message, ekiller):
    players = [p.display_name for p in ekiller.players]
    await client.send_message(message.channel, "Liste des joueurs :")
    await client.send_message(message.channel, "```PYTHON\n" + str(players) + "\n```")

async def players_reset(client, message, ekiller):
    ekiller.players = []
    await client.send_message(message.channel, message.author.mention + ", la liste des participants a bien été réinitialisée.")

async def words_add(client, message, ekiller):
    args = message.content.split(' ')
    if len(args) == 4:
        words = args[3].lower().split(',')
        for w in words:
            if w not in ekiller.words:
                ekiller.words.append(w)
        if len(words) == 1:
            await client.send_message(message.channel, message.author.mention + ", le mot `{0}` a bien été ajouté.".format(args[3]))
        else:
            await client.send_message(message.channel, message.author.mention + ", les mots `{0}` ont bien été ajoutés.".format(args[3]))
    else:
        await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique mot ou une liste de mots séparés par une virgule.")

async def words_remove(client, message, ekiller):
    args = message.content.split(' ')
    if len(args) == 4:
        words = args[3].lower().split(',')
        for w in words:
            if w in ekiller.words:
                ekiller.words.remove(w)
        if len(words) == 1:
            await client.send_message(message.channel, message.author.mention + ", le mot `{0}` a bien été retiré.".format(args[3]))
        else:
            await client.send_message(message.channel, message.author.mention + ", les mots `{0}` ont bien été retirés.".format(args[3]))
    else:
        await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique mot ou une liste de mots séparés par une virgule.")

async def words_list(client, message, ekiller):
    words = [ekiller.words[i:i+100] for i in range(0, len(ekiller.words), 100)]
    await client.send_message(message.channel, "Liste des mots :")
    for w in words:
        await client.send_message(message.channel, "```PYTHON\n" + str(w) + "\n```")

async def words_reset(client, message, ekiller):
    ekiller.words = []
    await client.send_message(message.channel, message.author.mention + ", la liste des mots a bien été réinitialisée.")

async def logs(client, message):
    if not (message.author == client.user) and await utils.perms.hasrole(message.author, settings.dellog.logsAuth) :
        try:
            await client.delete_message(message)
            await client.send_file(message.author, "tmp/ekillerLog.txt")
        except:
            await client.send_message(message.author, "```FAILED```")

async def help(client, message):
    text = "Liste des commandes :\n\n"
    text += "/ekiller join\nRejoindre la partie\n\n"
    text += "/ekiller quit\nQuitter la partie la partie\n\n"
    text += "/ekiller players list\nAfficher la liste des participants\n\n"
    text += "/ekiller words add foo,bar\najouter des mots\n\n"
    text += "/ekiller words list\nAfficher la liste des mots\n\n"
    text += "/ekiller start\nLancer la partie\n\n"
    embed = discord.Embed(title="E-KILLER", description=text, color=0x0000ff)
    await client.send_message(message.channel, embed=embed)


class Ekiller:

    def __init__(self):
        self.players = []
        self.words = []
