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
            "`{prefix}{command} kick`": "Enlève un joueur de la partie",
            "`{prefix}{command} start`": "Démarre la partie",
            "`{prefix}{command} players`": "Affiche les joueurs de la partie",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} roles`": "Change les rôles",
            "`{prefix}{command} rules`": "Affiche les règles et les explications des rôles"
        }
    }
    help_active = True
    command_text = "avalon"
    color = globals.color

    def __init__(self, client):
        super().__init__(client)
        # self.config.init({"help_active": True,
        #     "color": globals.color,
        #     "auth_everyone": True,
        #     "authorized_roles": [],
        #     "authorized_users": [],
        #     "command_text": "avalon",
        #     "configured": True
        # })

    async def on_ready(self):
        if self.client.get_guild(297780867286433792):
            globals.quest_emojis["failure"] = await self.client.get_guild(297780867286433792).fetch_emoji(727263550644551782) #Get the custom emoji

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

    async def com_kick(self, message, args, kwargs):
        if message.channel.id in globals.games:
            game = globals.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(args) > 1:
                        kicked = 0

                        if int(args[1][3:-1]) in game.players:
                            kicked = int(args[1][3:-1])
                        elif int(args[1]) in game.players:
                            kicked = int(args[1])

                        if kicked:
                            await message.channel.send(game.players[kicked].user.mention + " a été kick de la partie")
                            del game.players[kicked]

                            if len(game.players) == 0:
                                globals.games.pop(message.channel.id)
                        else:
                            await message.channel.send("La mention ou l'identifiant sont erronés ou ne sont pas dans la partie")
                    else:
                        await message.channel.send("Veuillez préciser un identifiant ou une mention")
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
            await message.channel.send("La partie a été réinitialisée")
            #globals.games[message.channel.id].delete_save()
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
                            await message.channel.send("Le nombre de rôles ne correspond pas au nombre de joueurs")
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
                        args.pop(0)
                        subcommand = args.pop(0)

                        if subcommand == "reset":
                            game.roles = []
                            await message.channel.send("Les rôles ont été réinitialisés")
                        else:
                            roles = args
                            invalid_roles = []
                            valid_roles = {"gentil": "good",
                                "méchant": "evil",
                                "mechant": "evil",
                                "merlin": "merlin",
                                "perceval": "percival",
                                "lancelot": "lancelot",
                                "karadoc": "karadoc",
                                "galaad": "galaad",
                                "uther": "uther",
                                "assassin": "assassin",
                                "morgane": "morgane",
                                "mordred": "mordred",
                                "oberon": "oberon",
                                "agrav1": "agrav1",
                                "agrav2": "agrav2",
                                "elias": "elias"}

                            for role in roles:
                                if role not in valid_roles:
                                    invalid_roles.push(role)

                            if not len(invalid_roles):
                                if subcommand == "set":
                                    game.roles = [valid_roles[x] for x in roles]
                                    await message.channel.send(embed = discord.Embed(title = "Rôles",
                                        description = "Rôles changés pour (" + str(len(game.roles)) + "): " + ', '.join([globals.visual_roles[x] for x in game.roles])))
                                elif subcommand == "add":
                                    game.roles.extend([valid_roles[x] for x in roles])
                                    await message.channel.send(embed = discord.Embed(title = "Rôles",
                                        description = "Rôles changés pour (" + str(len(game.roles)) + "): " + ', '.join([globals.visual_roles[x] for x in game.roles])))
                                elif subcommand == "remove":
                                    for x in roles:
                                        for role in game.roles:
                                            if role == valid_roles[x]:
                                                game.roles.remove(role)

                                    await message.channel.send(embed = discord.Embed(title = "Rôles",
                                        description = "Rôles changés pour (" + str(len(game.roles)) + "): " + ', '.join([globals.visual_roles[x] for x in game.roles])))
                                else:
                                    await message.channel.send("Sous-commande invalide")
                            else:
                                await message.channel.send(', '.join(invalid_roles) + " est/sont un/des rôle(s) invalide(s))")
                    else:
                        await message.channel.send("Vous n'êtes pas dans la partie")
                else:
                    await message.author.send("La partie a déjà commencé")
            else:
                if len(game.roles):
                    await message.channel.send(embed = discord.Embed(title = "Rôles",
                        description = "Rôles actuels (" + str(len(game.roles)) + "): " + ', '.join([globals.visual_roles[x] for x in game.roles])))
                else:
                    await message.channel.send('Rôles actuels: [Dépendant du nombre de joueurs]')
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_rules(self, message, args, kwargs):
        if len(args) > 1:
            if args[1] == "roles":
                await message.channel.send(embed = discord.Embed(title = ":small_blue_diamond: Les rôles spéciaux : :small_blue_diamond:",
                    description = """🟦 Les gentils: 🟦
                    __Merlin__ 🧙‍♂️ : Il connaît tous les noms des méchants et celui de Karadoc (Hormis Mordred).
                    __Perceval__ 🤴 : Il connaît le pseudo de Merlin et de Morgane mais pas qui est qui.
                    __Karadoc__ 🥴 : Il apparaît comme un méchant à Merlin.
                    __Gauvain__ 🛡️ : Peut inverser le résultat de la quête s'il est dedans.
                    __Galaad__ 🙋 : Les gentils le connaissent.
                    __Uther__ 👨‍🦳 : En début de partie, il choisit un joueur dont il apprend le rôle.

                    🟥 Les méchants: 🟥
                    __Assassin__ 🗡️ : Si les gentils ont réussi 3 quêtes, il peut tenter d’assassiner Merlin. S’il y parvient les méchants gagnent la partie.
                    __Mordred__ 😈 : Il n’est pas connu de Merlin.
                    __Morgane__ 🧙‍♀️ : Elle apparait aux yeux de Perceval.
                    __Oberon__ 😶 : Il ne connait pas ses alliés et ses alliés ne savent pas qui il est.
                    __Lancelot__ ⚔️ : Peut inverser le résultat de la quête s'il est dedans. Ne peut pas mettre d'Echec.

                    🟩 Les solos: 🟩
                    __Elias__ 🧙 : S'il est assassiné, il gagne seul. Si les méchants font rater 3 quêtes, il perd avec les gentils. Il connaît Merlin.""",
                    color = globals.color))
            else:
                await message.channel.send("Sous-section inconnue")
        else:
            await message.channel.send(embed = discord.Embed(title = ":small_orange_diamond: Règles du Avalon :small_orange_diamond:",
                description = """:small_blue_diamond: But du jeu : :small_blue_diamond:
                    Il a 2 équipes, les gentils et les méchants, leur but est :
                     - Pour les gentils faire réussir 3 quêtes
                     - Pour les méchants faire échouer 3 quêtes OU faire annuler 5 propositions d’équipe à la suite.

                    :small_blue_diamond: Déroulement d’un tour : :small_blue_diamond:
                     -  Au début du tour le chef d’équipe choisit qui partira en quête
                     -  Les joueurs votent* pour ou contre la composition de l’équipe
                          -  Si l’équipe est validée, ses membres valident en secret pour ou contre la réussite de la quête. Attention, il suffit d’un seul vote échec pour faire échouer la quête
                          -  Si l’équipe n’est pas validée, c’est au chef d’équipe suivant de choisir la composition de l’équipe
                    Attention S’il y a 7 participants ou plus, la quête n°4 doit avoir 2 échecs pour échouer

                    :small_blue_diamond: Les clans : :small_blue_diamond:
                    🟦 Gentils  : Simplement gentil
                    🟥 Méchant  : Les méchants se connaissent entre eux
                    🟩 Solo     : Ils gagnent autrement qu'avec la réussite ou l'échec des quêtes
                    (Conseil : Ne vous faites jamais passer pour un méchant)

                    :small_blue_diamond: **Utilisez "avalon rules roles" poura voir la liste des rôles spéciaux** :small_blue_diamond:

                    *Note : Tous les votes se font par le biais des réactions ( :white_check_mark: et :negative_squared_cross_mark: )""",
                color = globals.color))
