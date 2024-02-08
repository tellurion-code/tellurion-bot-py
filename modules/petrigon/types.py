"""Dataclasses and enums."""

from dataclasses import dataclass


@dataclass
class Announcement:
    name: str
    value: str

    