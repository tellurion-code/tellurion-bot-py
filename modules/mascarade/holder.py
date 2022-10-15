"""Holder class."""


class Holder:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.role = None
        self.index_emoji = ""
        self.revealed = False

    def __str__(self):
        return str(self.role if self.revealed else f"{self.index_emoji} **{self.name}**")