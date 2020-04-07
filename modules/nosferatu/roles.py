class Player:
    reaction_message = None

    def __init__(self):
        pass


class Renfield(Player):
    role = "Renfield"

    def __init__(self):
        super().__init__()

    async def game_start(self, games, index):
        pass


class Hunter(Player):
    role = "Hunter"

    def __init__(self):
        super().__init__()

    async def game_start(self, games, index):
        pass


class Vampire(Player):
    role = "Vampire"

    def __init__(self):
        super().__init__()

    async def game_start(self, games, index):
        pass
