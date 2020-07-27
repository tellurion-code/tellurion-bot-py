import discord
import random
import math
import copy

from modules.petri.player import Player
from modules.reaction_message.reaction_message import ReactionMessage

import modules.petri.globals as global_values

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
        self.turn = -1  # Le tour (index du joueur en cours) en cours, -1 = pas commencé
        self.round = 1  # Le nombre de tours de table complets
        self.map = []  # Carte où la partie se déroule
        self.ranges = [10, 10, 2]  # Taille horizontale, taille verticale, nombre de murs par quartiers
        self.info_message = None
        self.game_creation_message = None

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
            if len([0 for x in reactions.values() if len(x)]):
                await self.game_creation_message.message.remove_reaction("📩", self.mainclass.client.user)
            else:
                await self.game_creation_message.message.add_reaction("📩")

            self.players = {}

            for player_id, reaction in reactions.items():
                if 0 in reaction:
                    self.players[player_id] = Player(self.mainclass.client.get_user(player_id))

            embed = self.game_creation_message.message.embeds[0]

            embed.description = "Appuyez sur la réaction 📩 pour rejoindre la partie.\n\n__Joueurs:__\n" + '\n'.join(["`"+ str(x.user) + "`" for x in self.players.values()])

            await self.game_creation_message.message.edit(embed=embed)

        async def cond(reactions):
            return len(reactions) in range(2, 7)

        self.game_creation_message = ReactionMessage(
            cond,
            start,
            update=update,
            check=lambda r, u: r.emoji != "✅" or u.id == message.author.id
        )

        await self.game_creation_message.send(
            message.channel,
            "Création de la partie de Petri",
            "Appuyez sur la réaction 📩 pour vous inscrire au jeu.\n\n__Joueurs:__\n",
            global_values.color,
            ["Inscription"],
            emojis=["📩"],
            silent=True
        )

    async def start_game(self):
        self.turn = 0
        self.game_creation_message = None

        for y in range(self.ranges[1]):
            self.map.append([])
            for _ in range(self.ranges[0]):
                self.map[y].append(-1)  # -1 = vide, -2 = mur

        for my in range(self.ranges[1], int(self.ranges[1]/2)):
            for mx in range(self.ranges[0], int(self.ranges[0]/2)):
                for _ in range(self.ranges[2]):
                    while True:
                        x = random.randrange(mx, int(mx + self.ranges[0]/2))
                        y = random.randrange(my, int(my + self.ranges[1]/2))
                        if self.map[y][x] == -1:
                            break

                    self.map[y][x] = -2

        r, a = round(min(self.ranges[0], self.ranges[1])/3), random.uniform(0, math.pi*2)

        for player_id in self.players:
            while self.map[int(self.ranges[1]/2 + .5 + r * math.sin(a))][int(self.ranges[0]/2 + .5 + r * math.cos(a))] != -1:
                a += math.pi/20

            self.map[int(self.ranges[1]/2 + .5 + r * math.sin(a))][int(self.ranges[0]/2 + .5 + r * math.cos(a))] = len(self.order)
            self.order.append(player_id)

            a += math.pi/len(self.players) * 2

        random.shuffle(self.order)

        await self.send_info()

    # Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        info = kwargs["info"] if "info" in kwargs else None
        color = kwargs["color"] if "color" in kwargs else global_values.color

        row_strings = []
        for y in range(self.ranges[1]):
            row_strings.append("")
            for x in range(self.ranges[0]):
                row_strings[-1] += global_values.tile_colors[self.map[y][x] + 2]

        map_string = '\n'.join(row_strings)

        fields = []

        fields.append({
            "name": "Joueurs (Score de Domination: " + str(int((self.ranges[0] * self.ranges[1])/2)) +  ")",
            "value":'\n'.join([global_values.tile_colors[i + 2] + " `" + str(self.players[x].user) + "` : " + str(len([0 for row in self.map for tile in row if tile == i])) for i, x in enumerate(self.order)])
        })

        if self.round > 50:
            fields.append({
                "name": "💀 Mort Subite 💀",
                "value": "Le premier joueur à prendre l'avantage gagne"
            })

        if info:
            fields.append({
                "name": info["name"],
                "value": info["value"]
            })

        # --[ANCIEN BROADCAST]--
        # await self.channel.send(embed = embed)
        # for player in self.players.values():
        #     await player.user.send(embed = embed)

        if self.info_message:
            embed=discord.Embed(
                title="[PETRI Manche " + str(self.round) + "] Tour de `" + str(self.players[self.order[self.turn]].user) + "`",
                description=map_string,
                color=global_values.player_colors[self.turn]
            )

            for field in fields:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"] if "inline" in field else False
                )

            await self.info_message.message.edit(embed=embed)
        else:
            async def next_turn(reactions):
                if self.order[self.turn] in reactions:
                    if len(reactions[self.order[self.turn]]):
                        summary = self.process_direction(reactions[self.order[self.turn]][0])
                        await self.info_message.message.remove_reaction(global_values.arrow_emojis[reactions[self.order[self.turn]][0]], self.players[self.order[self.turn]].user)

                        self.info_message.reactions = {}

                        await self.next_turn(None if len(summary) == 0 else {
                            "name": "Combats",
                            "value": summary
                        })

            async def cond(reactions):
                return False

            self.info_message = ReactionMessage(
                cond,
                None,
                update=next_turn,
                temporary=False,
                check=lambda r, u: u.id == self.order[self.turn]
            )

            await self.info_message.send(
                self.channel,
                "[PETRI Manche " + str(self.round) + "] Tour de `" + str(self.players[self.order[self.turn]].user) + "`",
                map_string,
                global_values.player_colors[self.turn],
                ["Haut", "Droite", "Bas", "Gauche"],
                emojis=global_values.arrow_emojis,
                silent=True,
                fields=fields
            )

    def inside(self, x, y):
        return x >= 0 and x < self.ranges[0] and y >= 0 and y < self.ranges[1]

    #Gère les combats et les réplications
    def process_direction(self, choice):
        dx = [0, 1, 0 , -1][choice]
        dy = [-1, 0, 1 , 0][choice]
        new_map = copy.deepcopy(self.map)
        summary = []

        for y in range(self.ranges[1]):
            for x in range (self.ranges[0]):
                if self.map[y][x] == self.turn and self.inside(x + dx, y + dy):
                    new_tile = self.map[y + dy][x + dx]
                    if new_tile == -1:
                        new_map[y + dy][x + dx] = self.turn
                    elif new_tile >= 0 and new_tile != self.turn:
                        attack, defense = 0, 0
                        tdx, tdy = 0, 0

                        while self.map[y + tdy][x + tdx] == self.turn:
                            attack += 1
                            tdx -= dx
                            tdy -= dy
                            if not self.inside(x + tdx, y + tdy):
                                break

                        tdx, tdy = dx, dy
                        while self.map[y + tdy][x + tdx] == new_tile:
                            defense += 1
                            tdx += dx
                            tdy += dy
                            if not self.inside(x + tdx, y + tdy):
                                break

                        if attack > defense:
                            new_map[y + dy][x + dx] = self.turn
                            summary.append(global_values.tile_colors[self.turn + 2] + " `" + str(self.players[self.order[self.turn]].user) + "`️ 🗡️ " + global_values.tile_colors[new_tile + 2] + " `" + str(self.players[self.order[new_tile]].user) + "`")
                        elif attack == defense:
                            new_map[y + dy][x + dx] = -1
                            summary.append(global_values.tile_colors[self.turn + 2] + " `" + str(self.players[self.order[self.turn]].user) + "`️ ⚔️️ " + global_values.tile_colors[new_tile + 2] + " `" + str(self.players[self.order[new_tile]].user) + "`")
                        else:
                            summary.append(global_values.tile_colors[new_tile + 2] + " `" + str(self.players[self.order[new_tile]].user) + "` 🛡️ " + global_values.tile_colors[self.turn + 2] + " `" + str(self.players[self.order[self.turn]].user) + "`️")

        self.map = new_map
        summary.sort()
        return '\n'.join(summary)

    # Passe au prochain tour
    async def next_turn(self, message=None):
        old_turn = self.turn

        while True:
            self.turn = (self.turn + 1) % len(self.order)
            if self.turn == 0:
                self.round += 1

            if len([0 for row in self.map for tile in row if tile == self.turn]):
                break

        await self.send_info(info=message)

        if self.round == 51:
            max_score, winner, tie = 0, 0, False
            for i, player_id in enumerate(self.order):
                score = len([0 for row in self.map for tile in row if tile == i])
                if score == max_score:
                    tie = True
                elif score > max_score:
                    tie = False
                    max_score = score
                    winner = player_id

            if not tie:
                await self.end_game(str(self.players[self.order[self.turn]].user), "Usure")
                return

        if self.turn == old_turn:
            await self.end_game(str(self.players[self.order[self.turn]].user), "Annihiliation")
        else:
            for i in range(len(self.order)):
                if len([0 for row in self.map for tile in row if tile == i]) >= (self.ranges[0] * self.ranges[1])/2:
                    await self.end_game(str(self.players[self.order[i]].user), "Domination")
                    return

    # Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, name, cause):
        embed = discord.Embed(title="[PETRI] Victoire " + ("d'`" if name[:1] in "EAIOU" else "de `") + name + "` par " + cause  + " !", color=global_values.color)

        embed.description = "**Joueurs :**\n" + '\n'.join([global_values.tile_colors[i + 2] + " `" + str(self.players[x].user) + "` : " + str(len([0 for row in self.map for tile in row if tile == i])) for i, x in enumerate(self.order)])

        if self.info_message:
            await self.info_message.delete()
            await self.info_message.message.clear_reactions()

        await self.channel.send(embed=embed)
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
            "gamerules": self.game_rules,
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
        self.game_rules = object["gamerules"]
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
