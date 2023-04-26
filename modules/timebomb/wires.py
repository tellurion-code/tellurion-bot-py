class Wire:
    name = ""
    icon = "❌"

    def __init__(self, game):
        self.game = game
        self.player = None
        self.hidden = True

    def __str__(self):
        return "❔" if self.hidden else self.icon
    
    @property
    def back(self):
        return self.icon

    async def cut(self, current):
        self.hidden = False
        return False


class GroundWire(Wire):
    name = "Neutre"
    icon = "🔗"

    async def cut(self, current):
        self.game.stack.append(f"{current} a coupé un fil chez {self.player}")
        return await super().cut(current)


class LiveWire(Wire):
    name = "Fil actif"
    icon = "⚡"

    async def cut(self, current):
        remaining = len(self.game.players) - sum(1 for wire in self.game.aside if wire.name == self.name) - 1
        self.game.stack.append(f"{current} a coupé un **fil actif** chez {self.player}." + f" Plus que **{remaining}** !" if remaining else "")
        return await super().cut(current)


class BombWire(Wire):
    name = "Bombe"
    icon = "🧨"

    async def cut(self, current):
        self.hidden = False
        self.game.stack.append(f"{current} a coupé un fil *de trop* chez {self.player}!")

        await self.game.end_game(False, {
            "name": f"💥 Mauvaise coupe",
            "value": self.game.stack_string
        }, "coupe de la bombe")

        return True
