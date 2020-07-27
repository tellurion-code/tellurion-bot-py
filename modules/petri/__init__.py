import discord

from modules.petri.player import Player
from modules.petri.game import Game
from modules.reaction_message.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.petri.globals as global_values
global_values.init()


class MainClass(BaseClassPython):
    name = "Petri"
    help = {
        "description": "Module du jeu Petri",
        "commands": {
            "`{prefix}{command} create`": "Crée une partie",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} rules`": "Affiche les règles"
        }
    }
    help_active = True
    command_text = "petri"
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
            globals.debug = object["debug"]

        if self.objects.save_exists("games"):
            games = self.objects.load_object("games")
            for game in games.values():
                globals.games[game["channel"]] = Game(self)
                await globals.games[game["channel"]].reload(game, self.client)

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

                    if globals.games[message.channel.id].game_creation_message:
                        await globals.games[message.channel.id].game_creation_message.delete()

                    if globals.games[message.channel.id].info_message:
                        await globals.games[message.channel.id].info_message.delete()

                    globals.games[message.channel.id].delete_save()
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

    async def com_config(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            if message.author.id in game.players:
                args.pop(0)
                if args[0] % 2 == 0 and args[1] % 2 == 0:
                    game.ranges = args

    async def com_rules(self, message, args, kwargs):
        if len(args) > 1:
            await message.channel.send("Sous-section inconnue")
        else:
            await message.channel.send(embed=discord.Embed(
                title=":small_orange_diamond: Règles de Petri :small_orange_diamond:",
                description="""
:small_blue_diamond: **But du jeu** : :small_blue_diamond:
Chaque joueur commence avec une troupe à un endroit aléatoire de la carte de 10x10 au début de la partie.
Le gagnant est le joueur qui est le dernier avec des troupes encore vivantes, ou bien qui arrive à contrôler 50% de la carte.
Après 50 tours de table complets (manche) sans qu'un gagnant ne soit déterminé, le joueur avec le plus de troupes gagne.

:small_blue_diamond: **Déroulement d’un tour** : :small_blue_diamond:
 -  Le joueur choisit une direction
 -  Toutes ses troupes essaient de se répliquer dans cette direction:
    -  Si la case dans cette direction est vide, une nouvelle troupe de sa couleur est créée
    -  Si la case est occupée par une troupe alliée, rien ne se passe
    -  Si la case est occupée par une troupe ennemie, un combat se déclenche entre cette troupe et celle qui essaie de se répliquer

:small_blue_diamond: **Les combats** : :small_blue_diamond:
Pour déterminer qui gagne le combat, il suffit de regarder le nombre de troupes alliées se trouvant en une ligne derrière les deux troupes:
 -  Si l'attaquant en a le plus, il se réplique sur le défenseur
 -  Si le défenseur en a le plus, rien ne se passe
 -  S'il y a égalité, le défenseur est tué mais l'attaquant ne se réplique pas
                """,
                color=global_values.color))
