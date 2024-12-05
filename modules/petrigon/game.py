"""Game class."""

import asyncio
import math
import random

from modules.petrigon.map import Map
from modules.petrigon.player import Player
from modules.petrigon.bot import GameBot
from modules.petrigon.hex import AXIAL_DIRECTION_VECTORS, DIRECTIONS_TO_EMOJIS, Hex
from modules.petrigon.panels import FightPanel, JoinPanel, PowerPanel
from modules.petrigon.power import ALL_POWERS, Attacker, Defender, General, Glitcher, Liquid, Pacifist, Scout, Swarm, Topologist, Turtle
from modules.petrigon.bot import GameBot
from modules.petrigon.types import Context, PowersData


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

        self.powers_enabled = True
        self.use_symmetry = False
        self.tournament = False
        self.map_size = 6
        self.wall_count = 6

        self.panel = None
        self.announcements = []
        self.last_input = None

    @property
    def domination_score(self):
        return int(math.ceil((self.map.hex_count - self.wall_count - 1)) * self.domination_fraction) if self.map else None
    
    @property
    def domination_fraction(self):
        return 1./2. if len(self.players) > 2 else 3./5.
    
    @property
    def current_player(self):
        return self.turn_to_player(self.turn)
    
    @property
    def current_context(self):
        return Context(self.map, {k: PowersData({x.key: x.data for x in p.powers.values()}) for k,p in self.players.items()})
    
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
            if turn == last_turn: return turn
            
            # TODO: Since we're calculating all that, might as well store it somewhere to have the turn go by faster
            current_player = self.players[self.order[turn]]
            for direction in AXIAL_DIRECTION_VECTORS:
                for combination in current_player.usable_powers_combinations():
                    context = current_player.use_powers_from_combination(self.current_context, combination)
                    if current_player.move(context, direction).valid: return turn

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

        for i, id in enumerate(self.order):
            self.players[id].index = i+2
            if self.tournament and (user := self.players[id].user):
                await user.send(f"Vous êtes le joueur {i+1}")

        # Change panel
        await self.panel.close()
        if self.powers_enabled:
            for player in self.players.values():
                if isinstance(player, GameBot):
                    player.set_powers((random.choice(ALL_POWERS),))

            self.panel = await PowerPanel(self).send(self.channel)
        else:
            # for player in self.players.values():
            #     player.set_power((Power,))  # No special ability
            
            await self.start()

    async def finish_power_selection(self, interaction):
        await interaction.response.defer()
        await self.panel.close()

        powers_priority = (  # Later is more important, earlier is more fundamental
            Topologist,
            Swarm,
            Glitcher,
            Turtle,
            Attacker,
            Defender,
            General,
            Pacifist,
            Liquid,
            Scout,
        )
        for player in self.players.values():
            for power_class in powers_priority:
                if power := player.powers.get(power_class.__name__):
                    power.setup()

        await self.start()

    async def start(self):
        self.round = 1
        self.turn = 0
        self.setup_map()

        self.panel = await FightPanel(self).send(self.channel)
        await self.start_turn()

    def setup_map(self):
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
        r = -int(math.ceil(self.map_size * 2./3.))
        q = random.randrange(0, -r)
        for i, id in enumerate(self.order):
            self.players[id].place(Hex(q, r), rotations[len(self.players)][i])

        # Place walls
        self.map.set(Hex(0, 0), 1)
        symmetries = (
            [0, 3] if len(self.players) == 2 else
            ([0, 2, 4] if len(self.players) == 3 else
            ([0, 3] if len(self.players) == 4 else  # FIXME: La symmétrie est pas bonne ici
            [0, 1, 2, 3, 4, 5]))
        ) if self.use_symmetry else [0]

        def validate_walls_placement(hexes):
            for hex in hexes:
                if self.map.get(hex) != 0:
                    return False

                for neighbor in hex.neighbors():
                    if self.map.get(neighbor) != 0:
                        return False

            return True    
        
        i = 0
        while i < self.wall_count:
            q = random.randrange(0, self.map.size)
            r = -random.randrange(q + 1, self.map_size + 1)
            hexes = [Hex(q, r).rotate(i).rotate(j) for j in symmetries]

            if not validate_walls_placement(hexes):
                continue

            for hex in hexes:
                self.map.set(hex, 1)
                i += 1

    async def start_turn(self, interaction=None):
        context = self.current_player.start_turn(self.current_context)
        self.current_player.apply_powers_data(context)
        await self.panel.update(interaction)
        self.announcements = []

        if isinstance(self.current_player, GameBot):
            asyncio.create_task(self.current_player.take_move())

    async def handle_direction(self, direction, interaction=None):
        result = self.current_player.move(self.current_context, direction)
        if not result.valid:
            return False
        pass_turn, context = self.current_player.end_turn(result)

        self.last_input = DIRECTIONS_TO_EMOJIS[direction]
        for player in self.players.values():
            player.last_score_change = player.score(context.map) - player.score(self.map)
        
        self.current_player.apply_powers_data(context)
        self.map = context.map

        await self.end_action(pass_turn, interaction)
        return True
    
    async def end_action(self, pass_turn, interaction):
        if pass_turn:
            await self.next_turn()
        else:
            await self.panel.update()

        if not await self.check_for_game_end(interaction):
            await self.start_turn(interaction)

    async def next_turn(self):
        next_turn = self.next_valid_turn(self.turn)
        if next_turn <= self.turn: self.round += 1
        self.turn = next_turn

    async def check_for_game_end(self, interaction):
        winner, reason = self.check_game_over()
        if reason:
            await self.end_game(winner, reason, interaction)
            return True
        
        return False
        
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
        await self.panel.end(winner, reason, interaction)
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
