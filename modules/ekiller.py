# -*-coding:utf-8 -*
#!/usr/bin/python3

import random
import discord
import utils.perms
import utils.usertools
import settings.ekiller
async def commandHandler(client, message, ekiller):

    if message.content.startswith("/ekiller quit"):
        await remove_player(client, message, ekiller)
    try :
        if message.content.startswith("/ekiller") and (not utils.perms.hasrole(message.author, settings.ekiller.auth)) :
            await client.send_message(message.channel, message.author.mention + ", vous n'avez pas la permission d'effectuer cette commande.")
            return
    except :
        if message.content.startswith("/ekiller") :
            await client.send_message(message.channel, message.author.mention + ", Une erreur s'est produite. \n\nPS: les commandes ayant un rapport avec ekiller doivent être éffectuées sur le serveur.")
            raise

    elif message.content.startswith("/ekiller addplayer"):
        await addplayerbyid(client, message, ekiller)

    elif message.content.startswith("/ekiller removeplayer"):
        await delplayerbyid(client, message, ekiller)

    if message.content == "/ekiller join":
        await add_player(client, message, ekiller)

    elif message.content.startswith("/ekiller add"):
        args = message.content.split(' ')
        if len(args) == 3:
            for e in args[2].split(','):
                await add_word(client, message, ekiller, e)
            await client.send_message(message.channel, message.author.mention + ", le(s) mot(s) `{0}` a bien été ajouté.".format(args[2]))
        else:
            await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique mot ou une liste de mots séparés par des virgules.")

    elif message.content.startswith("/ekiller remove"):
        args = message.content.split(' ')
        if len(args) == 3:
            await remove_word(client, message, ekiller, args[2])
        else:
            await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique mot.")

    elif message.content == "/ekiller players":
        await print_players(client, message, ekiller)

    elif message.content == "/ekiller words":
        await print_words(client, message, ekiller)

    elif message.content == "/ekiller start":
        await start(client, message, ekiller)

    elif message.content == "/ekiller reset players":
        await reset_players(client, message, ekiller)

    elif message.content == "/ekiller reset words":
        await reset_words(client, message, ekiller)



async def add_player(client, message, ekiller):
    if message.author not in ekiller.players:
        ekiller.players.append(message.author)
    await client.send_message(message.channel, message.author.mention + ", vous avez bien été ajouté à la liste des participants.")

async def remove_player(client, message, ekiller):
    if message.author in ekiller.players:
        ekiller.players.remove(message.author)
    await client.send_message(message.channel, message.author.mention + ", vous avez bien été retiré de la liste des participants.")

async def print_players(client, message, ekiller):
    players = [p.display_name for p in ekiller.players]
    await client.send_message(message.channel, "Liste des joueurs :")
    await client.send_message(message.channel, "```PYTHON\n" + str(players) + "\n```")

async def add_word(client, message, ekiller, word):
    ekiller.words.append(word)

async def remove_word(client, message, ekiller, word):
    if word in ekiller.words:
        ekiller.words.remove(word)
        await client.send_message(message.channel, message.author.mention + ", le mot `{0}` a bien été supprimé.".format(word))
    else:
        await client.send_message(message.channel, message.author.mention + ", le mot `{0}` n'existe pas.".format(word))

async def print_words(client, message, ekiller):
    words = [ekiller.words[i:i+100] for i in range(0, len(ekiller.words), 100)]
    await client.send_message(message.channel, "Liste des mots :")
    for w in words:
        await client.send_message(message.channel, "```PYTHON\n" + str(w) + "\n```")

async def start(client, message, ekiller):
    players = [p for p in ekiller.players]
    random.shuffle(players)
    players.append(players[0])
    for i in range(len(players)-1):
        word = random.choice(ekiller.words)
        embed = discord.Embed(title="E-KILLER", description="Votre cible est : " + players[i+1].display_name + "\nLe mot est : `" + word + "`\n\nBonne chance à vous.", color=0x0000ff)
        await client.send_message(players[i], embed=embed)
    embed = discord.Embed(title="E-KILLER", description="Liste des joueurs :\n" + str([p.display_name for p in ekiller.players]) + "\n\n Bonne chance à tous !", color=0x0000ff)
    await client.send_message(message.channel, embed=embed)

async def reset_players(client, message, ekiller):
    ekiller.players = []
    await client.send_message(message.channel, "Les participants à la partie de E-Killer ont été réinitialisés.")

async def reset_words(client, message, ekiller):
    ekiller.words = []
    await client.send_message(message.channel, "Les mots de la partie de E-Killer ont été réinitialisés.")

async def addplayerbyid(client, message, ekiller):
    args=message.content.split(' ')
    if len(args)==3:
        member = False
        try :
            member = await utils.usertools.UserByID(client, args[2])
        except :
            pass
        if member == False :
            await client.send_message(message.channel, message.author.mention + ", l'ID que vous avez donné est invalide.")
        else :
            ekiller.players.append(member)
    else :
        await client.send_message(message.channel, message.author.mention + ", veuillez péciser un seul et unique ID.")

async def delplayerbyid(client, message, ekiller):
    args=message.content.split(' ')
    if len(args)==3:
        member = False
        try :
            member = await utils.usertools.UserByID(client, args[2])
        except :
            pass
        if member == False :
            await client.send_message(message.channel, message.author.mention + ", l'ID que vous avez donné est invalide.")
        else :
            ekiller.players.remove(member)
    else :
        await client.send_message(message.channel, message.author.mention + ", veuillez péciser un seul et unique ID.")
class Ekiller:

    def __init__(self):
        self.players = []
        self.words = []
