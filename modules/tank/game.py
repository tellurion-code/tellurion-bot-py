import discord
import random
import math
import copy
import asyncio

from modules.reaction_message.reaction_message import ReactionMessage
from modules.tank.player import Player

import modules.tank.globals as global_values

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

        self.order = []
        self.round = -1  # Le nombre de tours de table complets
        self.map = []  # Carte où la partie se déroule
        self.info_message = None
        self.game_creation_message = None
        self.phase = "plan"
        # self.power_selection_message = None

    async def reload(self, object, client):
        await self.deserialize(object, client)
        await self.send_info()

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

            # embed.set_field_at(
            #     0,
            #     name="🦸 Pouvoirs",
            #     value="Activé" if len([0 for x in reactions.values() if 0 in x]) else "Désactivé"
            # )

            embed.description = "Cliquez sur la réaction 📩 pour rejoindre la partie.\n\n__Joueurs:__\n" + '\n'.join(["`"+ str(x.user) + "`" for x in self.players.values()])
            await self.game_creation_message.message.edit(embed=embed)

        async def cond(reactions):
            return len([0 for x in reactions.values() if 0 in x]) in range(2, 7)

        self.game_creation_message = ReactionMessage(
            cond,
            start,
            update=update,
            check=lambda r, u: r.emoji == "📩" or u.id == message.author.id
        )

        await self.game_creation_message.send(
            message.channel,
            "Création de la partie de Tank",
            "Appuyez sur la réaction 📩 pour vous inscrire au jeu.\n\n__Joueurs:__\n",
            global_values.color,
            ["Inscription"],
            emojis=["📩"],
            silent=True
        )

    # async def send_power_selection(self):
    #     choices = list(classes.keys())
    #     emojis = [classes[x].name.split()[0] for x in choices]
    #     fields = [{
    #         "name": classes[x].name,
    #         "value": classes[x].description
    #     } for x in choices]
    #
    #     async def start(reactions):
    #         for player_id, choice in reactions.items():
    #             self.players[player_id] = classes[choices[choice[0]]](self.players[player_id].user)
    #
    #         await self.start_game()
    #
    #     async def cond(reactions):
    #         return len([0 for x in reactions.values() if len(x) == 1]) == len(self.players)
    #
    #     self.power_selection_message = ReactionMessage(
    #         cond,
    #         start,
    #         check=lambda r, u: u.id in self.players
    #     )
    #
    #     await self.power_selection_message.send(
    #         self.channel,
    #         "🦸 Choix des pouvoirs",
    #         "Choississez un pouvoir pour la partie",
    #         global_values.color,
    #         choices,
    #         emojis=emojis,
    #         silent=True,
    #         fields=fields
    #     )

    async def start_game(self):
        self.round = 1
        self.game_creation_message = None
        # self.power_selection_message = None

        map = copy.deepcopy(random.choice(random.choice(global_values.maps[len(self.players)-2:-1])))
        self.map = map["map"]

        for player_id, player in self.players.items():
            self.order.append(player_id)

        random.shuffle(self.order)

        for i, player_id in enumerate(self.order):
            self.players[player_id].index = i

            spawnpoint = map["spawnpoints"][i]
            self.players[player_id].spawn(self, self.map, spawnpoint[0], spawnpoint[1], spawnpoint[2])

        await self.send_info()
        # self.save()

    # Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        info = kwargs["info"] if "info" in kwargs else None
        color = kwargs["color"] if "color" in kwargs else global_values.color

        def draw_tile(x, y):
            for player_id in self.order:
                player = self.players[player_id]
                if player.x == x and player.y == y:
                    row_strings[-1] += global_values.player_colors[player.index]
                    return
                elif player.x + global_values.dir_x[player.direction] == x and player.y + global_values.dir_y[player.direction] == y:
                    row_strings[-1] += global_values.direction_emojis[player.direction]
                    return

            row_strings[-1] += global_values.tile_colors[self.map[y][x] + 1]

        row_strings = []
        for y in range(len(self.map)):
            row_strings.append("")
            for x in range(len(self.map[y])):
                 draw_tile(x, y)

        map_string = '\n'.join(row_strings)

        fields = []

        fields.append({
            "name": "Joueurs",
            "value": ('\n'.join([global_values.player_colors[self.players[x].index] + " `" + str(self.players[x].user) + "` " + ("▫️" * self.players[x].ammo if self.players[x].ammo else "🚫") + (" ✅" if self.players[x].confirmed else "") for i, x in enumerate(self.order)]) if len(self.order) else "💀 Aucun")
        })

        if info:
            fields.append({
                "name": info["name"],
                "value": info["value"]
            })

        if self.info_message:
            embed=discord.Embed(
                title="[TANK Manche " + str(self.round) + "] Planification",
                description=map_string,
                color=global_values.color
            )

            for field in fields:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"] if "inline" in field else False
                )

            await self.info_message.message.edit(embed=embed)
        else:
            choices = ["CCW", "CW", "FW", "BW", "DL", "DR", "S", "P", "V"]

            async def next_turn(reactions):
                for id, l in reactions.items():
                    if 8 in l and not self.players[id].confirmed:
                        self.players[id].confirmed = True
                        await self.send_info()

                if len([0 for id in self.order if self.players[id].confirmed]) == len(self.order) and self.phase == "plan":
                    self.phase = "act"
                    embed = self.info_message.message.embeds[0]
                    embed.title = "[TANK Manche " + str(self.round) + "] Action"
                    await self.info_message.message.edit(embed=embed)

                    dead = await self.process_inputs(copy.deepcopy(reactions))

                    await self.next_turn({
                        "name": "Eliminations:",
                        "value": dead
                    } if len(dead) else None)

            async def cond(reactions):
                return False

            def check(reaction, user):
                if user.id in self.info_message.reactions:
                    return not self.players[user.id].confirmed
                else:
                    return user.id in self.order

            self.info_message = ReactionMessage(
                cond,
                None,
                update=next_turn,
                temporary=False,
                check=check
            )

            await self.info_message.send(
                self.channel,
                "[TANK Manche " + str(self.round) + "] Planification",
                map_string,
                global_values.color,
                choices,
                emojis=global_values.choice_emojis,
                silent=True,
                fields=fields,
                validation_emoji="⭕"
            )

    def inside(self, x, y):
        if y >= 0 and y < len(self.map):
            return x >= 0 and x < len(self.map[y])
        else:
            return False

    #Gère les combats et les réplications
    async def process_inputs(self, reactions):
        new_map = copy.deepcopy(self.map)
        dead = []
        visual_cache = []

        for player_id in self.order:
            if player_id in reactions:
                if 6 not in reactions[player_id]:
                    self.players[player_id].ammo = min(self.players[player_id].ammo_max, self.players[player_id].ammo + 1)

        while len([0 for id in self.order if len(reactions[id]) > 1]):
            print(reactions)

            # Reset du cache
            visual_cache = []
            for y in range(len(self.map)):
                visual_cache.append(["" for _ in range(len(self.map[y]))])

            # Rotation
            def try_and_change_direction(player, diff):
                new_dir = (player.direction + diff) % 4
                if self.inside(player.x + global_values.dir_x[new_dir], player.y + global_values.dir_y[new_dir]):
                    new_cannon_tile = new_map[player.y + global_values.dir_y[new_dir]][player.x + global_values.dir_x[new_dir]]
                    # corner_tile = new_map[player.y + global_values.dir_y[new_dir] + global_values.dir_y[player.direction]][player.x + global_values.dir_x[new_dir] + global_values.dir_x[player.direction]]
                    if new_cannon_tile <= 0:
                        player.direction = new_dir
                    else:
                        if new_cannon_tile > 0:
                            visual_cache[player.y + global_values.dir_y[new_dir]][player.x + global_values.dir_x[new_dir]] = "⚪"

                        # if corner_tile > 0:
                        #     visual_cache[player.y + global_values.dir_y[new_dir] + global_values.dir_y[player.direction]][player.x + global_values.dir_x[new_dir] + global_values.dir_x[player.direction]] = "⚪"

            for player_id in self.order:
                if len(reactions[player_id]):
                    player = self.players[player_id]
                    if reactions[player_id][0] == 0:
                        try_and_change_direction(player, 1)
                    elif reactions[player_id][0] == 1:
                        try_and_change_direction(player, -1)

            # Dash
            def try_and_move(player, direction):
                if self.inside(player.x + global_values.dir_x[direction], player.y + global_values.dir_y[direction]) and self.inside(player.x + global_values.dir_x[direction] + global_values.dir_x[player.direction], player.y + global_values.dir_y[direction] + global_values.dir_y[player.direction]):
                    new_tile = new_map[player.y + global_values.dir_y[direction]][player.x + global_values.dir_x[direction]]
                    new_cannon_tile = new_map[player.y + global_values.dir_y[direction] + global_values.dir_y[player.direction]][player.x + global_values.dir_x[direction] + global_values.dir_x[player.direction]]
                    if new_tile == 0 and new_cannon_tile <= 0:
                        player.x += global_values.dir_x[direction]
                        player.y += global_values.dir_y[direction]
                    elif new_tile == -1:
                        dead.append(player.kill(self, "l'environnement"))

            for player_id in self.order:
                if len(reactions[player_id]):
                    player = self.players[player_id]
                    if reactions[player_id][0] == 4:
                        try_and_move(player, (player.direction + 1)%4)
                    elif reactions[player_id][0] == 5:
                        try_and_move(player, (player.direction - 1)%4)

            # Tir
            toKill = []
            def shoot(player):
                dx = global_values.dir_x[player.direction]
                dy = global_values.dir_y[player.direction]
                x = player.x + dx
                y = player.y + dy

                if player.ammo > 0:
                    player.ammo -= 1

                    while True:
                        for id in self.order:
                            p = self.players[id]
                            if p.x == x and p.y == y:
                                toKill.append((p, player))
                                visual_cache[y][x] = "💥"
                                return

                        if new_map[y][x] > 0:
                            visual_cache[y][x] = ""
                            visual_cache[y - dy][x - dx] = "💥"
                            break

                        if not self.inside(x + dx, y + dy):
                            break

                        x += dx
                        y += dy
                        visual_cache[y][x] = "◽"
                    else:
                        if self.inside(x, y):
                            visual_cache[y][x] = "💨"

            for player_id in self.order:
                if len(reactions[player_id]):
                    player = self.players[player_id]
                    if reactions[player_id][0] == 6:
                        shoot(player)

            for s in toKill:
                dead.append(s[0].kill(self, s[1]))

            #Déplacement
            for player_id in self.order:
                if len(reactions[player_id]):
                    player = self.players[player_id]
                    if reactions[player_id][0] == 2:
                        try_and_move(player, player.direction)
                    elif reactions[player_id][0] == 3:
                        try_and_move(player, (player.direction + 2)%4)

            # Pop
            for player_id in self.order:
                if len(reactions[player_id]):
                    reactions[player_id].pop(0)

            # Generation du plateau + cache
            def draw_tile(x, y):
                if len(visual_cache[y][x]):
                    row_strings[-1] += visual_cache[y][x]
                    return

                for i, player_id in enumerate(self.order):
                    player = self.players[player_id]
                    if player.x == x and player.y == y:
                        row_strings[-1] += global_values.player_colors[player.index]
                        return
                    elif player.x + global_values.dir_x[player.direction] == x and player.y + global_values.dir_y[player.direction] == y:
                        row_strings[-1] += global_values.direction_emojis[player.direction]
                        return

                row_strings[-1] += global_values.tile_colors[new_map[y][x] + 1]

            row_strings = []
            for y in range(len(self.map)):
                row_strings.append("")
                for x in range(len(self.map[y])):
                     draw_tile(x, y)

            map_string = '\n'.join(row_strings)

            embed = self.info_message.message.embeds[0]
            embed.description = map_string
            await self.info_message.message.edit(embed=embed)

            await asyncio.sleep(1)

        self.map = new_map
        return '\n'.join(dead)

    # Passe au prochain tour
    async def next_turn(self, message=None):
        self.round += 1

        for player in self.players.values():
            player.confirmed = False

        await self.send_info(info=message)

        alives = [i for i in range(len(self.order)) if len([0 for row in self.map for tile in row if tile == i])]

        if len(alives) == 1:
            await self.end_game(str(self.players[self.order[alives[0]]].user), "Survie")
            return

        if len(alives) == 0:
            await self.end_game("Personne", "Annihilation")
            return

        await self.info_message.reset()

        self.phase = "plan"

        # self.save()

    # Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, name, cause):
        embed = discord.Embed(title="[TANK] Victoire " + ("d'`" if name[:1] in "EAIOU" else "de `") + name + "` par " + cause  + " !", color=global_values.color)

        embed.description = "**Joueurs :**\n" + '\n'.join([(global_values.player_colors[x.index] if id in self.order else "💀") + " `" + str(x.user) + "`" for id, x in self.players.items()])

        if self.info_message:
            await self.info_message.delete()
            await self.info_message.message.clear_reactions()

        await self.channel.send(embed=embed)
        self.delete_save()
        del global_values.games[self.channel.id]

    def serialize(self):
        object = {
            "channel": self.channel.id,
            "order": self.order,
            "map": self.map,
            "last_choice": self.last_choice,
            "round": self.round,
            "players": {}
        }

        for id, player in self.players.items():
            object["players"][id] = {
                "user": player.user.id,
                "class": player.__class__.__name__.lower(),
                "power_active": player.power_active,
                "index": player.index,
                "variables": player.variables
            }

        return object

    async def deserialize(self, object, client):
        self.channel = client.get_channel(object["channel"])
        self.order = object["order"]
        self.round = int(object["round"])
        self.map = list(object["map"])
        self.last_choice = object["last_choice"]
        self.players = {}

        for id, info in object["players"].items():
            player = self.players[int(id)] = classes[info["class"]](client.get_user(info["user"]))
            player.power_active = info["power_active"]
            player.index = info["index"]
            player.variables = info["variables"]

    def save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
        else:
            object = {}

        object[self.channel.id] = self.serialize()
        self.mainclass.objects.save_object("games", object)

    def delete_save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
            if str(self.channel.id) in object:
                object.pop(str(self.channel.id))

            self.mainclass.objects.save_object("games", object)
        else:
            print("no save")

  # Module créé par Le Codex#9836
