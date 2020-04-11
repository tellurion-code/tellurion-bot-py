import sys
import discord
import asyncio

from modules.nosferatu.game import Game
from modules.nosferatu.reaction_message import ReactionMessage
from modules.nosferatu.roles import Renfield, Vampire, Hunter
from modules.base import BaseClassPython

import modules.nosferatu.globals as globals
globals.init()

class MainClass(BaseClassPython):
    name = "Nosferatu"
    help_active = True
    help = {
        "description": "Module du jeu Nosferatu",
        "commands": {
            "`{prefix}{command} join`": "Démarre ou rejoint la partie de Nosferatu",
            "`{prefix}{command} quit`": "Quitte la partie de Nosferatu",
            "`{prefix}{command} start`": "Démarre la partie de Nosferatu",
            "`{prefix}{command} players`": "Affiche les joueurs de la partie de Nosferatu",
            "`{prefix}{command} reset`": "Reset la partie de Nosferatu"
        }
    }
    color = 0xff0000
    command_text = "nosferatu"

    def __init__(self, client):
        super().__init__(client)

    async def command(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if args[0] == "join't" and game.turn == -1:
                await message.channel.send(message.author.mention + " n'a pas rejoint la partie")

    #Rejoindre la partie
    async def com_join(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    await message.channel.send("Vous êtes déjà dans la partie")
                elif len(game.players) < 8:
                    await message.channel.send(message.author.mention + " a rejoint la partie")

                    game.players[message.author.id] = Hunter(message.author)
                else:
                    await message.channel.send("Il y a déjà le nombre maximum de joueurs (8)")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            embed = discord.Embed(title = "Démarrage de la partie de Nosferatu",
                                description = "Tapez %nosferatu join pour rejoindre la partie",
                                color = self.color)

            await message.channel.send(embed = embed)

            globals.games[message.channel.id] = Game(message)

    #Quitter la partie
    async def com_quit(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if game.players[message.author.id].role == "Renfield":
                        await message.channel.send("Tu ne peux pas quitter la partie si tu es Renfield. Utilise %nosferatu nominate pour changer le Renfield")
                    else:
                        await message.channel.send(message.author.mention + " a quitté la partie")

                        del game.players[message.author.id]

                        if len(game.players) == 0:
                            globals.games.pop(message.channel.id)
                elif len(game.players) < 8:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Liste des joueurs
    async def com_players(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
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
            if game.turn == -1:
                await message.channel.send("La partie a été reset")
                globals.games.pop(message.channel.id)
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Début de partie + logique des parties (début des fonctions circulaires)
    async def com_start(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(game.players) >= 4 or globals.debug:
                        await game.start_game(message)
                    else:
                        await message.channel.send("Il faut au minimum 5 joueurs pour commencer la partie")
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #SUTARUTO
    async def com_SUTARUTO(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(game.players) >= 5 or globals.debug:
                        if message.author.id == 118399702667493380:
                            await game.start_game(message)
                        else:
                            await message.channel.send("Vous n'êtes pas Alix")
                    else:
                        await message.channel.send("Il faut au minimum 5 joueurs pour commencer la partie")
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_end(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if globals.debug:
                await game.end_game()

    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            globals.debug = not globals.debug
            await message.channel.send("Debug: " + str(globals.debug))


    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            for message in globals.reaction_messages:
                if message.message.id == reaction.message.id:
                    if message.check(reaction, user) and reaction.emoji in message.number_emojis:
                        await message.add_reaction(reaction, user)
                    else:
                        await message.message.clear_reaction(reaction)

    async def on_reaction_remove(self, reaction, user):
        if not user.bot:
            for message in globals.reaction_messages:
                if message.check(reaction, user) and reaction.emoji in message.number_emojis and message.message.id == reaction.message.id:
                    await message.remove_reaction(reaction, user)
