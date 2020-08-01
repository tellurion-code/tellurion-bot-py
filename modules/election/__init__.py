import discord

import modules.election.globals as global_values
global_values.init()

from modules.election.player import Player, Le_Pen
from modules.election.game import Game
from modules.reaction_message.reaction_message import ReactionMessage
from modules.base import BaseClassPython

classes = {"player": Player}
classes.update({c.__name__.lower(): c for c in Player.__subclasses__()})

class MainClass(BaseClassPython):
    name = "Election"
    help = {
        "description": "Module du jeu Election de Kaznad",
        "commands": {
            "`{prefix}{command} create`": "Crée une partie s'il n'y en a pas déjà une dans le salon",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} roles set/add/remove`": "Change les rôles, ou affiche les rôles en jeu si aucune sous-commande n'est donnée",
            "`{prefix}{command} rules`": "Affiche les règles et les explications des rôles"
        }
    }
    help_active = True
    command_text = "election"
    color = global_values.color

    def __init__(self, client):
        super().__init__(client)
        self.config["name"] = self.name
        self.config["coommand_text"] = self.command_text
        self.config["color"] = self.color
        self.config["help_active"] = self.help_active
        self.config["configured"] = True
        self.config["auth_everyone"] = True

    async def on_ready(self):
        if self.objects.save_exists("globals"):
            object = self.objects.load_object("globals")
            global_values.debug = object["debug"]

        if self.objects.save_exists("games"):
            games = self.objects.load_object("games")
            for game in games.values():
                global_values.games[game["channel"]] = Game(self)
                await global_values.games[game["channel"]].reload(game, self.client)

        if self.client.get_guild(297780867286433792):
            global_values.le_pen_emoji = await self.client.get_guild(297780867286433792).fetch_emoji(308640897090977792) #Get the custom emoji
            Le_Pen.name = str(global_values.le_pen_emoji) + " Le Pen"

    async def command(self, message, args, kwargs):
        if args[0] == "join't":
            await message.channel.send(message.author.mention + " n'a pas rejoint la partie")

    async def com_create(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            await message.channel.send("Il y a déjà une partie en cours dans ce channel")
        else:
            global_values.games[message.channel.id] = Game(self,message=message)
            await global_values.games[message.channel.id].on_creation(message)

    # Réitinitialise et supprime la partie
    async def com_reset(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            async def confirm(reactions):
                if reactions[message.author.id][0] == 0:
                    await message.channel.send("La partie a été réinitialisée")

                    if global_values.games[message.channel.id].game_creation_message:
                        await global_values.games[message.channel.id].game_creation_message.delete()

                    global_values.games[message.channel.id].delete_save()
                    del global_values.games[message.channel.id]

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
                                "joueur": "player",
                                "scientifique": "scientist",
                                "raoult": "raoult",
                                "martyr": "martyr",
                                "lobbyiste": "lobbyist",
                                "corrupteur": "corruptor",
                                "journaliste": "journalist",
                                "le_pen": "le_pen"
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
                                    description=', '.join([classes[x].name for x in game.roles]),
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
                    description=', '.join([classes[x].name for x in game.roles]),
                    color=self.color))
            else:
                await message.channel.send(embed=discord.Embed(
                    title="Liste des rôles :",
                    description="Aucun rôle n'a été défini, la composition par défaut va être utilisé (Merlin, Perceval, Morgane, Assassin).",
                    color=self.color
                ))
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
                            if rule in game.gamerules:
                                game.gamerules[rule] = not game.gamerules[rule]
                            else:
                                invalid_rules.append(rule)

                        if len(invalid_rules):
                            await message.channel.send(', '.join(invalid_rules) + (" sont des règles invalides" if len(invalid_rules) > 1 else " est une règle invalide"))

                        if len(invalid_rules) < len(args):
                            await message.channel.send(embed=discord.Embed(
                                title="Règles modifiées:",
                                description='\n'.join([str(i) + " = **" + str(x)+ "**" for i, x in game.gamerules.items()]),
                                color=self.color))
                    else:
                        await message.channel.send(embed=discord.Embed(
                            title="Règles modifiables:",
                            description='\n'.join([str(i) + " = **" + str(x)+ "**" for i, x in game.gamerules.items()]),
                            color=self.color))
                else:
                    await message.channel.send("Vous n'êtes pas dans la partie")
            else:
                await message.author.send("La partie a déjà commencé")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_rules(self, message, args, kwargs):
        if len(args) > 1:
            if args[1] == "roles":
                await message.channel.send(embed=discord.Embed(
                    title=":small_blue_diamond: Les rôles spéciaux : :small_blue_diamond:",
                    description='\n\n'.join(["**" + c.name + "**\n" + '. '.join(c.description.split(". ")[1:]) for c in Player.__subclasses__()]) + "\n\n" + """
__Les rôles temporaires:__

🎩 **Le ministre** :
Un joueur obtient ce rôle au tour k si il est l'unique personne ayant récolté le plus de votes.
Ce rôle confère un point supplémentaire au tour k + 1, et n'est pas accessible à l'avant dernier tour.

👑 **Le chef d'état** :
Si un joueur possède plus de 50% des voix au tour k, il obtient ce rôle
Il donne à ce joueur la capacité d'affecter un malus d'un point à un autre joueur au tour k + 1, et n'est pas accessible à l'avant dernier tour.
                    """,
                    color=global_values.color
                ))
            else:
                await message.channel.send("Sous-section inconnue")
        else:
            await message.channel.send(embed=discord.Embed(
                title=":small_orange_diamond: Règles d'Election (jeu de Kaznad) :small_orange_diamond:",
                description="""
:small_blue_diamond: **But du jeu** : :small_blue_diamond:
Être le dernier joueur à ne pas être éliminé

:small_blue_diamond: **Déroulement d’un tour** : :small_blue_diamond:
- Chaque joueur vote pour un autre joueur
- Celui avec le moins de vote pour lui est éliminé
- S'il y a une égalité, un vote est lancé pour départager. Si l'égalité persiste, elle est résolue au hasard

:small_blue_diamond: **Utilisez "election rules roles" pour avoir la liste des rôles spéciaux** :small_blue_diamond:

:small_blue_diamond: **Précisions** :small_blue_diamond:
- Même si un joueur est éliminé, il vote encore et ce, jusqu'à la fin de la partie
- Sauf exceptions, le rôle d'un joueur n'est plus effectif s'il est éliminé
- Les rôles et les votes sont cachés
- Les rôles sont inactifs lors de votes dûs à des égalités.
- Les rôles de ministre et chef d'état sont cumulables
- Le malus affecté par le chef d'état est visible par tous les joueurs.
""",
                color=global_values.color))
