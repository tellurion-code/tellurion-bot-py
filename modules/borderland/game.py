import discord
import random
import datetime
import asyncio

from modules.borderland.player import Player, Jack
from modules.borderland.reaction_message import ReactionMessage

import modules.borderland.globals as global_values


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
    def __init__(self, mainclass, **kwargs):
        message = kwargs["message"] if "message" in kwargs else None
        self.mainclass = mainclass

        if message:
            self.channel = message.channel
            self.starter = message.author.id
        else:
            self.starter = 0
            self.channel = None

        self.players = {}  # Dict pour rapidement accéder aux infos
        self.round = 0  # Nombre de manches
        self.roles = []  # Roles vides = à générer
        self.info_message = None
        self.in_game = []
        self.next_turn_timer = None

    async def reload(self, object, client):
        await self.deserialize(object, client)

        self.time_next_turn(datetime.datetime.fromtimestamp(object["time"]))

        for player in self.players.values():
            if player.choice == "":
                await player.send_choice_message()

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
            "🎴 🃏 Création de la partie de Borderland ❤️ ♠️ 🔷 🍀",
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


        await self.send_info(info="Début de partie")
        self.time_next_turn()

    # Envoies un message à tous les joueurs + le channel
    async def broadcast(self, _embed, **kwargs):
        exceptions = kwargs["exceptions"] if "exceptions" in kwargs else []
        mode = kwargs["mode"] if "mode" in kwargs else "normal"

        if mode == "append":  # append = ajoute à la description
            if self.info_message:
                embed = self.info_message.embeds[0]
                embed.description += _embed.description

                await self.info_message.edit(embed=embed)
            else:
                self.info_message = await self.channel.send(embed=_embed)

            for player_id in self.in_game:
                player = self.players[player_id]
                if player_id not in exceptions:
                    if player.info_message:
                        embed = player.info_message.embeds[0]
                        embed.description += _embed.description

                        await player.info_message.edit(embed=embed)
                    else:
                        player.info_message = await player.user.send(embed=_embed)
        elif mode == "replace":  # replace = modifie le dernier message
            if self.info_message:
                await self.info_message.edit(embed=_embed)
            else:
                self.info_message = await self.channel.send(embed=_embed)

            for player_id in self.in_game:
                player = self.players[player_id]
                if player_id not in exceptions:
                    if player.info_message:
                        await player.info_message.edit(embed=_embed)
                    else:
                        player.info_message = await player.user.send(embed=_embed)
        elif mode == "set":  # set = nouveau message avec mémoire
            self.info_message = await self.channel.send(embed=_embed)
            for player_id in self.in_game:
                player = self.players[player_id]
                if player_id not in exceptions:
                    player.info_message = await player.user.send(embed=_embed)
        else:  # normal = nouveau message sans mémoire
            await self.channel.send(embed=_embed)
            for player_id in self.in_game:
                player = self.players[player_id]
                if player_id not in exceptions:
                    await player.user.send(embed=_embed)

    # Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        info = kwargs["info"] if "info" in kwargs else ""
        color = kwargs["color"] if "color" in kwargs else global_values.color

        embed = discord.Embed(
            title="[BORDERLAND] Manche " + str(self.round),
            description="**N'oubliez pas d'envoyer votre choix avant demain.**\n" + info,
            color=color
        )

        embed.description += "\n\n__Joueurs restants:__\n" + '\n'.join(["• `" + str(self.players[x].user) + "` (`" + str(x) + "`)" for x in self.in_game])

        await self.broadcast(embed, mode=mode)

    def time_next_turn(self, tomorrow=None):
        # delay = datetime.timedelta(minutes=1).total_seconds()
        # delay = (datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=1), self.time) - datetime.datetime.now()).total_seconds()
        if not tomorrow:
            tomorrow = datetime.timedelta(hours=24)

        delay = tomorrow.total_seconds()

        self.next_turn_timer = Timer(delay, self.next_turn)
        self.save(tomorrow)

    # Elimine les joueurs qui n'ont pas répondu ou qui se sont trompés
    async def next_turn(self):
        if self.next_turn_timer:
            self.next_turn_timer.cancel()
            del self.next_turn_timer

        eliminated = []

        for player_id in self.in_game:
            player = self.players[player_id]
            if player.choice != player.symbol:
                await player.user.send(embed=discord.Embed(
                    title="[BORDERLAND] Elimination",
                    description="Vous avez été éliminé.",
                    color=0))
                eliminated.append(player)
            else:
                player.choice = ""
                player.symbol = random.choice(["❤️", "♠️", "🔷", "🍀"])

        for player in eliminated:
            self.in_game.remove(player.user.id)

        self.round += 1

        await self.send_info(
            info="__Joueurs éliminés:__\n" + ('\n'.join(["• `" + str(x.user) + "` " + x.symbol for x in eliminated]) if len(eliminated) else "Personne!"),
            mode="set")

        if len([x for x in eliminated if x.role == "jack"]):
            await self.end_game(False)
        elif len(self.in_game) <= (1 if global_values.debug else 2):
            await self.end_game(True)
        else:
            for player_id in self.in_game:
                await self.players[player_id].send_choice_message()

            self.time_next_turn()

    # Fin de partie, envoies le message de fin et détruit la partie
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
        self.delete_save()
        global_values.games.pop(self.channel.id)

    def serialize(self, time):
        object = {
            "channel": self.channel.id,
            "round": self.round,
            "starter": self.starter,
            "time": datetime.datetime.timestamp(time),
            "roles": self.roles,
            "info_message": self.info_message.id if self.info_message else None,
            "in_game": self.in_game,
            "players": {},
            "state": state
        }

        for id, player in self.players.items():
            object["players"][id] = {
                "role": player.role,
                "symbol": player.symbol,
                "choice": player.choice,
                "info_message": player.info_message.id if player.info_message else None,
                "user": player.user.id
            }

        return object

    async def deserialize(self, object, client):
        self.channel = client.get_channel(object["channel"])
        self.info_message = await self.channel.fetch_message(object["info_message"]) if object["info_message"] else None
        self.in_game = object["in_game"]
        self.players = {}
        self.round = object["round"]
        self.starter = object["starter"]
        self.roles = object["roles"]

        classes = {
            "random": Player,
            "jack": Jack
        }

        for id, info in object["players"].items():
            player = self.players[int(id)] = classes[info["role"]](client.get_user(info["user"]))
            player.symbol = info["symbol"]
            player.choice = info["choice"]
            player.info_message = await player.user.fetch_message(info["info_message"]) if info["info_message"] else None

    def save(self, time):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
        else:
            object = {}

        object[self.channel.id] = self.serialize(time)
        self.mainclass.objects.save_object("games", object)

    def delete_save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
            if str(self.channel.id) in object:
                object.pop(str(self.channel.id))

            self.mainclass.objects.save_object("games", object)
        else:
            print("no save")
