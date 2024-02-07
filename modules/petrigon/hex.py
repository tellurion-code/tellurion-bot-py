"""Hex math."""

class Hex:
    """A hex in axial/cube coordinates. Basically a vector in hex coordinates."""
    def __init__(self, q: int, r: int, s: int = None):
        self.q = q
        self.r = r
        self.s = s or -q-r

        if self.s != -q-r:
            raise ValueError(f"s must be equal to -q-r, but {self.s} is not equal to {-q-r}")
        
    @property
    def length(self):
        return max(abs(self.q), abs(self.s), abs(self.r))

    def neighbors(self):
        for direction in AXIAL_DIRECTION_VECTORS:
            yield self + direction

    def distance_to(self, other):
        return (self - other).length
    
    def rotate(self, amount=1):
        hex = Hex(self.q, self.r)
        for _ in range(amount % 6):
            hex = Hex(-hex.r, -hex.s, -hex.q)

        return hex

    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r)
    
    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r)
    
    def __mul__(self, other):
        return Hex(self.q * other, self.r * other)
    
    def __hash__(self):
        # TODO: Implement spiral coordinates as a hash to avoid collisions
        return self.q * 13 + self.r * 17
    
    def __eq__(self, other):
        return isinstance(other, Hex) and self.__hash__() == other.__hash__()
    
    def __ne__(self, other):
        return not self == other
    
    def __repr__(self):
        return f"Hex({self.q}, {self.r}, {self.s})"


AXIAL_DIRECTION_VECTORS = [
    Hex(+1, 0), Hex(+1, -1), Hex(0, -1), 
    Hex(-1, 0), Hex(-1, +1), Hex(0, +1), 
]