import discord
import asyncio
import random

from modules.secrethitler.game import Game
from modules.secrethitler.player import Player
from modules.reaction_message.reaction_message import ReactionMessage
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
            "`{prefix}{command} reset`": "Reinitialise la partie de Secret Hitler",
            "`{prefix}{command} powers`": "Change les pouvoirs présidentiels, ou les affiche si aucun argument n'est précisé",
            "`{prefix}{command} roles`": "Change les rôles, ou les affiche si aucun argument n'est précisé"
        }
    }
    color = globals.color
    command_text = "sh"

    def __init__(self, client):
        super().__init__(client)
        self.config["configured"] = True
        self.config["color"] = self.color
        self.config["help_active"] = True
        self.config["auth_everyone"] = True
        self.config["command_text"] = self.command_text

    async def on_ready(self):
        if self.objects.save_exists("globals"):
            object = self.objects.load_object("globals")
            globals.debug = object["debug"]

        if self.objects.save_exists("games"):
            games = self.objects.load_object("games")
            for game in games.values():
                globals.games[game["channel"]] = Game(self)
                await globals.games[game["channel"]].reload(game, self.client)

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

                        game.players[message.author.id] = Player(message.author)
                    else:
                        await message.channel.send("Il y a déjà le nombre maximum de joueurs (10)")
        else:
            embed = discord.Embed(title = "Création de la partie de Secret Hitler",
                description = "Tapez %sh join pour rejoindre la partie",
                color = self.color)

            await message.channel.send(embed = embed)

            globals.games[message.channel.id] = Game(self, message = message)

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

    #Réitinitialise et supprime la partie
    async def com_reset(self, message, args, kwargs):
        if message.channel.id in globals.games:
            await message.channel.send("La partie a été reset")
            globals.games[message.channel.id].delete_save()
            del globals.games[message.channel.id]
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Lance la partie
    async def com_start(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(game.players) >= 5 or globals.debug:
                        if len(game.roles) in [0, len(game.players)]:
                            await game.start_game()
                        else:
                            await message.channel.send("Le nombre de rôles ne correspond pasau nombre de joueurs")
                    else:
                        await message.channel.send("Il faut au minimum 5 joueurs")
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
            globals.debug = not globals.debug
            await message.channel.send("Debug: " + str(globals.debug))

            if self.objects.save_exists("globals"):
                object = self.objects.load_object("globals")
            else:
                object = {}

            object["debug"] = globals.debug
            self.objects.save_object("globals", object)

    #Change les pouvoirs présidentiels
    async def com_powers(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(args) > 1:
                        powers = args
                        powers.pop(0)
                        print(len(powers))
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
                                await message.channel.send('Il faut préciser 5 pouvoirs séparés en arguments parmi none, peek, inspect, kill ou elect (Un des pouvoirs était invalide)')
                        else:
                            await message.channel.send('Il faut préciser 5 pouvoirs séparés en arguments parmi none, peek, inspect, kill ou elect (5 pouvoirs requis)')
                    else:
                        if len(game.policies):
                            await message.channel.send('Pouvoirs actuels: ```' + ', '.join([x for x in game.policies]) + '```')
                        else:
                            await message.channel.send('Pouvoirs actuels: ```Dépendant du nombre de joueurs```')
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_roles(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(args) > 1:
                        roles = args
                        roles.pop(0)
                        print(len(roles))
                        if len(roles) >= len(game.players):
                            roles = roles[:len(game.players)]
                            done = True
                            valid_roles = ["liberal", "fascist", "hitler", "goebbels", "merliner"]

                            for role in roles:
                                if role not in valid_roles:
                                    done = False
                                    break

                            if done:
                                await message.channel.send("Rôles changés pour : " + ', '.join(roles))
                                game.roles = roles
                            else:
                                await message.channel.send('Il faut préciser autant de roles que de joueurs séparés en arguments parmi liberal, fascist, hitler, goebbels ou merliner (Un des roles était invalide)')
                        else:
                            await message.channel.send('Il faut préciser autant de roles que de joueurs séparés en arguments parmi liberal, fascist, hitler, goebbels ou merliner (Pas assez de roles)')
                    else:
                        if len(game.roles):
                            await message.channel.send('Roles actuels: ```' + ', '.join([x for x in game.roles]) + '```')
                        else:
                            await message.channel.send('Roles actuels: ```Dépendant du nombre de joueurs```')
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")
