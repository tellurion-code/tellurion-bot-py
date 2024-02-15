"""Dataclasses and enums."""

from dataclasses import dataclass, replace
from PIL import Image

from modules.petrigon.map import Map


@dataclass
class Announcement:
    name: str
    value: str


@dataclass
class MapImage:
    image: Image
    url: str = None


class PowersData(dict):
    def __init__(self, powers_data):
        for key, value in powers_data.items():
            self[key] = replace(value)
    
    def __hash__(self):
        return 0


@dataclass
class Context:
    map: Map
    powers_data: PowersData

    def copy(self):
        return Context(self.map.copy(), PowersData(self.powers_data))