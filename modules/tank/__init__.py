import discord

from modules.tank.player import Player
from modules.tank.game import Game
from modules.reaction_message.reaction_message import ReactionMessage
from modules.base import BaseClassPython

import modules.tank.globals as global_values
global_values.init()


class MainClass(BaseClassPython):
    name = "Tank"
    help = {
        "description": "Module du jeu Tank",
        "commands": {
            "`{prefix}{command} create`": "Crée une partie",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} rules`": "Affiche les règles"
        }
    }
    help_active = True
    command_text = "tank"
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

    async def com_show(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            if game.round > -1:
                game.resend_info_message = True
                await message.channel.send("Le message de jeu sera de nouveau renvoyé une fois cette manche terminée")
            else:
                await message.channel.send("La partie n'a pas commencé")
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
                if len(args) == 4:
                    args.pop(0)
                    try:
                        args = [int(x) for x in args]
                    except:
                        await message.channel.send("Un des arguments n'est pas un nombre valide")
                        return

                    if args[0] % 2 == 0 and args[1] % 2 == 0:
                        game.ranges = args
                        await message.channel.send("La carte a été changée pour être " + str(game.ranges[0]) + "x" + str(game.ranges[1]) + " avec " + str(game.ranges[2]) + (" murs" if game.ranges[2] > 1 else " mur") + " par quartier")
                    else:
                        await message.channel.send("La carte doit avoir des dimensions paires")
                else:
                    await message.channel.send("Il faut préciser la hauteur, la largeur, et le nombre de murs par quartier")
            else:
                await message.channel.send("Vous n'êtes pas dans la partie")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_rules(self, message, args, kwargs):
        if len(args) > 1:
            if args[1] == "powers":
                await message.channel.send(embed=discord.Embed(
                    title=":small_orange_diamond: Pouvoirs :small_orange_diamond:",
                    description="Les pouvoirs actifs sont déclenchés avec l'option 🦸 et ne prennent pas le tour\n\n" + '\n\n'.join(["**" + c.name + "**\n" + c.description for c in Player.__subclasses__()]),
                    color=global_values.color))
            else:
                await message.channel.send("Sous-section inconnue")
        else:
            await message.channel.send(embed=discord.Embed(
                title=":small_orange_diamond: Règles de Tank :small_orange_diamond:",
                description="""
:small_blue_diamond: **But du jeu** : :small_blue_diamond:
Chaque joueur joue un tank placé dans un des coins du plateau au début de la partie.
Le gagnant est le dernier joueur en vie.

:small_blue_diamond: **Déroulement d’une manche** : :small_blue_diamond:
 -  Tous les joueurs choissisent leurs actions dans l'ordre parmis les options suivantes:
 --- 🔄 Tourner à gauche
 --- 🔁 Tourner à droite
 --- 🔼 Avancer
 --- 🔽 Reculer
 --- ⏪ Dash à gauche
 --- ⏩ Dash à droite
 --- 💥 Tirer
 --- ❌ Ne rien faire
 -  Une fois les actions validées (✅), elles ne sont alorsplus modifiables. Retirer les réactions n'a aucun effet et en rajouter devient impossible.
 -  Un joueur peut choisir d'utiliser toutes, aucune, ou juste certaines des actions disponibles en un seul tour.
 -  Si jamais un joueur en choisit moins que les autres, il terminera alors son programme plus tôt.
 -  Toutes les actions choisies sont résolues dans l'ordre choisi par les joueurs.
 -  __Les mouvements sont relatifs à la direction du tank.__

:small_blue_diamond: **La navigation** : :small_blue_diamond:
 -  Les murs empêchent les joueurs d'avancer et bloquent les tirs.
 -  Les murs empêchent aussi de tourner si le canon du tank doit se retrouver à sa place. Un tank peut tourner même s'il a un mur sur le chemin (dans le coin).

:small_blue_diamond: **Les tirs** : :small_blue_diamond:
 -  Chaque tir consomme une munition (▫️). Les muntions rechargent à la fin du tour si tu ne tires pas à un maximum de 3.
 -  Les tirs se font en ligne droite dans la direction actuelle du tank. Le tir est instantanné sur toute la distance.
 -  Ils s'arrêtent au premier joueur ou mur touché. Seul la partie colorée peut être touchée, les canons sont ignorés.
 -  Tous les tanks ont un seul point de vie, et sont donc éliminés au premier coup.
 -  Les tirs sont plus rapides que les mouvements avant et arrière, et plus lents que les dash à droite ou à gauche.
                """,
                color=global_values.color))
