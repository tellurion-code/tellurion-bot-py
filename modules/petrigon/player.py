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

    def set_power(self, power):
        self.power = power

    def move(self, direction):
        new_map = Map.copy(self.game.map)

        for hex, value in self.game.map.hexes():
            if value == self.index:
                moving_to = self.game.map.get(hex + direction)
                if moving_to == None or moving_to == 1:
                    continue

                if moving_to == 0:
                    new_map.set(hex + direction, self.index)
                    continue

                if moving_to != self.index:
                    new_map = self.fight(new_map, hex, direction)

        if new_map == self.game.map:
            return False
        
        for player in self.game.players.values():
            player.last_score_change = player.score(new_map) - player.score(self.game.map)

        self.game.map = new_map
        return True
    
    def fight(self, map, hex, direction):
        new_map = Map.copy(map)
        opponent = self.game.index_to_player(map.get(hex + direction))

        attack = self.get_power(map, hex, direction * -1)
        defense = opponent.get_power(map, hex + direction, direction)

        if attack >= defense:
            new_map.set(hex + direction, 0 if attack == defense else self.index)

        return new_map
    
    def get_power(self, map, hex, direction):
        power = 0
        while map.get(hex) == self.index:
            power += 1
            hex += direction

        return power
    
    def use_power(self):
        if not self.power:
            return False
        
        return True
    
    def forfeit(self):
        new_map = Map.copy(self.game.map)
        for hex, value in self.game.map.hexes():
            if value == self.index:
                new_map.set(hex, 0)

        self.game.map = new_map
    
    def info(self, no_change=False):
        score_change = ""
        if self.last_score_change and not no_change:
            score_change = f"({'+' if self.last_score_change > 0 else ''}{self.last_score_change})"

        return f"{constants.TILE_COLORS[self.index]} **{self}**: {self.score()} {score_change}"

    def __str__(self):
        return self.user.display_name