"""Game class."""

import discord
import math
import random

from modules.petrigon.map import Map
from modules.petrigon.player import Player
from modules.petrigon.bot import GameBot
from modules.petrigon.hex import AXIAL_DIRECTION_VECTORS, DIRECTIONS_TO_EMOJIS, Hex
from modules.petrigon.panels import FightPanel, JoinPanel, PowerPanel
from modules.petrigon.power import Attacker, Defender, General, Glitcher, Liquid, Pacifist, Power, Swarm, Topologist, Turtle
from modules.petrigon.bot import GameBot


class Game:
    def __init__(self, mainclass):
        self.mainclass = mainclass
        self.channel = None
        self.admin = None

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
    def domination_score(self):
        return int(math.ceil((self.map.hex_count - self.wall_count * 6 - 1)) * self.domination_fraction) if self.map else None
    
    @property
    def domination_fraction(self):
        return 1./2. if len(self.players) > 2 else 3./5.
    
    @property
    def current_player(self):
        return self.turn_to_player(self.turn)
    
    def index_to_player(self, index):
        for player in self.players.values():
            if player.index == index: return player
        
        return None

    def player_turn(self, player):
        return self.order.index(player.id)
    
    def next_valid_turn(self, turn):
        last_turn = turn
        while True:
            turn = (turn + 1) % len(self.players)
            if any(self.players[self.order[turn]].move(self.map, direction).valid for direction in AXIAL_DIRECTION_VECTORS) or turn == last_turn:
                return turn
            
    def turn_to_player(self, turn):
        return self.players[self.order[turn]]
    
    def next_player(self, player):
        return self.turn_to_player(self.next_valid_turn(self.player_turn(player)))

    async def on_creation(self, message):
        self.channel = message.channel
        self.admin = message.author.id
        self.panel = await JoinPanel(self).send(self.channel)

    def add_player(self, user):
        self.players[user.id] = Player(self, user)

    def add_bot(self, depth):
        id = min(min(self.players.keys(), default=0), 0) - 1
        self.players[id] = GameBot(self, id, depth=depth)

    async def prepare_game(self):
        self.order = [i for i in self.players.keys()]
        random.shuffle(self.order)

        # Change panel
        await self.panel.close()
        if self.powers_enabled:
            for player in self.players.values():
                if isinstance(player, GameBot):
                    player.set_powers((random.choice((Attacker, Defender, Swarm, Topologist, Liquid)),))

            self.panel = await PowerPanel(self).send(self.channel)
        else:
            # for player in self.players.values():
            #     player.set_power((Power,))  # No special ability
            
            await self.start()

    async def finish_power_selection(self, interaction):
        await interaction.response.defer()
        await self.panel.close()

        powers_priority = (
            Swarm,
            Glitcher,
            Turtle,
            Attacker,
            Defender,
            General,
            Pacifist,
            Topologist,
            Liquid,
        )
        for player in self.players.values():
            for power_class in powers_priority:
                if power := player.powers.get(power_class.__name__, None):
                    power.setup()

        await self.start()

    async def start(self):
        self.round = 1
        self.turn = 0
        self.setup_map()

        self.panel = await FightPanel(self).send(self.channel)
        await self.current_player.start_turn()

    def setup_map(self):
        self.map = Map(size=self.map_size)

        # Place players
        rotations = [
            [],
            [],
            [0, 3],
            [0, 2, 4],
            [0, 1, 3, 4],
            [0, 1, 5, 2, 4],    # We leave a gap between the last two players as last player advantage
            [0, 1, 2, 3, 4, 5]
        ]
        r = -int(math.ceil(self.map_size * 2./3.))
        q = random.randrange(0, -r)
        for i, id in enumerate(self.order):
            self.players[id].index = i+2
            self.players[id].place(Hex(q, r), rotations[len(self.players)][i])

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

    async def handle_direction(self, direction, interaction=None):
        result = self.current_player.move(self.map, direction)
        if not result.valid:
            return False

        for fight in result.fights:
            fight.attacker.on_fight(fight)
            fight.defender.on_fight(fight)

        for player in self.players.values():
            player.last_score_change = player.score(result.map) - player.score(self.map)

        self.map = result.map
        self.last_input = DIRECTIONS_TO_EMOJIS[direction]    
        await self.current_player.end_turn(interaction)
        return True

    async def next_turn(self, interaction):
        next_turn = self.next_valid_turn(self.turn)
        if next_turn <= self.turn: self.round += 1
        self.turn = next_turn

        winner, reason = self.check_game_over()
        if reason:
            await self.end_game(winner, reason, interaction)
        else:
            await self.current_player.start_turn(interaction)
        
    def check_game_over(self):
        potential_winner, max_score, alive_players = None, 0, 0
        for player in self.players.values():
            score = player.score()
            if score >= self.domination_score:
                return player, "Domination"

            if score > 0:
                alive_players += 1

            if score > max_score:
                potential_winner = player
                max_score = score
        
        if alive_players == 1:
            return potential_winner, "Annihilation"
        
        if alive_players == 0:
            return None, "Destruction Mutuelle"

        if self.round >= 30:
            return potential_winner, "Usure"

        return None, None

    async def end_game(self, winner, reason, interaction):
        embed = discord.Embed(title=f"Petrigon | Victoire de {winner if winner else 'personne'} par {reason}", color=self.mainclass.color)
        embed.description = '\n'.join(self.players[id].info(no_change=True) for id in self.order)
        await self.channel.send(embed=embed)
        await self.panel.update(interaction)
        await self.end()

    async def end(self):
        await self.panel.close()
        self.players.clear()
        del self.map
        del self.panel
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
