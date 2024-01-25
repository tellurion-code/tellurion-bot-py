"""Player class."""

class Player:
    def __init__(self, game, user=None):
        self.user = user
        self.game = game
        self.name = None

        self.alive = True
        self.dead_vote = True
        self.traveller = False

        self.has_nominated = False
        self.was_nominated = False

        self.thief_affected = False
        self.bureaucrat_affected = False

        # self.whispers = 0

    @property
    def display_name(self):
        return self.name or self.user.display_name

    @property
    def can_vote(self):
        return self.alive or self.dead_vote

    def __str__(self):
        return f"{'' if self.alive else ('💀 ' if self.dead_vote else '🚫💀 ')}{'🎒 ' if self.traveller else ''}{self.display_name}"

    def serialize(self):
        return {
            "user": self.user.id,
            "name": self.name,
            "alive": self.alive,
            "dead_vote": self.dead_vote,
            "traveller": self.traveller,
            "has_nominated": self.has_nominated,
            "was_nominated": self.was_nominated,
            "thief_affected": self.thief_affected,
            "bureaucrat_affected": self.bureaucrat_affected
        }
    
    async def parse(self, object, client):
        self.user = await self.game.channel.guild.fetch_member(object["user"])
        self.name = object.get("name", self.alive)
        self.alive = object.get("alive", self.alive)
        self.dead_vote = object.get("dead_vote", self.dead_vote)
        self.traveller = object.get("traveller", self.traveller)
        self.has_nominated = object.get("has_nominated", self.has_nominated)
        self.was_nominated = object.get("was_nominated", self.was_nominated)
        self.thief_affected = object.get("thief_affected", self.thief_affected)
        self.bureaucrat_affected = object.get("bureaucrat_affected", self.bureaucrat_affected)
        return self
