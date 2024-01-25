"""Dataclasses and enums."""

from dataclasses import dataclass
from enum import Enum


@dataclass
class Gamerule:
    name: str
    state: bool


class Phases(Enum):
    start = "start"
    night = "night"
    day = "day"
    nominations = "nominations"


class VoteState(Enum):
    no_vote = 0
    unknown = 1  # Le joueur a voté, mais n'a pas déterminé son choix
    vote_for = 2
    vote_against = 3


@dataclass
class Vote:
    state: VoteState
    display: str

    with_thief: bool = False
    with_bureaucrat: bool = False

    @property
    def value(self):
        value = 1 if self.state == VoteState.vote_for else 0
        if self.with_thief: value *= -1
        if self.with_bureaucrat: value *= 3
        return value
    
    def to_dict(self):
        return {
            "state": self.state.value,
            "display": self.display,
            "thief": self.with_thief,
            "bureaucrat": self.with_bureaucrat
        }
    
    @classmethod
    def from_dict(cls, dict):
        return cls(VoteState(dict["state"]), dict["display"], dict["thief"], dict["bureaucrat"])
