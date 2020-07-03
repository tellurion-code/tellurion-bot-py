import discord
import asyncio
import random

from modules.wonderland.game import Game
from modules.wonderland.player import Player
from modules.wonderland.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.wonderland.globals as global_values
global_values.init()

class MainClass(BaseClassPython):
    name = "Wonderland"
    help_active = True
    help = {
        "description": "Module du jeu Wonderland",
        "commands": {
            "`{prefix}{command} create`": "Crée une partie. Le salon où la commande est utilisée sera utilisé pour les messages d'infos.",
            "`{prefix}{command} start`": "Démarre la partie",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} roles`": "Change les rôles en jeu",
            "`{prefix}{command} rules`": "Affiche les règles"
        }
    }
    color = global_values.color
    command_text = "wl"

    def __init__(self, client):
        super().__init__(client)

        self.config["auth_everyone"] = True
        self.config["configured"] = True
        self.config["color"] = self.color
        self.command_text = self.command_text

    async def com_create(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            await message.channel.send("Il y a déjà une partie en cours dans ce channel")
        else:
            global_values.games[message.channel.id] = Game(message, self)
            await global_values.games[message.channel.id].on_creation(message)

    #Réitinitialise et supprime la partie
    async def com_reset(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            await message.channel.send("La partie a été reset")
            global_values.games.pop(message.channel.id)
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Lance la partie
    async def com_start(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            if game.round == 0:
                if message.author.id in game.players:
                    if len(game.players) >= 3 or global_values.debug:
                        await game.start_game()
                    else:
                        await message.channel.send("Il faut au minimum 3 joueurs")
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Idem
    async def com_SUTARUTO(self, message, args, kwargs):
        if message.author.id == 118399702667493380:
            await self.com_start(message, args, kwargs)

    #Active le debug: enlève la limitation de terme, et le nombre minimal de joueurs
    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            global_values.debug = not global_values.debug
            await message.channel.send("Debug: " + str(global_values.debug))

    async def com_tell(self, message, args, kwargs):
        for game in global_values.games.values():
            if message.author.id in game.in_game:
                args.pop(0)
                if len(args):
                    try:
                        id = int(args.pop(0))
                        if id in game.in_game:
                            if id != message.author.id:
                                await message.author.send("Symbole envoyé à `" + str(game.players[id].user) + "`")

                                await game.players[id].user.send(embed=discord.Embed(
                                    title="[WONDERLAND] Symbole reçu",
                                    description="`" + str(message.author) + "` vous a envoyé son symbole. Son symbole est : " + game.players[message.author.id].symbol,
                                    color=self.color
                                ))
                            else:
                                await message.author.send("Vous n'avez pas le droit de vous envoyer votre symbole à vous-même")
                        else:
                            await message.author.send("ID Invalide (Non-existant)")
                    except:
                        await message.author.send("ID Invalide (Pas un nombre valide)")

    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            for message in global_values.reaction_messages:
                if message.message.id == reaction.message.id:
                    if reaction.emoji in message.number_emojis:
                        if message.check(reaction, user):
                            await message.add_reaction(reaction, user)
                        else:
                            await message.message.remove_reaction(reaction, user)
                    else:
                        await message.message.remove_reaction(reaction, user)

    async def on_reaction_remove(self, reaction, user):
        if not user.bot:
            for message in global_values.reaction_messages:
                if user.id in message.reactions:
                    if reaction.emoji in message.number_emojis:
                        if message.number_emojis.index(reaction.emoji) in message.reactions[user.id]:
                            if message.check(reaction, user) and message.message.id == reaction.message.id:
                                await message.remove_reaction(reaction, user)
