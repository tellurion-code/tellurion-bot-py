"""Player class."""

from copy import deepcopy
import itertools
import random
from dataclasses import dataclass, field

from modules.petrigon import constants
from modules.petrigon.map import Map
from modules.petrigon.hex import Hex
from modules.petrigon.panels import PowerActivationPanel
from modules.petrigon.types import Context


class Player:
    def __init__(self, game, user=None):
        self.game = game
        self.user = user
        self.id = user.id if user else 0

        self.index = None
        self.hash = random.getrandbits(64)
        self.powers = {}

        self.last_score_change = 0

    def powers_data_from_context(self, context):
        return context.players_powers_data[self.id]
    
    def usable_powers_combinations(self, context=None):
        if context is None: context = self.game.current_context
        max_power_uses = {}
        for key in self.powers.keys():
            max_uses = 0
            power_context = context.copy()
            while self.powers[key].data_from_context(power_context).active:  # We assume the powers are activated independently
                power_context = self.powers[key].use(power_context)
                max_uses += 1
            
            max_power_uses[key] = tuple(range(max_uses + 1))

        return tuple(dict(zip(max_power_uses.keys(), x)) for x in tuple(itertools.product(*max_power_uses.values())))

    def use_powers_from_combination(self, context, combination, *, with_announcements=False):
        for key, amount in combination.items():
            for _ in range(amount):
                context = self.powers[key].use(context)
                if with_announcements: self.powers[key].send_announcement()
                if context is None: return None
        
        return context

    def score(self, map=None):
        if not map: map = self.game.map
        return sum(1 for _, x in map.items() if x == self.index)

    def set_powers(self, power_classes):
        self.powers.clear()
        power_instances = [c(self) for c in power_classes]
        self.powers = {p.key: p for p in power_instances}

    def place(self, hex, rotation):
        self.game.map.set(hex.rotate(rotation), self.index)

    def start_turn(self, context):
        return context

    def move(self, context, direction):
        return self.do_move(context, direction)

    def do_move(self, context, direction):
        new_context = context.copy()
        result = MoveResult(new_context)
        for hex in context.map.hexes():
            move_context, fight = self.move_tile(context, hex, hex + direction, direction)
            if move_context:
                new_context.map.update(move_context.map, base_map=context.map)
                new_context.players_powers_data.update(move_context.players_powers_data)
            if fight: result.fights.append(fight)

        result.valid = hash(new_context) != hash(context)
        return result
    
    def displace(self, context, direction, *, ties_consume_units=False):
        first_result = self.do_move(context, direction)
        if not first_result.valid: return first_result
        
        new_map = first_result.context.map.copy()
        for hex, value in first_result.context.map.items():
            if value == self.index and self.get_hex(first_result.context, hex - direction) != self.index:
                wall_check_hex = hex + direction
                while self.get_hex(context, wall_check_hex) == self.index:
                    wall_check_hex += direction

                if not ( # Don't remove the unit if:
                    # We moved against a wall or edge, or
                    self.get_hex(context, wall_check_hex) in (None, 1) or
                    # We lost a fight (or it's a tie and should not consume a unit)
                    any(
                        x.hex == wall_check_hex and (
                            self.get_hex(first_result.context, x.hex) == x.defender.index or
                            self.get_hex(first_result.context, x.hex) == 0 and not ties_consume_units
                        )
                        for x in first_result.fights
                    )                               
                ):
                    new_map.clear(hex)

        new_context = Context(new_map, first_result.context.players_powers_data)
        second_result = MoveResult(
            new_context,
            fights=first_result.fights,
            valid=hash(new_context) != hash(context)
        )
        return second_result

    def get_hex(self, context, hex):
        return context.map.get(hex)
    
    def move_tile(self, context, hex, target, direction):
        if self.get_hex(context, hex) == self.index:
            moving_to = self.get_hex(context, target)
            if moving_to in (None, 1, self.index):
                return None, None
            
            if moving_to not in (0, self.index):
                return self.fight(context, hex, target, direction)

            new_map = context.map.copy()
            new_map.set(target, self.index)
            return Context(new_map, context.players_powers_data), None
        
        return None, None
    
    def fight(self, context, hex, target, direction):
        opponent = self.game.index_to_player(self.get_hex(context, target))

        attack = self.get_strength(context, hex, direction * -1, opponent=opponent, attacking=True)
        defense = opponent.get_strength(context, target, direction, opponent=self, attacking=False)

        fight = Fight(self, opponent, attack, defense, target)
        new_context = context.copy()
        new_context.map = fight.resolve(new_context.map)
        return new_context, fight
    
    def get_strength(self, context, hex, direction, *, opponent, attacking):
        strength = 0
        while self.get_hex(context, hex) == self.index:
            strength += 1
            hex += direction

        return strength
    
    def apply_powers_data(self, context):
        for key, data in self.powers_data_from_context(context).items():
            self.powers[key].data = data
    
    async def use_power(self, interaction):
        powers = {i: x for i,x in self.powers.items() if x.data.active}
        await PowerActivationPanel(self.game, powers).reply(interaction)

    def is_on_extra_turn(self, context):
        new_powers_data = deepcopy(self.powers_data_from_context(context))
        extra_turn = False
        for key, data in self.powers_data_from_context(context).items():
            if data.extra_turn:
                new_powers_data[key].extra_turn = False
                extra_turn = True
                break

        return extra_turn, context.copy(same_map=True, players_powers_data_update={self.id: new_powers_data})
    
    def end_turn(self, result):
        extra_turn, new_context = self.is_on_extra_turn(result.context)
        if extra_turn: return False, new_context
        return True, new_context
    
    async def forfeit(self, interaction):
        with self.game.map.edit() as editor:
            for hex, value in editor.map.items():
                if value == self.index:
                    editor.new_map.clear(hex)

        await self.game.end_action(self == self.game.current_player, interaction)

    def base_info(self, show_name=False):
        return f"{constants.TILE_EMOJIS[self.index]}{''.join(power.icon for power in self.powers.values())} **{self.player_name(show_name)}**: {self.score()}"
    
    def info(self):
        score_change = f" **({'+' if self.last_score_change > 0 else ''}{self.last_score_change})**" if self.last_score_change != 0 else ""
        return f"{self.base_info()}{score_change}"

    def player_name(self, show_name=False):
        return f"`{self.user.display_name}`" if show_name or not self.game.tournament else f"`Joueur {self.index - 1}`"

    def __hash__(self):
        return self.hash


@dataclass
class Fight:
    attacker: Player
    defender: Player
    attack: int
    defense: int
    hex: Hex

    def resolve(self, map: Map):
        if self.attack >= self.defense:
            new_map = map.copy()
            new_map.set(self.hex, 0 if self.attack == self.defense else self.attacker.index)
            return new_map
    
        return map


@dataclass
class MoveResult:
    context: Context
    fights: list[Fight] = field(default_factory=list)
    valid: bool = True
