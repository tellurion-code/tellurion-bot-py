import discord
import asyncio
import random

from modules.secrethitler.game import Game
from modules.secrethitler.player import Liberal, Fascist, Hitler
from modules.secrethitler.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.secrethitler.globals as globals
globals.init()

class MainClass(BaseClassPython):
    name = "SH"
    help_active = True
    help = {
        "description": "Module du jeu Secret Hitler",
        "commands": {
            "`{prefix}{command} join`": "Rejoint la partie de Secret Hitler. S'il n'y en a pas dans le salon, en crée une nouvelle.",
            "`{prefix}{command} quit`": "Quitte la partie de Secret Hitler",
            "`{prefix}{command} start`": "Démarre la partie de Secret Hitler",
            "`{prefix}{command} players`": "Affiche les joueurs de la partie de Secret Hitler",
            "`{prefix}{command} reset`": "Reinitialise la partie de Secret Hitler"
        }
    }
    color = globals.color
    command_text = "sh"

    def __init__(self, client):
        super().__init__(client)

    async def command(self, message, args, kwargs):
        if args[0] == "join't":
            await message.channel.send(message.author.mention + " n'a pas rejoint la partie")

    async def com_join(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    await message.channel.send("Vous êtes déjà dans la partie")
                else:
                    if len(game.players) < 10:
                        await message.channel.send("<@" + str(message.author.id) + "> a rejoint la partie")

                        game.players[message.author.id] = Liberal(message.author)
                    else:
                        await message.channel.send("Il y a déjà le nombre maximum de joueurs (10)")
        else:
            embed = discord.Embed(title = "Démarrage de la partie de Secret Hitler",
                description = "Tapez %sh join pour rejoindre la partie",
                color = self.color)

            await message.channel.send(embed = embed)

            globals.games[message.channel.id] = Game(message)

    #Quitter la partie
    async def com_quit(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
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

    async def com_start(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(game.players) >= 5 or globals.debug:
                        await game.start_game()
                    else:
                        await message.channel.send("Il faut au minimum 5 joueurs")
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            globals.debug = not globals.debug
            await message.channel.send("Debug: " + str(globals.debug))

    async def com_powers(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(args):
                        powers = args.split(", ")
                        if len(powers) >= 5:
                            powers = powers[:5]
                            done = True
                            valid_powers = ["none", "kill", "elect", "inspect", "peek"]
                            for power in powers:
                                if power not in valid_powers:
                                    done = False
                                    break

                            if done:
                                await message.channel.send("Pouvoirs changés pour : " + ', '.join(powers))
                                powers.append("none")
                                game.policies = powers
                            else:
                                await message.channel.send('Il faut préciser 5 pouvoirs séparés par ", " parmi none, peek, inspect, kill ou elect (Un des pouvoirs était invalide)')
                        else:
                            await message.channel.send('Il faut préciser 5 pouvoirs séparés par ", " parmi none, peek, inspect, kill ou elect (5 pouvoirs requis)')
                    else:
                        await message.channel.send('Il faut préciser 5 pouvoirs séparés par ", " parmi none, peek, inspect, kill ou elect (5 pouvoirs requis)')
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

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
