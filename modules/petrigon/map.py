"""Map class."""

from modules.petrigon import constants
from modules.petrigon.hex import Hex


class Map:
    """A hash map representing a hexagonal-shaped hex map."""
    def __init__(self, size):
        self.size = size    # This is a hexagonal shaped hex grid, so this is the number of hexes from the center (size of 1 = "3x3")
        self.hash = {}      # Dict<Hex, int>. Non-existence means the tile is empty. For simplicity, coordinates are gonna be based around the center

    @classmethod
    def copy(cls, other):
        map = cls(other.size)
        map.hash = {i: x for i, x in other.hash.items()}
        return map

    @property
    def hex_count(self):
        return self.size * (self.size + 1) * 3 + 1

    def is_inside(self, hex):
        return hex.length <= self.size
    
    def get(self, hex):
        """Returns None if out of the map, 0 if empty, and the value ther otherwise."""
        if not self.is_inside(hex):
            return None
        
        if hex not in self.hash:
            return 0
        
        return self.hash[hex]
    
    def set(self, hex, value):
        if not self.is_inside(hex):
            return
        
        if value == 0:
            return self.clear(hex)
        
        self.hash[hex] = value

    def clear(self, hex):
        if not self.is_inside(hex):
            return

        if hex not in self.hash:
            return
        
        del self.hash[hex]

    def hexes(self):
        return self.hash.items()
    
    def __eq__(self, other):
        if not isinstance(other, Map):
            return False
        
        if len(self.hash) != len(other.hash):
            return False
        
        for hex, value in self.hash.items():
            if other.get(hex) != value:
                return False
            
        return True
    
    def __ne__(self, other):
        return not self == other

    def __str__(self):
        string = ""
        for y in range(-self.size, self.size + 1):
            if y&1 == 0: string += "  "
            
            for x in range(-self.size, self.size + 1):
                q = int(x - (y + (y&1)) / 2)
                r = y
                value = self.get(Hex(q, r))
                string += constants.TILE_COLORS[-1] if value == None else constants.TILE_COLORS[value]
            
            if y&1 == 1: string += constants.TILE_COLORS[-1]
            string += "\n"

        return string
