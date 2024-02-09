"""Player class."""

from dataclasses import dataclass, field

from modules.petrigon import constants
from modules.petrigon.map import Map
from modules.petrigon.hex import Hex
from modules.petrigon.panels import PowerActivationPanel


class Player:
    def __init__(self, game, user=None):
        self.game = game
        self.user = user
        self.id = user.id if user else 0

        self.index = None
        self.powers = {}

        self.last_score_change = 0

    def score(self, map=None):
        if not map: map = self.game.map
        return sum(1 for _, x in map.items() if x == self.index)

    def set_powers(self, power_classes):
        self.powers.clear()
        self.powers = {c.__name__: c(self) for c in power_classes}

    def place(self, hex, rotation):
        self.game.map.set(hex.rotate(rotation), self.index)

    async def start_turn(self, interaction=None):
        await self.game.panel.update(interaction)
        self.game.announcements = []

    def move(self, map, direction):
        result = MoveResult(Map.copy(map))
        for hex in map.hexes():
            new_map, fight = self.move_tile(map, hex, hex + direction, direction)
            if new_map: result.map.update(new_map, base_map=map)
            if fight: result.fights.append(fight)

        result.valid = result.map != map
        return result

    def get_hex(self, map, hex):
        return map.get(hex)
    
    def move_tile(self, map, hex, target, direction):
        if self.get_hex(map, hex) == self.index:
            moving_to = self.get_hex(map, target)
            if moving_to in (None, 1, self.index):
                return None, None
            
            if moving_to not in (0, self.index):
                fight = self.fight(map, hex, target, direction)
                new_map = fight.resolve(map)
                return new_map, fight

            new_map = Map.copy(map)
            new_map.set(target, self.index)
            return new_map, None
        
        return None, None
    
    def fight(self, map, hex, target, direction):
        opponent = self.game.index_to_player(self.get_hex(map, target))

        attack = self.get_strength(map, hex, direction * -1, opponent=opponent, attacking=True)
        defense = opponent.get_strength(map, target, direction, opponent=self, attacking=False)

        return Fight(self, opponent, attack, defense, target)
    
    def get_strength(self, map, hex, direction, opponent, attacking):
        strength = 0
        while self.get_hex(map, hex) == self.index:
            strength += 1
            hex += direction

        return strength
    
    def on_fight(self, fight):
        pass
    
    async def use_power(self, interaction):
        powers = {i: x for i,x in self.powers.items() if x.active}
        await PowerActivationPanel(self.game, powers).reply(interaction)
    
    async def end_turn(self, interaction):
        await self.game.next_turn(interaction)
    
    async def forfeit(self, interaction):
        with self.game.map.edit() as editor:
            for hex, value in editor.map.items():
                if value == self.index:
                    editor.new_map.clear(hex)

        if self == self.game.current_player:
            await self.game.next_turn(interaction)
        else:
            await self.game.check_for_game_end(interaction)
    
    def info(self, no_change=False):
        score_change = f"**({'+' if self.last_score_change > 0 else ''}{self.last_score_change})**" if self.last_score_change and not no_change else ""
        return f"{constants.TILE_COLORS[self.index]}{''.join(power.icon for power in self.powers.values())} **{self}**: {self.score()} {score_change}"

    def __str__(self):
        return f"`{self.user.display_name}`"


@dataclass
class Fight:
    attacker: Player
    defender: Player
    attack: int
    defense: int
    hex: Hex

    def resolve(self, map: Map):
        if self.attack >= self.defense:
            new_map = Map.copy(map)
            new_map.set(self.hex, 0 if self.attack == self.defense else self.attacker.index)
            return new_map
    
        return map


@dataclass
class MoveResult:
    map: Map
    fights: list[Fight] = field(default_factory=list)
    valid: bool = True