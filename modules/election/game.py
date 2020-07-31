import discord
import random

from modules.election.player import Player
from modules.reaction_message.reaction_message import ReactionMessage

import modules.election.globals as global_values

classes = {"player": Player}
classes.update({c.__name__.lower(): c for c in Player.__subclasses__()})

class Game:
    def __init__(self, mainclass, **kwargs):
        message = kwargs["message"] if "message" in kwargs else None
        self.mainclass = mainclass

        if message:
            self.channel = message.channel
            self.players = {
                message.author.id: Player(message.author)
            }  # Dict pour rapidement accéder aux infos
        else:
            self.channel = None
            self.players = {}

        self.order = []  # Ordre des id des joueurs
        self.turn = -1  # Le nombre de tours, -1 = pas commencé
        self.info_message = None
        self.roles = []  # Rôles
        self.tied = False
        self.minister = 0  # Id du ministre
        self.head_of_state = 0  # If du Chef d'Etat
        self.gamerules = {
            "minister_on": True,
            "head_of_state_on": True
        }

    async def reload(self, object, client):
        await self.deserialize(object, client)

        if object["state"]["type"] == "send_team_choice":
            await self.send_team_choice()
        elif object["state"]["type"] == "quest":
            await self.send_players_quest_choice()
        elif object["state"]["type"] == "next_turn":
            await self.next_turn()

    async def on_creation(self, message):
        async def start(reactions):
            await self.start_game()

        async def update(reactions):
            if len([0 for x in reactions.values() if 0 in x]):
                await self.game_creation_message.message.remove_reaction("📩", self.mainclass.client.user)
            else:
                await self.game_creation_message.message.add_reaction("📩")

            self.players = {}
            for player_id, reaction in reactions.items():
                if 0 in reaction:
                    self.players[player_id] = Player(self.mainclass.client.get_user(player_id))

            embed = self.game_creation_message.message.embeds[0]
            embed.description = "Cliquez sur la réaction 📩 pour rejoindre la partie.\n\n__Joueurs:__\n" + '\n'.join(["`"+ str(x.user) + "`" for x in self.players.values()])
            await self.game_creation_message.message.edit(embed=embed)

        async def cond(reactions):
            return len([0 for x in reactions.values() if 0 in x]) in range(5, 14) or global_values.debug

        self.game_creation_message = ReactionMessage(
            cond,
            start,
            update=update,
            check=lambda r, u: r.emoji == "📩" or u.id == message.author.id
        )

        await self.game_creation_message.send(
            message.channel,
            "Création de la partie d'Election",
            "Cliquez sur la réaction 📩 pour vous inscrire au jeu.\n\n__Joueurs:__\n",
            global_values.color,
            ["Inscription"],
            emojis=["📩"],
            silent=True
        )

    async def start_game(self):
        self.turn = 0

        if len(self.roles) == 0:
            self.roles = ["player" for _ in len(self.players)]

        for player_id in self.players:
            self.order.append(player_id)

        random.shuffle(self.order)
        random.shuffle(self.roles)

        for i in range(len(self.order)):
            self.players[self.order[i]] = classes[self.roles[i]](self.players[self.order[i]].user)

        for i in range(len(self.order)):
            await self.players[self.order[i]].game_start(self)

        random.shuffle(self.roles)

        await self.next_turn()

    # Envoie un message à tous les joueurs + le channel
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

            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    if player_object.info_message:
                        embed = player_object.info_message.embeds[0]
                        embed.description += _embed.description

                        await player_object.info_message.edit(embed=embed)
                    else:
                        player_object.info_message = await player_object.user.send(embed=_embed)
        elif mode == "replace":  # replace = modifie le dernier message
            if self.info_message:
                await self.info_message.edit(embed=_embed)
            else:
                self.info_message = await self.channel.send(embed=_embed)

            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    if player_object.info_message:
                        await player_object.info_message.edit(embed=_embed)
                    else:
                        player_object.info_message = await player_object.user.send(embed=_embed)
        elif mode == "set":  # set = nouveau message
            self.info_message = await self.channel.send(embed=_embed)
            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    player_object.info_message = await player_object.user.send(embed=_embed)
        else:  # normal = nouveau message sans mémoire
            await self.channel.send(embed=_embed)
            for player_id, player_object in self.players.items():
                if player_id not in exceptions:
                    await player_object.user.send(embed=_embed)

    # Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        info = kwargs["info"] if "info" in kwargs else None
        color = kwargs["color"] if "color" in kwargs else global_values.color

        embed = discord.Embed(
            title="[ELECTION] Tour " + str(self.turn),
            description="",
            color=color
        )

        embed.add_field(
            name="Joueurs :",
            value='\n'.join([global_values.number_emojis[i] + " `" + str(self.players[x].user) + "` " + ("👑 " if not self.head_of_state == x else "") + ("🎩 " if not self.minister == x else "") + ("💀 " if not self.players[x].alive else "") + ("✉️ " * max(0, self.players[x].votes + self.players[x].bonus)) + ("❌ " * min(0, -(self.players[x].votes + self.players[x].bonus))) for i, x in enumerate(self.order)]),
            inline=False
        )

        if info:
            embed.add_field(name=info["name"], value=info["value"])

        # --[ANCIEN BROADCAST]--
        # await self.channel.send(embed = embed)
        # for player in self.players.values():
        #     await player.user.send(embed = embed)

        await self.broadcast(embed, mode=mode)

    async def next_turn(self, message=None):
        # self.save({"type":"next_turn"})

        alives = [x for x in self.players.values() if x.alive]
        if len(alives) == 1:
            await self.end_game(str(alives[0].user), "Survie")
        else:
            self.tied = False
            self.turn = self.turn + 1

            for player in self.players.values():
                player.last_vote = -1
                player.votes = player.bonus

            await self.send_info(mode="set", info=message)

            if self.head_of_state:
                head_of_state = self.players[self.head_of_state]

                choices = [i for i, x in enumerate(self.order) if self.players[x].alive and (x != self.head_of_state or global_values.debug)]
                visual_choices = ["`" + str(self.players[self.order[i]].user) + "`" for i in choices]
                emojis = [global_values.number_emojis[i] for i in choices]

                choices.append("-1")
                visual_choices.append("Personne")
                emojis.append("🚫")

                async def malus(reactions):
                    if reactions[self.head_of_state][0] + 1 < len(choices):
                        self.players[self.order[choices[reactions[self.head_of_state][0]]]].bonus -= 1

                        await self.send_info({
                            "name": "Malus",
                            "value": "Le Chef d'Etat `" + str(head_of_state.user) + "` a décidé de retirer une voix à `" + self.players[self.order[choices[reactions[self.head_of_state][0]]]] +  "`"
                        })

                    for player in self.players.values():
                        await player.send_vote(self)

                async def cond(reactions):
                    return len(reactions[self.head_of_state]) == 1

                await ReactionMessage(
                    cond,
                    malus
                ).send(
                    head_of_state.user,
                    "👑 Pouvoir du Chef d'Etat",
                    "Choisissez le joueur a qui vous voulez retirer une voix",
                    global_values.color,
                    visual_choices,
                    emojis=emojis
                )
            else:
                for player in self.players.values():
                    await player.send_vote(self)

    # Appelé à chaque fois qu'un joueur vote. Vérifie les votes manquants puis la majorité
    async def check_vote_end(self):
        missing = False

        for player_id in self.order:
            player = self.players[player_id]

            if player.last_vote == -1:
                missing = True

            if player.vote_message:
                embed = player.vote_message.message.embeds[0]
                embed.set_field_at(
                    0,
                    name="Votes:",
                    value=' '.join(["✉️" if self.players[x].last_vote == -1 else "📩" for x in self.order])
                )

                if player.last_vote > -1:
                    embed.description = "Vous avez voté pour " + global_values.number_emojis[player.last_vote] + " `" + str(self.players[self.order[player.last_vote]].user) + "`"

                await player.vote_message.message.edit(embed=embed)

        if not missing:
            for i, player_id in enumerate(self.order):
                player = self.players[player_id]

                if player.vote_message:
                    await player.vote_message.message.delete()

                player.votes = len([0 for x in self.players.values() if x.last_vote == i]) + player.bonus
                player.bonus = 0

            self.order.sort(key=lambda e: self.players[e].votes, reverse=True)

            self.minister = 0
            self.head_of_state = 0
            if len([0 for x in self.players.values() if x.alive]) > 2:
                if len([0 for x in self.players.values() if x.votes == self.players[self.order[0]].votes]) == 1:
                    if self.gamerules["minister_on"]:
                        self.minister = self.order[0]
                        self.players[self.order[0]].bonus += 1
                        message = {
                            "name": "Nomination",
                            "value": "`" + str(self.players[self.order[0]].user) + "` est devenu le Ministre 🎩, et aura donc une voix bonus au prochain tour"
                        }

                    if self.players[self.order[0]].votes >= len(self.players)/2 and self.gamerules["head_of_state_on"]:
                        self.head_of_state = self.order[0]

                        message = {
                            "name": "Nomination",
                            "value": "`" + str(self.players[self.order[0]].user) + "` est devenu le Chef d'Etat 👑, et aura donc une voix bonus au prochain tour, ainsi que la possibilité de retirer une voix à un joueur"
                        }

            if len([0 for x in self.players.values() if x.votes == self.players[self.order[-1]].votes]) > 1 and not self.tied:
                tied = [i for i, x in enumerate(self.order) if self.players[x].votes == self.players[self.order[-1]].votes]
                info, next, end = "", False, False
                for player in self.players.values():
                    i, n, e = await player.on_tie(self, tied)

                    if i:
                        info += i

                    if n:
                        next = True

                    if e:
                        end = True

                await self.send_info(info={
                    "name": "Egalité",
                    "value": ', '.join(["`" + str(self.players[self.order[i]].user) + "`" for i in tied][:-1]) + "et `" + str(self.players[self.order[tied[-1]]].user) + "` sont à égalité. Un second vote a été lancé pour déterminer qui sera éliminé. **Une seconde égalité sera résolue au hasard.**" + info
                })

                if end:
                    return

                if next:
                    await self.next_turn(info=message)
                else:
                    await self.break_tie(tied)
            else:
                eliminated = random.choice([x for x in self.order if self.players[x].votes == self.players[self.order[-1]].votes])

                if await self.eliminate(eliminated):
                    return

                await self.next_turn(info=message)

    async def eliminate(self, eliminated):
        self.players[eliminated].alive = False
        info, end = "", False
        for player in self.players.values():
            i, e = await player.on_kill(self, eliminated)

            if i:
                info += i

            if e:
                end = True

        await self.send_info(info={
            "name": "Elimination",
            "value": "`" + str(self.players[eliminated].user) + "` a été éliminé." + info
        })

        return end

    async def break_tie(self, tied):
        self.tied = True

        for player in self.players.values():
            player.last_vote = -1

        for player in self.players.values():
            await player.send_vote(self, choice=tied)

    # Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, winner, cause):
        embed = discord.Embed(title="[ELECTION] Victoire " + ("d'`" if winner[:1] in "EAIOU" else "de`") + winner + "` par " + cause  + " !", color=global_values.color)

        embed.description = "**Joueurs :**\n" + '\n'.join([global_values.number_emojis[i] + " `" + str(self.players[x].user) + "` : " + self.players[x].name for i, x in enumerate(self.order)])

        await self.broadcast(embed)
        self.delete_save()
        del global_values.games[self.channel.id]

    def serialize(self, state):
        object = {
            "channel": self.channel.id,
            "order": self.order,
            "turn": self.turn,
            "round": self.round,
            "team": self.team,
            "refused": self.refused,
            "quests": self.quests,
            "info_message": self.info_message.id if self.info_message else None,
            "played": self.played,
            "lady_of_the_lake": self.lady_of_the_lake,
            "roles": self.roles,
            "phase": self.phase,
            "gamerules": self.gamerules,
            "players": {},
            "state": state
        }

        for id, player in self.players.items():
            object["players"][id] = {
                "role": player.role,
                "last_vote": player.last_vote,
                "inspected": player.inspected,
                "quest_choices": player.quest_choices,
                "info_message": player.info_message.id if player.info_message else None,
                "user": player.user.id
            }

        return object

    async def deserialize(self, object, client):
        self.channel = client.get_channel(object["channel"])
        self.order = object["order"]
        self.turn = int(object["turn"])
        self.round = int(object["round"])
        self.quests = object["quests"]
        self.roles = object["roles"]
        self.phase = object["phase"]
        self.gamerules = object["gamerules"]
        self.refused = int(object["refused"])
        self.info_message = await self.channel.fetch_message(object["info_message"]) if object["info_message"] else None
        self.played = object["played"]
        self.lady_of_the_lake = object["lady_of_the_lake"]
        self.players = {}
        self.team = {}

        for i, id in object["team"].items():
            self.team[int(i)] = int(id)

        for id, info in object["players"].items():
            player = self.players[int(id)] = classes[info["role"]](client.get_user(info["user"]))
            player.last_vote = info["last_vote"]
            player.inspected = info["inspected"]
            player.quest_choices = info["quest_choices"]
            player.info_message = await player.user.fetch_message(info["info_message"]) if info["info_message"] else None

    def save(self, state):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
        else:
            object = {}

        object[self.channel.id] = self.serialize(state)
        self.mainclass.objects.save_object("games", object)

    def delete_save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
            if str(self.channel.id) in object:
                object.pop(str(self.channel.id))

            self.mainclass.objects.save_object("games", object)
        else:
            print("no save")

  # Module créé par Le Codex#9836. Idée originale par Kaznad#6511
