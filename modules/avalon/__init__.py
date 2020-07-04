import discord

from modules.avalon.player import Player
from modules.avalon.reaction_message import ReactionMessage
from modules.avalon.game import Game
from modules.base import BaseClassPython

import modules.avalon.globals as global_values
global_values.init()


class MainClass(BaseClassPython):
    name = "Avalon"
    help = {
        "description": "Maître du jeu Avalon",
        "commands": {
            "`{prefix}{command} join`": "Rejoint la partie. S'il n'y en a pas dans le salon, en crée une nouvelle",
            "`{prefix}{command} quit`": "Quitte la partie",
            "`{prefix}{command} kick`": "Enlève un joueur de la partie",
            "`{prefix}{command} start`": "Démarre la partie",
            "`{prefix}{command} players`": "Affiche les joueurs de la partie",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} roles set/add/remove`": "Change les rôles, ou affiche les rôles en jeu si aucune sous-commande n'est donnée",
            "`{prefix}{command} rules`": "Affiche les règles et les explications des rôles",
            "`{prefix}{command} gamerules`": "Active/désactive les règles du jeu"
        }
    }
    help_active = True
    command_text = "avalon"
    color = global_values.color

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
        if self.objects.save_exists("globals"):
            object = self.objects.load_object("globals")
            globals.debug = object["debug"]

        if self.objects.save_exists("games"):
            games = self.objects.load_object("games")
            for game in games.values():
                globals.games[game["channel"]] = Game(self)
                await globals.games[game["channel"]].reload(game, self.client)

    async def on_ready(self):
        if self.client.get_guild(297780867286433792):
            global_values.quest_emojis["failure"] = await self.client.get_guild(297780867286433792).fetch_emoji(727263550644551782) #Get the custom emoji

    async def command(self, message, args, kwargs):
        if args[0] == "join't":
            await message.channel.send(message.author.mention + " n'a pas rejoint la partie")

    async def com_join(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
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
            embed = discord.Embed(
                title="Création de la partie d'Avalon",
                description="Tapez %avalon join pour rejoindre la partie",
                color=self.color
            )

            await message.channel.send(embed=embed)
            await message.channel.send("<@" + str(message.author.id) + "> a rejoint la partie")

            global_values.games[message.channel.id] = Game(self, message=message)

    # Quitter la partie
    async def com_quit(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    await message.channel.send(message.author.mention + " a quitté la partie")

                    del game.players[message.author.id]

                    if len(game.players) == 0:
                        global_values.games.pop(message.channel.id)
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_kick(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
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
                                global_values.games.pop(message.channel.id)
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

    # Liste des joueurs
    async def com_players(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            embed = discord.Embed(
                title="Liste des joueurs (" + str(len(game.players)) + ")",
                color=self.color,
                description="```" + ', '.join([str(self.client.get_user(x)) for x, y in game.players.items()]) + "```"
            )
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    # Réitinitialise et supprime la partie
    async def com_reset(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            async def confirm(reactions):
                if reactions[message.author.id][0] == 0:
                    await message.channel.send("La partie a été réinitialisée")
                    globals.games[message.channel.id].delete_save()
                    global_values.games.pop(message.channel.id)

            async def cond(reactions):
                if message.author.id in reactions:
                    return len(reactions[message.author.id]) == 1
                else:
                    return False

            await ReactionMessage(
                cond,
                confirm
            ).send(
                message.channel,
                "Êtes vous sûr.e de vouloir réinitialiser la partie?",
                "",
                self.color,
                ["Oui", "Non"],
                emojis=["✅", "❎"],
                validation_emoji="⭕"
            )
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    # Lance la partie
    async def com_start(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    if len(game.players) >= 5 or global_values.debug:
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

    async def com_gamerules(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            if game.turn == -1:
                if message.author.id in game.players:
                    args.pop(0)
                    if len(args):
                        invalid_rules = []
                        for rule in args:
                            if rule in game.game_rules:
                                game.game_rules[rule] = not game.game_rules[rule]
                            else:
                                invalid_rules.append(rule)

                        if len(invalid_rules):
                            await message.channel.send(', '.join(invalid_rules) + (" sont des règles invalides" if len(invalid_rules) > 1 else " est une règle invalide"))

                        if len(invalid_rules) < len(args):
                            await message.channel.send(embed=discord.Embed(
                                title="Règles modifiées:",
                                description='\n'.join([str(i) + " = **" + str(x)+ "**" for i, x in game.game_rules.items()]),
                                color=self.color))
                    else:
                        await message.channel.send(embed=discord.Embed(
                            title="Règles modifiables:",
                            description='\n'.join([str(i) + " = **" + str(x)+ "**" for i, x in game.game_rules.items()]),
                            color=self.color))
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    # Idem
    async def com_SUTARUTO(self, message, args, kwargs):
        if message.author.id == 118399702667493380:
            await self.com_start(message, args, kwargs)

    # Active le debug: enlève la limitation de terme, et le nombre minimal de joueurs
    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            global_values.debug = not global_values.debug
            await message.channel.send("Debug: " + str(global_values.debug))

            if self.objects.save_exists("globals"):
                save = self.objects.load_object("globals")
            else:
                save = {}

            save["debug"] = global_values.debug
            self.objects.save_object("globals", save)

    async def com_roles(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
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
                            valid_roles = {
                                "gentil": "good",
                                "méchant": "evil",
                                "mechant": "evil",
                                "merlin": "merlin",
                                "perceval": "percival",
                                "karadoc": "karadoc",
                                "gauvain": "gawain",
                                "galaad": "galaad",
                                "uther": "uther",
                                "arthur": "arthur",
                                "assassin": "assassin",
                                "morgane": "morgane",
                                "mordred": "mordred",
                                "oberon": "oberon",
                                "lancelot": "lancelot",
                                "elias": "elias"
                            }

                            for i, role in enumerate(roles):
                                role = roles[i] = role.lower()
                                if role not in valid_roles:
                                    invalid_roles.append(role)

                            if not len(invalid_roles):
                                if subcommand == "set":
                                    game.roles = [valid_roles[x] for x in roles]
                                elif subcommand == "add":
                                    game.roles.extend([valid_roles[x] for x in roles])
                                elif subcommand == "remove":
                                    for x in roles:
                                        for role in game.roles:
                                            if role == valid_roles[x]:
                                                game.roles.remove(role)
                                else:
                                    await message.channel.send("Sous-commande invalide")

                                await message.channel.send(embed=discord.Embed(
                                    title="Liste des rôles (" + str(len(game.roles)) + ") :",
                                    description=', '.join([global_values.visual_roles[x] for x in game.roles]),
                                    color=self.color))
                            else:
                                if len(invalid_roles) - 1:
                                    await message.channel.send(', '.join(invalid_roles) + " sont des rôles invalides.")
                                else:
                                    await message.channel.send(', '.join(invalid_roles) + " est un rôle invalide.")
                    else:
                        await message.channel.send("Vous n'êtes pas dans la partie")
                else:
                    await message.author.send("La partie a déjà commencé")
            elif len(game.roles):
                await message.channel.send(embed=discord.Embed(
                    title="Liste des rôles (" + str(len(game.roles)) + ") :",
                    description=', '.join([global_values.visual_roles[x] for x in game.roles]),
                    color=self.color))
            else:
                await message.channel.send(embed=discord.Embed(
                    title="Liste des rôles :",
                    description="Aucun rôle n'a été défini, la composition par défaut va être utilisé (Merlin, Perceval, Morgane, Assassin).",
                    color=self.color))
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_rules(self, message, args, kwargs):
        if len(args) > 1:
            if args[1] == "roles":
                await message.channel.send(embed=discord.Embed(
                    title=":small_blue_diamond: Les rôles spéciaux : :small_blue_diamond:",
                    description="""
🟦 Les gentils: 🟦
__Merlin__ 🧙‍♂️ : Il connaît tous les noms des méchants et celui de Karadoc (Hormis Mordred).
__Perceval__ 🤴 : Il connaît le pseudo de Merlin et de Morgane mais pas qui est qui.
__Karadoc__ 🥴 : Il apparaît comme un méchant à Merlin.
__Gauvain__ 🛡️ : Peut inverser le résultat de la quête s'il est dedans.
__Galaad__ 🙋 : Les gentils le connaissent.
__Uther__ 👨‍🦳 : En début de partie, il choisit un joueur dont il apprend le rôle.
__Arthur__ 👑 : Une fois dans la partie, il peut faire annuler une quête s'il est dedans. Les choix ne sont alors pas révélés et l'équipe est considérée comme refusée.

🟥 Les méchants: 🟥
__Assassin__ 🗡️ : Si les gentils ont réussi 3 quêtes, il peut tenter d’assassiner Merlin. S’il y parvient les méchants gagnent la partie.
__Mordred__ 😈 : Il n’est pas connu de Merlin.
__Morgane__ 🧙‍♀️ : Elle apparait aux yeux de Perceval.
__Oberon__ 😶 : Il ne connait pas ses alliés et ses alliés ne savent pas qui il est.
__Lancelot__ ⚔️ : Peut inverser le résultat de la quête s'il est dedans. Ne peut pas mettre d'Echec. Il ne connait pas les méchants mais eux le connaissent en tant que Lancelot.

🟩 Les solos: 🟩
__Elias__ 🧙 : S'il est assassiné, il gagne seul. Si les méchants font rater 3 quêtes, il perd avec les gentils. Il connaît Merlin.
                    """,
                    color=global_values.color))
            else:
                await message.channel.send("Sous-section inconnue")
        else:
            await message.channel.send(embed=discord.Embed(
                title=":small_orange_diamond: Règles du Avalon :small_orange_diamond:",
                description="""
:small_blue_diamond: But du jeu : :small_blue_diamond:
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

*Note : Tous les votes se font par le biais des réactions ( :white_check_mark: et :negative_squared_cross_mark: )
                """,
                color=global_values.color))

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
