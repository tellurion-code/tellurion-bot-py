import discord
import asyncio
import random

from modules.codenames.game import Game
from modules.codenames.player import Player
from modules.codenames.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.codenames.globals as globals
globals.init()

class MainClass(BaseClassPython):
    name = "Codenames"
    help_active = True
    help = {
        "description": "Module du jeu Codenames",
        "commands": {
            "`{prefix}{command} join`": "Rejoint la partie de Codenames. S'il n'y en a pas dans le salon, en crée une nouvelle.",
            "`{prefix}{command} quit`": "Quitte la partie de Codenames",
            "`{prefix}{command} start`": "Démarre la partie de Codenames",
            "`{prefix}{command} players`": "Affiche les joueurs de la partie de Codenames",
        }
    }
    color = 0x880088
    command_text = "codenames"

    def __init__(self, client):
        super().__init__(client)

    async def com_join(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == "none":
                if message.author.id in game.players:
                    await message.channel.send("Vous êtes déjà dans la partie")
                else:
                    await message.channel.send("<@" + str(message.author.id) + "> a rejoint la partie")

                    game.players[message.author.id] = Player(message.author)
        else:
            embed = discord.Embed(title = "Démarrage de la partie de Codenames",
                description = "Tapez %codenames join pour rejoindre la partie",
                color = self.color)

            await message.channel.send(embed = embed)

            globals.games[message.channel.id] = Game(message)

    #Quitter la partie
    async def com_quit(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == "none":
                if message.author.id in game.players:
                    await message.channel.send(message.author.mention + " a quitté la partie")

                    del game.players[message.author.id]

                    if len(game.players) == 0:
                        globals.games.pop(message.channel.id)
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Liste des joueurs
    async def com_players(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == "none":
                embed = discord.Embed(
                    title = "Liste des joueurs (" + str(len(globals.games[message.channel.id].players)) + ")",
                    color = self.color,
                    description = "```" + ', '.join([str(self.client.get_user(x)) for x, y in globals.games[message.channel.id].players.items()]) + "```"
                )
                await message.channel.send(embed = embed)
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_reset(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == "none":
                await message.channel.send("La partie a été réinitialisée")
                globals.games.pop(message.channel.id)
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_start(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == "none":
                if message.author.id in game.players:
                    if len(game.players) >= 4 or globals.debug:
                        await game.start_game()
                    else:
                        await message.channel.send("Il faut au minimum 4 joueurs")
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_send(self, message, args, kwargs):
        if not message.guild:
            done = False
            for game in globals.games.values():
                if message.author.id in game.players:
                    if message.author.id in game.spy_masters:
                        done = True
                        if game.players[message.author.id].team == game.turn:
                            if game.hint == "":
                                if len(args) == 3:
                                    try:
                                        affected = int(args[2])
                                    except:
                                        await message.author.send("Le nombre de mots concernés est invalide")
                                    else:
                                        game.hint = args[1]
                                        game.affected = affected
                                        await game.send_info()
                                        await message.author.send("Vous pouvez utiliser %codenames reveal pour révéler les mots, et %codenames pass pour passer votre tour")
                                        #await game.players[message.author.id].send_tile_choice(game)
                                else:
                                    await message.author.send("Vous devez spécifier juste un indice et le nombre de mots concernés")
                            else:
                                await message.author.send("Tu as déjà envoyé un indice")
                        else:
                            await message.author.send("Ce n'est pas ton tour")
                    else:
                        await message.author.send("Tu n'es pas un Spy Master")

            if not done:
                await message.author.send("Il n'y a pas de partie en cours")
        else:
            await message.channel.send("Cette commande est à envoyer en DM")

    async def com_reveal(self, message, args, kwargs):
        if not message.guild:
            done = False
            for game in globals.games.values():
                if message.author.id in game.players:
                    if message.author.id in game.spy_masters:
                        done = True
                        if game.players[message.author.id].team == game.turn:
                            if game.hint != "":
                                if len(args) == 2:
                                    try:
                                        card = game.board.index(card)
                                    except:
                                        await message.author.send("Il n'y a pas de cartes avec ce nom. Vérifiez que le mot est en minuscules et sans accents")
                                    else:
                                        game.revealed[card] = game.colors[card]
                                        if game.colors[card] == game.turn:
                                            await game.check_if_win()
                                        elif game.colors[card] == "black":
                                            await game.end_game(False)
                                        else:
                                            game.turn = "blue" if game.turn == "red" else "red"
                                            game.hint = ""
                                            await game.send_info()
                                else:
                                    await message.author.send("Vous devez spécifier juste un mot")
                            else:
                                await message.author.send("Tu n'as pas envoyé un indice")
                        else:
                            await message.author.send("Ce n'est pas ton tour")
                    else:
                        await message.author.send("Tu n'es pas un Spy Master")

            if not done:
                await message.author.send("Il n'y a pas de partie en cours")
        else:
            await message.channel.send("Cette commande est à envoyer en DM")

    async def com_pass(self, message, args, kwargs):
        if not message.guild:
            done = False
            for game in globals.games.values():
                if message.author.id in game.players:
                    if message.author.id in game.spy_masters:
                        done = True
                        if game.players[message.author.id].team == game.turn:
                            if game.hint != "":
                                game.turn = "blue" if game.turn == "red" else "red"
                                game.hint = ""
                                await game.send_info()
                            else:
                                await message.author.send("Tu n'as pas envoyé un indice")
                        else:
                            await message.author.send("Ce n'est pas ton tour")
                    else:
                        await message.author.send("Tu n'es pas un Spy Master")

            if not done:
                await message.author.send("Il n'y a pas de partie en cours")
        else:
            await message.channel.send("Cette commande est à envoyer en DM")

    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            globals.debug = not globals.debug
            await message.channel.send("Debug: " + str(globals.debug))

    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            for message in globals.reaction_messages:
                if message.message.id == reaction.message.id:
                    if  reaction.emoji in message.number_emojis:
                        if message.check(reaction, user):
                            await message.add_reaction(reaction, user)
                        else:
                            await message.message.remove_reaction(reaction, user)
                    else:
                        await message.message.remove_reaction(reaction, user)

    async def on_reaction_remove(self, reaction, user):
        if not user.bot:
            for message in globals.reaction_messages:
                if user.id in message.reactions:
                    if message.number_emojis.index(reaction.emoji) in message.reactions[user.id]:
                        if message.check(reaction, user) and message.message.id == reaction.message.id:
                            await message.remove_reaction(reaction, user)
