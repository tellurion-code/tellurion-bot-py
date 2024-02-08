"""Map class."""

import random

from modules.petrigon import constants
from modules.petrigon.hex import Hex


class Map:
    """A hash map representing a hexagonal-shaped hex map."""
    class MapEditor:
        """An editor that allows reading a map and automatically updating it only once exited."""
        def __init__(self, map):
            self.map = map
            self.new_map = None

        def __enter__(self):
            self.new_map = Map.copy(self.map)
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            if exc_type == None and self.new_map:
                self.map.hash_map = self.new_map.hash_map


    class ZobristHash:
        hash_tables = {}

        def __init__(self, size):
            if size in self.hash_tables: 
                self.zobrist_hash = self.hash_tables[size]
                return

            self.zobrist_hash = self.hash_tables[size] = {}
            for r in range(-size, size+1):
                hex = Hex(max(0, -r) - size, r)

                while hex.length <= size:
                    self.zobrist_hash[hex] = {i+1: random.getrandbits(64) for i in range(7)}
                    hex += Hex(1, 0)

        def hash(self, map):
            hash = 0
            for hex, value in map.items():
                hash ^= self.zobrist_hash[hex][value]

            return hash
    

    def __init__(self, size):
        self.size = size                            # This is a hexagonal shaped hex grid, so this is the number of hexes from the center (size of 1 = "3x3")
        self.hash_map = {}                          # Dict<Hex, int>. Non-existence means the tile is empty. For simplicity, coordinates are gonna be based around the center
        self.zobrist_hash = Map.ZobristHash(size)   # Hashing handler

    @classmethod
    def copy(cls, other):
        map = cls(other.size)
        map.hash_map = other.hash_map.copy()
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
        
        if hex not in self.hash_map:
            return 0
        
        return self.hash_map[hex]
    
    def set(self, hex, value):
        if not self.is_inside(hex):
            return

        if value == None:
            raise ValueError(f"{value} is not a valid value to set a hex")

        if value == 0:
            return self.clear(hex)

        self.hash_map[hex] = value

    def clear(self, hex):
        if not self.is_inside(hex):
            return

        if hex not in self.hash_map:
            return
        
        del self.hash_map[hex]

    def items(self):
        return self.hash_map.items()
    
    def hexes(self):
        return self.hash_map.keys()
    
    def edit(self):
        return Map.MapEditor(self)
    
    def update(self, other, base_map=None):
        """Apply all the differences between other and base_map (default: self) to the Map."""
        if base_map == None: base_map = self
        if other == base_map: return

        hexes = set((*base_map.hexes(), *other.hexes()))
        for hex in hexes:
            value = other.get(hex)
            if value != base_map.get(hex): self.set(hex, value)
    
    def __eq__(self, other):
        if not isinstance(other, Map):
            return False
        
        if len(self.hash_map) != len(other.hash_map):
            return False
        
        if any(other.get(hex) != value for hex, value in self.hash_map.items()):
            return False
            
        return True
    
    def __ne__(self, other):
        return not self == other

    def __str__(self):
        string = ""
        for y in range(-self.size, self.size + 1):
            if y&1 == 1: string += "⠀"
            
            for x in range(-self.size, self.size + 1):
                q = int(x - (y - (y&1)) / 2)
                r = y
                value = self.get(Hex(q, r))
                string += constants.TILE_COLORS[-1] if value == None else constants.TILE_COLORS[value]
        
            string = string.rstrip(constants.TILE_COLORS[-1]) + "\n"

        return string
    
    def __repr__(self):
        lines = []
        empty_count = 0
        for r in range(-self.size, self.size+1):
            hex = Hex(max(0, -r) - self.size, r)
            line = ""

            while self.is_inside(hex):
                value = self.get(hex)
                hex += Hex(1, 0)
                if value == 0:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        line += str(empty_count)
                        empty_count = 0
                    
                    line += "X" if value == 1 else chr(63 + value)

            if empty_count > 0:
                line += str(empty_count)
                empty_count = 0
            lines.append(line)

        return f"Map({'/'.join(lines)})"

    def __hash__(self):
        return self.zobrist_hash.hash(self)
