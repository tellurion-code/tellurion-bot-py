"""Player class."""

from modules.petrigon import constants
from modules.petrigon.map import Map
from modules.petrigon.hex import Hex


class Player:
    def __init__(self, game, user=None):
        self.game = game
        self.user = user

        self.index = None
        self.power = None

        self.last_score_change = 0

    def score(self, map=None):
        if not map: map = self.game.map
        return sum(1 for _, x in map.hexes() if x == self.index)

    def set_power(self, power_class):
        self.power = power_class(self)

    def place(self, q, r, rotation):
        hex = Hex(q, r).rotate(rotation)
        self.game.map.set(hex, self.index)

    def start_turn(self):
        pass

    def move(self, direction):
        with self.game.map.edit() as editor:
            for hex, value in editor.map.hexes():
                if value == self.index:
                    moving_to = editor.map.get(hex + direction)
                    if moving_to == None or moving_to == 1:
                        continue

                    if moving_to == 0:
                        editor.new_map.set(hex + direction, self.index)
                        continue

                    if moving_to != self.index:
                        editor.new_map = self.fight(editor.new_map, hex, direction)

            if editor.new_map == editor.map:
                return False
            
            for player in self.game.players.values():
                player.last_score_change = player.score(editor.new_map) - player.score(editor.map)

        return True
    
    def fight(self, map, hex, direction):
        new_map = Map.copy(map)
        opponent = self.game.index_to_player(map.get(hex + direction))

        attack = self.get_strength(map, hex, direction * -1) + self.on_attack(opponent)
        defense = opponent.get_strength(map, hex + direction, direction) + opponent.on_defense(self)

        if attack >= defense:
            new_map.set(hex + direction, 0 if attack == defense else self.index)

        return new_map
    
    def on_attack(self, opponent):
        return 0
    
    def on_defense(self, opponent):
        return 0
    
    def get_strength(self, map, hex, direction):
        strength = 0
        while map.get(hex) == self.index:
            strength += 1
            hex += direction

        return strength
    
    def use_power(self):
        if not self.power:
            return False
        
        return self.power.use()
    
    async def end_turn(self, interaction):
        await self.game.next_turn(interaction)
    
    def forfeit(self):
        with self.game.map.edit() as editor:
            for hex, value in editor.map.hexes():
                if value == self.index:
                    editor.new_map.set(hex, 0)
    
    def info(self, no_change=False):
        score_change = f"**({'+' if self.last_score_change > 0 else ''}{self.last_score_change})**" if self.last_score_change and not no_change else ""
        return f"{constants.TILE_COLORS[self.index]}{self.power.icon if self.power else ''} **{self}**: {self.score()} {score_change}"

    def __str__(self):
        return self.user.display_name