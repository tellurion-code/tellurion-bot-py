"""Dataclasses and enums."""

from copy import deepcopy
from dataclasses import dataclass
from PIL import Image

from modules.petrigon.map import Map
from modules.petrigon.zobrist import zobrist_hash


@dataclass
class Announcement:
    name: str
    value: str


@dataclass
class MapImage:
    image: Image
    url: str = None


@zobrist_hash(fields=('self__no_key',))
class PowersData(dict):
    def __init__(self, powers_data):
        for key, value in powers_data.items():
            self[key] = deepcopy(value)


@dataclass
@zobrist_hash
class Context:
    map: Map
    players_powers_data: dict[int, PowersData]

    def copy(self, *, same_map=False, players_powers_data_update={}):
        return Context(
            self.map if same_map else self.map.copy(),
            {k: players_powers_data_update.get(k, x) for k,x in self.players_powers_data.items()}
        )