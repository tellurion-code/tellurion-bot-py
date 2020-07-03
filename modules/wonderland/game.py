import discord
import random
import datetime
import asyncio

from modules.wonderland.player import Player, Jack
from modules.wonderland.reaction_message import ReactionMessage

import modules.wonderland.globals as global_values

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()

class Game:
    def __init__(self, message, mainclass):
        self.mainclass = mainclass
        self.channel = message.channel
        self.players = {} #Dict pour rapidement accéder aux infos
        self.round = 0 #Nombre de manches
        self.time = 0 #Heure à laquelle le jour finit
        self.roles = [] #Roles vides = à générer
        self.info_message = None
        self.in_game = []

    async def on_creation(self, message):
        async def update(reactions):
            self.players = {}

            for player_id, reaction in reactions.items():
                if 0 in reaction:
                    self.players[player_id] = Player(self.mainclass.client.get_user(player_id))

            embed = game_creation_message.message.embeds[0]

            embed.description = "Appuyez sur la réaction 📩 pour vous inscrire au jeu.\n\n__Joueurs:__\n" + '\n'.join(["`"+ str(x.user) + "`" for x in self.players.values()])

            await game_creation_message.message.edit(embed=embed)

        async def cond(reactions):
            return False

        game_creation_message = ReactionMessage(
            cond,
            None,
            update=update,
            temporary=False
        )

        await game_creation_message.send(
            message.channel,
            "🎴 🃏 Création de la partie de Wonderland ❤️ ♠️ 🔷 🍀",
            "Appuyez sur la réaction 📩 pour vous inscrire au jeu.\n\n__Joueurs:__\n",
            global_values.color,
            ["Inscription"],
            emojis=["📩"],
            silent=True
        )

    async def start_game(self):
        self.round = 1

        roles = {
            "jack": Jack
        }

        if not len(self.roles):
            self.roles = ["jack"]

        while len(self.roles):
            selected = random.choice([x for x in self.players])
            while self.players[selected].role != "random":
                selected = random.choice([x for x in self.players])

            self.players[selected] = roles[self.roles.pop()](self.players[selected].user)

        for player_id, player in self.players.items():
            await player.game_start(self)
            self.in_game.append(player_id)

        self.time = datetime.datetime.now().time()

        await self.send_info(info="Début de partie")

        # delay = datetime.timedelta(minutes=1).total_seconds()
        delay = ((datetime.date.today() + datetime.timedelta(day=1,hours=self.time)) - datetime.now()).total_seconds()
        timer = Timer(delay, self.next_turn)

    #Envoies un message à tous les joueurs + le channel
    async def broadcast(self, _embed, **kwargs):
        exceptions = kwargs["exceptions"] if "exceptions" in kwargs else []
        mode = kwargs["mode"] if "mode" in kwargs else "normal"

        if mode == "append": #append = ajoute à la description
            if self.info_message:
                embed = self.info_message.embeds[0]
                embed.description += _embed.description

                await self.info_message.edit(embed=embed)
            else:
                self.info_message = await self.channel.send(embed=_embed)

            for id in self.in_game:
                if id not in exceptions:
                    if player.info_message:
                        embed = player.info_message.embeds[0]
                        embed.description += _embed.description

                        await player.info_message.edit(embed=embed)
                    else:
                        player.info_message = await player.user.send(embed=_embed)
        elif mode == "replace": #replace = modifie le dernier message
            if self.info_message:
                await self.info_message.edit(embed=_embed)
            else:
                self.info_message = await self.channel.send(embed=_embed)

            for id in self.in_game:
                player = self.players[id]
                if id not in exceptions:
                    if player.info_message:
                        await player.info_message.edit(embed=_embed)
                    else:
                        player.info_message = await player.user.send(embed=_embed)
        elif mode == "set": #set = nouveau message avec mémoire
            self.info_message = await self.channel.send(embed=_embed)
            for id in self.in_game:
                player = self.players[id]
                if id not in exceptions:
                    player.info_message = await player.user.send(embed=_embed)
        else: #normal = nouveau message sans mémoire
            await self.channel.send(embed=_embed)
            for id in self.in_game:
                player = self.players[id]
                if id not in exceptions:
                    await player.user.send(embed=_embed)

    #Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        info = kwargs["info"] if "info" in kwargs else ""
        color = kwargs["color"] if "color" in kwargs else global_values.color

        embed = discord.Embed(
            title="[WONDERLAND] Manche " + str(self.round),
            description="**N'oubliez pas d'envoyer votre choix avant demain, " + self.time.strftime("%H") + "h00.**\n" + info,
            color=color
        )

        embed.description += "\n\n__Joueurs restants:__\n" + '\n'.join(["• `" + str(self.players[x].user) + "` (`" + str(x) + "`)" for x in self.in_game])

        await self.broadcast(embed, mode=mode)

    #Elimine les joueurs qui n'ont pas répondu ou qui se sont trompés
    async def next_turn(self):
        eliminated = []

        for player_id in self.in_game:
            player = self.players[player_id]
            if player.choice != player.symbol:
                await player.user.send(embed=discord.Embed(
                    title="[WONDERLAND] Elimination",
                    description="Vous avez été éliminé.",
                    color=0))
                eliminated.append(player)
            else:
                player.choice = ""
                player.symbol = random.choice(["❤️", "♠️", "🔷", "🍀"])

        for player in eliminated:
            self.in_game.remove(player.user.id)

        self.round += 1
        print("Passed")

        await self.send_info(
            info="__Joueurs éliminés:__\n" + ('\n'.join(["• `" + str(x.user) + "` " + x.symbol for x in eliminated]) if len(eliminated) else "Personne!"),
            mode="set")

        if len([x for x in eliminated if x.role == "jack"]):
            await self.end_game(False)
        elif len(self.players) <= (1 if global_values.debug else 2):
            await self.end_game(True)
        else:
            for player_id in self.in_game:
                await self.players[player_id].send_choice_message()

            # delay = datetime.timedelta(minutes=1).total_seconds()
            delay = ((datetime.date.today() + datetime.timedelta(day=1,hours=self.time)) - datetime.now()).total_seconds()
            timer = Timer(delay, self.next_turn)

    #Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, jack_wins):
        if jack_wins:
            embed = discord.Embed(title="🃏 Victoire du Valet de Coeur! 🃏", color=0xfffffe)
        else:
            embed = discord.Embed(title="🎴 Victoire de l'équipe des randoms! 🎴", color=global_values.color)

        roles = {
            "random": "🎴 Random",
            "jack": "🃏 Valet de Coeur"
        }

        embed.description="__Joueurs restants:__\n" + '\n'.join(["`" + str(x.user) + "` : " + roles[x.role] for x in self.players.values()])

        await self.broadcast(embed)
        global_values.games.pop(self.channel.id)
