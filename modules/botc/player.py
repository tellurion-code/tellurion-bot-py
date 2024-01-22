"""Player class."""

class Player:
    def __init__(self, game, user):
        self.user = user
        self.game = game
        self.name = None

        self.alive = True
        self.dead_vote = True
        self.traveller = False

        self.has_nominated = False
        self.was_nonimated = False

        # self.whispers = 0

    @property
    def display_name(self):
        return self.name or self.user.display_name

    def __str__(self):
        return f"{'' if self.alive else ('💀 ' if self.dead_vote else '🚫💀 ')}{'🎒 ' if self.traveller else ''}{self.display_name}"
