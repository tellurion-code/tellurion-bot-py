"""Power class."""

from modules.petrigon.types import Announcement


class Power:
    name = "Sans Pouvoir"
    icon = "🚫"
    description = "Sans pouvoir spécial"

    activation_description = ""
    start_active = False

    def __init__(self, player):
        self.player = player
        self.active = self.start_active

    def setup(self):
        # Get all methods ending with "_decorator" and apply them to the player
        for method_name in (func for func in dir(self.__class__) if callable(getattr(self, func)) and func.endswith("_decorator")):
            player_method_name = method_name.rstrip("_decorator")
            player_method = getattr(self.player, player_method_name)
            setattr(self.player, player_method_name, getattr(self, method_name)(player_method))

    def use(self):
        self.player.game.announcements.append(Announcement(
            name=f"{self.icon} Pouvoir du {self.name}",
            value=self.activation_description
        ))
        return True

    def __str__(self):
        return f"{self.icon} {self.name}"
    

class Attacker(Power):
    name = "Attaquant"
    icon = "🗡️"
    description = "A un bonus de +1 en attaque"

    def on_attack_decorator(self, func):
        def decorator():
            return func() + 1

        return decorator


class Defender(Power):
    name = "Défenseur"
    icon = "🛡️"
    description = "A un bonus de +1 en défense"

    def on_defense_decorator(self, func):
        def decorator():
            return func() + 1

        return decorator


class Glitcher(Power):
    name = "Glitcheur"
    icon = "👾"
    description = "Une fois par partie, peut jouer deux tours d'affilée"

    activation_description = "Le Glitcheur va jouer deux tours d'affilée"
    start_active = True

    def __init__(self, player):
        super().__init__(player)
        self.double_turn = False

    def use(self):
        self.active = False
        self.double_turn = True
        return super().use()

    def end_turn_decorator(self, func):
        async def decorator(interaction):
            if self.double_turn: 
                self.player.game.turn += len(self.player.game.players) - 1
                self.double_turn = False
            await func(interaction)

        return decorator
