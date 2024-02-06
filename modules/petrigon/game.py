"""Game class."""

import discord
import math
import random

from modules.petrigon.map import Map
from modules.petrigon.hex import Hex
from modules.petrigon.power import Power
from modules.petrigon.panels import FightPanel, JoinPanel, PowerPanel


class Game:
    def __init__(self, mainclass):
        self.mainclass = mainclass
        self.channel = None

        self.map = None
        self.players = {}
        self.order = []
        self.turn = -1
        self.round = 0

        self.powers_enabled = False
        self.map_size = 6
        self.wall_count = 1

        self.panel = None
        self.announcements = []
        self.last_input = None

    @property
    def current_player(self):
        return self.players[self.order[self.turn]]
    
    @property
    def domination_score(self):
        return int(math.ceil(self.map.hex_count / 2.)) if self.map else None
    
    def index_to_player(self, index):
        for player in self.players.values():
            if player.index == index: return player
        
        return None

    async def on_creation(self, message):
        self.channel = message.channel
        self.panel = await JoinPanel(self).send(self.channel)

    async def start(self):
        self.order = [i for i in self.players.keys()]
        random.shuffle(self.order)

        self.map = Map(size=self.map_size)

        # Place players
        rotations = [
            [],
            [],
            [0, 3],
            [0, 2, 4],
            [0, 1, 3, 4],
            [0, 1, 2, 3, 5],    # We leave a gap between the last two players as last player advantage
            [0, 1, 2, 3, 4, 5]
        ]
        r = -int(math.ceil(self.map_size/2.))
        q = random.randrange(0, -r)
        for i, id in enumerate(self.order):
            self.players[id].index = i+2
            self.players[id].place(q, r, rotations[len(self.players)][i])

        # Place walls
        self.map.set(Hex(0, 0), 1)

        def validate_wall_placement(hex):
            if self.map.get(hex) != 0:
                return False

            for neighbor in hex.neighbors():
                if self.map.get(neighbor) != 0:
                    return False

            return True    
        
        for i in range(6):
            remaining_walls_to_place = self.wall_count
            while remaining_walls_to_place > 0:
                q = random.randrange(0, self.map.size)
                r = -random.randrange(q + 1, self.map_size + 1)
                hex = Hex(q, r).rotate(i)

                if not validate_wall_placement(hex):
                    continue

                self.map.set(hex, 1)
                remaining_walls_to_place -= 1

        # Change panel
        await self.panel.close()
        if self.powers_enabled:
            self.panel = await PowerPanel(self).send(self.channel)
        else:
            for player in self.players.values():
                player.set_power(Power)  # No special ability
            
            self.panel = await FightPanel(self).send(self.channel)

    async def finish_power_selection(self, interaction):
        await interaction.response.defer()
        await self.panel.close()

        for player in self.players.values():
            player.power.setup()

        self.panel = await FightPanel(self).send(self.channel)

    async def next_turn(self, interaction):
        last_turn = self.turn
        while True:
            self.turn = (self.turn + 1) % len(self.players)
            if self.turn == 0: self.round += 1
            if self.current_player.score() > 0 or self.turn == last_turn:
                break

        self.current_player.start_turn()
        await self.check_for_game_end(interaction)
        self.announcements = []

    async def check_for_game_end(self, interaction):
        potential_winner, max_score, alive_players = None, 0, 0
        for player in self.players.values():
            if player.score() >= self.domination_score:
                await self.end_game(player, "Domination")
                alive_players = -1
                break

            if player.score() > 0:
                alive_players += 1

            if player.score() > max_score:
                potential_winner = player
                max_score = max_score
        
        if alive_players == 1:
            await self.end_game(potential_winner, "Annihilation")
        
        if alive_players == 0:
            await self.end_game(None, "Destruction Mutuelle")

        if self.round >= 40:
            await self.end_game(potential_winner, "Usure")

        await self.panel.update(interaction)

    async def end_game(self, winner, reason):
        embed = discord.Embed(title=f"Petrigon | Victoire de {winner if winner else 'personne'} par {reason}", color=self.mainclass.color)
        embed.description = '\n'.join(self.players[id].info(no_change=True) for id in self.order)
        await self.channel.send(embed=embed)
        await self.end()

    async def end(self):
        await self.panel.close()
        del self.mainclass.games[self.channel.id]
        # self.delete_save()

    def save(self):
        pass

    def serialize(self):
        pass

    async def parse(self, client):
        return self
    
    def delete_save(self):
        pass