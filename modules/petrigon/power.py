"""Power class."""

import math

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
            player_method_name = method_name.removesuffix("_decorator")
            player_method = getattr(self.player, player_method_name)
            decorator = getattr(self, method_name)
            setattr(self.player, player_method_name, decorator(player_method))

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
        def decorated(opponent):
            return func(opponent) + 1

        return decorated


class Defender(Power):
    name = "Défenseur"
    icon = "🛡️"
    description = "A un bonus de +1 en défense"

    def on_defense_decorator(self, func):
        def decorated(opponent):
            return func(opponent) + 1

        return decorated


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
        async def decorated(interaction):
            if self.double_turn: 
                self.player.game.turn += len(self.player.game.players) - 1
                self.double_turn = False
            await func(interaction)

        return decorated


class Pacifist(Power):
    name = "Pacifiste"
    icon = "🕊️"
    description = "Ne peut pas être attaqué par les joueurs qu'il n'a pas attaqué"

    def __init__(self, player):
        super().__init__(player)
        self.war_with = []

    def on_attack_decorator(self, func):
        def decorated(opponent):
            self.war_with.append(opponent.user.id)
            return func(opponent)

        return decorated

    def on_defense_decorator(self, func):
        def decorated(opponent):
            return func(opponent) + (math.inf if opponent.user.id not in self.war_with else 0)

        return decorated


class General(Power):
    name = "Général"
    icon = "🚩"
    description = "Une fois par partie, peut doubler la force de ses unités pour 2 tours"

    activation_description = "Les unités du Général vont être doublées pour 2 tours"
    start_active = True

    def __init__(self, player):
        super().__init__(player)
        self.doubled_turns = 0

    def use(self):
        self.doubled_turns = 2
        self.active = False
        return super().use()

    def start_turn_decorator(self, func):
        def decorated():
            if self.doubled_turns > 0: self.doubled_turns -= 1
            func()

        return decorated

    def get_strength_decorator(self, func):
        def decorated(*args):
            return func(*args) * (2 if self.doubled_turns > 0 else 1)

        return decorated
    
    def info_decorator(self, func):
        def decorated():
            return func() + (f" (🚩 {self.doubled_turns} tours)" if self.doubled_turns > 0 else "")
        
        return decorated
