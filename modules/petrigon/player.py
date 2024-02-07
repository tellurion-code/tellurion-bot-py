"""Player class."""

from modules.petrigon import constants
from modules.petrigon.map import Map

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

    def place(self, hex, rotation):
        self.game.map.set(hex.rotate(rotation), self.index)

    def start_turn(self):
        pass

    def move(self, direction):
        with self.game.map.edit() as editor:
            for hex, _ in editor.map.hexes():
                editor.new_map.update(self.move_tile(editor.map, hex, hex + direction, direction), base_map=editor.map)

            if editor.new_map == editor.map:
                return False
            
            for player in self.game.players.values():
                player.last_score_change = player.score(editor.new_map) - player.score(editor.map)

        return True
    
    def move_tile(self, map, hex, target, direction):
        new_map = Map.copy(map)
        if map.get(hex) == self.index:
            moving_to = map.get(target)
            if moving_to == None or moving_to == 1:
                return new_map

            if moving_to == 0:
                new_map.set(target, self.index)
                return new_map

            if moving_to != self.index:
                new_map.update(self.fight(map, hex, target, direction), base_map=map)
                return new_map
        
        return new_map
    
    def fight(self, map, hex, target, direction):
        new_map = Map.copy(map)
        opponent = self.game.index_to_player(map.get(target))

        attack = self.get_strength(map, hex, direction * -1) + self.on_attack(opponent)
        defense = opponent.get_strength(map, target, direction) + opponent.on_defense(self)

        if attack >= defense:
            new_map.set(target, 0 if attack == defense else self.index)

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