"""Dataclasses and enums."""

from dataclasses import dataclass
from PIL import Image


@dataclass
class Announcement:
    name: str
    value: str


@dataclass
class MapImage:
    image: Image
    url: str = None
