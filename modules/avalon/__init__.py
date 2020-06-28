import datetime
import discord

import modules.avalon.globals as globals
globals.init()

from modules.avalon.player import Player
from modules.avalon.game import Game
from modules.base import BaseClassPython

class MainClass(BaseClassPython):
    name = "Avalon"
    help = {
        "description": "Maître du jeu Avalon.",
        "commands": {
            "`{prefix}{command} join`": "Rejoint la partie. S'il n'y en a pas dans le salon, en crée une nouvelle",
            "`{prefix}{command} quit`": "Quitte la partie",
            "`{prefix}{command} start`": "Démarre la partie",
            "`{prefix}{command} players`": "Affiche les joueurs de la partie",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} roles`": "Change les rôles"
        }
    }
    help_active = True
    command_text = "avalon"
    color = globals.color

    def __init__(self, client):
        super().__init__(client)
        # self.config.init({"spectate_channel": 0,
        #                   "illustrations":{"merlin":"",
        #                                    "perceval":"",
        #                                    "gentil":"",
        #                                    "assassin":"",
        #                                    "mordred":"",
        #                                    "morgane":"",
        #                                    "oberon":"",
        #                                    "mechant":""},
        #                   "couleurs":{"merlin":"",
        #                               "perceval":0,
        #                               "gentil":0,
        #                               "assassin":0,
        #                               "mordred":0,
        #                               "morgane":0,
        #                               "oberon":0,
        #                               "mechant":0,
        #                               "test":15},
        #                   "test":{"merlin":"",
        #                                    "perceval":0,
        #                                    "gentil":0,
        #                                    "assassin":0,
        #                                    "mordred":0,
        #                                    "morgane":0,
        #                                    "oberon":0,
        #                                    "mechant":0,
        #                                    "test":15}
        #                   })

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
                    if len(game.players) < 14:
                        await message.channel.send("<@" + str(message.author.id) + "> a rejoint la partie")

                        game.players[message.author.id] = Player(message.author)
                    else:
                        await message.channel.send("Il y a déjà le nombre maximum de joueurs (10)")
        else:
            embed = discord.Embed(title = "Création de la partie d'Avalon",
                description = "Tapez %avalon join pour rejoindre la partie",
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
            embed = discord.Embed(
                title = "Liste des joueurs (" + str(len(globals.games[message.channel.id].players)) + ")",
                color = self.color,
                description = "```" + ', '.join([str(self.client.get_user(x)) for x, y in globals.games[message.channel.id].players.items()]) + "```"
            )
            await message.channel.send(embed = embed)
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Réitinitialise et supprime la partie
    async def com_reset(self, message, args, kwargs):
        if message.channel.id in globals.games:
            await message.channel.send("La partie a été reset")
            globals.games[message.channel.id].delete_save()
            globals.games.pop(message.channel.id)
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

    async def com_roles(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if len(args) > 1:
                if game.turn == -1:
                    if message.author.id in game.players:
                        roles = args
                        roles.pop(0)
                        if len(roles) >= len(game.players):
                            done = True
                            valid_roles = {"gentil": "good", "méchant": "evil", "merlin": "merlin", "perceval": "percival", "lancelot": "lancelot", "assassin": "assassin", "morgane": "morgane", "mordred": "mordred", "oberon": "oberon", "agrav1": "agrav1", "agrav2": "agrav2"}

                            for role in roles:
                                if role not in valid_roles:
                                    done = False
                                    break

                            if done:
                                await message.channel.send("Rôles changés pour : " + ', '.join(roles))
                                game.roles = [valid_roles[x] for x in roles]
                            else:
                                await message.channel.send('Il faut préciser autant de roles que de joueurs en arguments (Un des roles était invalide)')
                        else:
                            await message.channel.send('Il faut préciser autant de roles que de joueurs en arguments (Pas assez de rôles)')
                    else:
                        await message.channel.send("Vous n'êtes pas dans la partie")
                else:
                    await message.author.send("La partie a déjà commencé")
            else:
                if len(game.roles):
                    await message.channel.send('Rôles actuels: ```' + ', '.join([x for x in game.roles]) + '```')
                else:
                    await message.channel.send('Rôles actuels: ```Dépendant du nombre de joueurs```')
        else:
            await message.channel.send("Il n'y a pas de partie en cours")
