import discord

from modules.mascarade.game import Game
from modules.mascarade.roles import Role
from modules.mascarade.utils import display_money
from modules.reaction_message.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.mascarade.globals as global_values
global_values.init()

class MainClass(BaseClassPython):
    name = "Mascarade"
    help = {
        "description": "Maître du jeu Mascarade",
        "commands": {
            "`{prefix}{command} create`": "Rejoint la partie. S'il n'y en a pas dans le salon, en crée une nouvelle",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} rules`": "Affiche les règles et les explications des rôles",
            "`{prefix}{command} gamerules`": "Active/désactive les règles du jeu"
        }
    }
    help_active = True
    command_text = "mascarade"
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
        self.config["configured"] = True
        self.config["color"] = self.color
        self.config["help_active"] = True
        self.config["auth_everyone"] = True

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
        if len(args):
            if args[0] == "join't":
                await message.channel.send(message.author.mention + " n'a pas rejoint la partie")
        else:
            self.com_create(message, args, kwargs)

    async def com_create(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            await message.channel.send("Il y a déjà une partie en cours")
        else:
            global_values.games[message.channel.id] = Game(self, message=message)
            await global_values.games[message.channel.id].on_creation(message)

    async def com_roles(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            await game.channel.send(
                embed=discord.Embed(
                    title="[MASCARADE]Rôles en jeu",
                    description='\n'.join(str(x) for x in game.roles),
                    color=global_values.color
                )
            )
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_show(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            await game.info_view.message.delete()
            await game.send_info(mode="set")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")
            
    # Réitinitialise et supprime la partie
    async def com_reset(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            async def confirm(reactions):
                if reactions[message.author.id][0] == 0:
                    await message.channel.send("La partie a été réinitialisée")

                    if global_values.games[message.channel.id].info_view:
                        await global_values.games[message.channel.id].info_view.delete()

                    global_values.games[message.channel.id].delete_save()
                    del global_values.games[message.channel.id]

            async def cond(reactions):
                if message.author.id in reactions:
                    return len(reactions[message.author.id]) == 1
                else:
                    return False

            await ReactionMessage(
                cond,
                confirm,
                check=lambda r, u: u.id == message.author.id
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

    async def com_rules(self, message, args, kwargs):
        if len(args) > 1:
            if args[1] == "roles":
                await message.channel.send(embed=discord.Embed(
                    title="🔸 Rôles de Mascarade 🔸",
                    description='\n'.join([e.icon + " **" + e.name + "**: " + e.description for e in Role.__subclasses__()]),
                    color=global_values.color
                ))
            else:
                await message.channel.send("Sous-section inconnue")
        else:
            await message.channel.send(embed=discord.Embed(
                title="🔸 Règles de Mascarade 🔸",
                description=f"""
🔹 **But du jeu** : 🔹
Obtenir 13 pièces {display_money(1)}, ou avoir le plus de {display_money(1)} lorsqu'un joueur est éliminé. 
Au début de la partie, vous recevrez un rôle parmi ceux disponibles et 6 {display_money(1)} ({display_money(6)}).

🔹 **Déroulement d’un tour** : 🔹
Chaque tour, vous pouvez réaliser une des trois actions suivantes:
- Regarder votre rôle
- Echanger (ou faire semblant d'échanger) de rôle avec quelqu'un d'autre
- Utiliser le pouvoir de votre rôle (ou bluffer avoir un autre rôle)

🔹 **Les pouvoirs** : 🔹
Lorsqu'un joueur annonce avoir un rôle, les autres joueurs peuvent contester. Si au moins un le fait, le joueur ayant fait l'annonce et tous les contestants révèlent leur rôle.
Tous ceux qui n'ont pas le rôle annoncé paye {display_money(1)} au tribunal. Si un joueur a effectivement le rôle annoncé, il peut effectuer son pouvoir, même si ce n'est pas son tour.
Si un joueur n'a plus de {display_money(1)}, il est éliminé.

🔹 **Précisions** : 🔹
Lorsque que le jeu commence, tous les joueurs révèlent leur rôle avant de commencer à jouer.
Les 4 premiers joueurs sont obligés de faire l'action d'échanger (ou pas) durant leur tour.
Si la carte d'un joueur a été révélée durant son tour ou le tour précédent, il doit aussi échanger durant son tour.
                """,
                color=global_values.color
            ))

    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            if reaction.message.channel.id in global_values.games:
                game = global_values.games[reaction.message.channel.id]
                if game.info_view.message.id == reaction.message.id:
                    await reaction.message.remove_reaction(reaction.emoji, user)
                    if game.turn != -1:
                        if user.id in game.players:
                            game.players[user.id].index_emoji = str(reaction.emoji)

                            if self.objects.save_exists("icons"):
                                save = self.objects.load_object("icons")
                            else:
                                save = {}

                            save[str(user.id)] = str(reaction.emoji)
                            self.objects.save_object("icons", save)

                            await game.send_info()
