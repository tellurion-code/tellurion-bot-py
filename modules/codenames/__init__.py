import discord
import asyncio
import random

from modules.codenames.game import Game
from modules.codenames.player import Player
from modules.base import BaseClassPython

import modules.codenames.globals as global_values
global_values.init()

class MainClass(BaseClassPython):
    name = "Codenames"
    help_active = True
    help = {
        "description": "Module du jeu Codenames",
        "commands": {
            "`{prefix}{command} create`": "Rejoint la partie de Codenames. S'il n'y en a pas dans le salon, en crée une nouvelle.",
            "`{prefix}{command} rules`": "Affiche les règles du jeu."
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.color = global_values.color

        self.config["color"] = self.color
        self.config["auth_everyone"] = True
        self.config["help_active"] = True
        self.config["configured"] = True
        self.config["command_text"] = "codenames"

    async def com_rules(self, message, args, kwargs):
        objectives = """
        Les joueurs sont répartis en deux équipes (Rouge et Bleue), avec un Spymaster au sein de chaque équipe.
        Chaque équipe doit deviner les mots (8 ou 9 mots selon l'équipe débutant la partie) qui lui appartiennent à l'aide des indices donnés par son Espion.
        La partie s'achève lorsqu'une équipe a deviné tous les mots ou si elle tombe sur le mot de l'Assassin.
        """

        gameprocess1 = """
    Le jeu se déroule au tour par tour, par équipe. Chaque tour se décompose en deux phases :

    :one: **Phase du Spymaster**

    Lors de cette phase, le Spymaster peut donner un indice qui est nécessairement de la forme `<mot> <chiffre>`, le chiffre désignant le nombre de cartes liées au `<mot>`.
    :warning: Tout indice ayant une proximité (homonymique, phonétique, sémantique) avec l'une des cartes est considéré comme invalide, tout comme ceux se rapportant à la position ou au nombre de lettes d'une carte.
    :no_entry_sign: En cas d'invalidité, le tour est terminé et l'équipe adverse peut marquer un de ses mots.
    """

        gameprocess2 = """
    :two: **Phase de l'équipe**

    L'équipe doit, à partir de l'indice du Spymaster, choisir un mot sur la grille.
    Si celui-ci correspond bien, il est marqué et le tour continue : l'équipe peut
    deviner un autre mot, à partir du même indice. L'équipe peut deviner jusqu'à autant de mots que chiffre donné en indice, plus 1.
    :stop_sign: Toute erreur met fin au tour.
    :dagger: Si le mot de l'Assassin est trouvé, l'équipe a immédiatement perdu.
    """

        gamerules = discord.Embed(title="Codenames - Règles du jeu", color=global_values.color)
        gamerules.add_field(name='Objectifs', value=objectives, inline=False)
        gamerules.add_field(name='Déroulement de la partie', value=gameprocess1, inline=False)
        gamerules.add_field(name='', value=gameprocess2, inline=False)
        await message.channel.send(embed=gamerules)

    async def com_create(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            await message.channel.send("Il y a déjà une partie en cours dans le salon")
        else:
            global_values.games[message.channel.id] = Game(message)
            await global_values.games[message.channel.id].create_game(message)

    async def com_show(self, message, args, kwargs):
        if message.channel.id not in global_values.games:
            await message.channel.send("Il n'y a pas de partie en cours dans le salon")
        else:
            game = global_values.games[message.channel.id]
            if game.turn == 0:
                await game.game_message.delete(True)
                await game.spymaster_message.delete()
                await game.send_game_messages()

    async def com_reset(self, message, args, kwargs):
        if message.channel.id in global_values.games:
            game = global_values.games[message.channel.id]
            await message.channel.send("La partie a été réinitialisée")

            if (game.game_message):
                await game.game_message.delete(False, True)

            if (game.spymaster_message):
                await game.spymaster_message.delete()

            global_values.games.pop(message.channel.id)
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            global_values.debug = not global_values.debug
            await message.channel.send("Debug: " + str(global_values.debug))
