"""Power class."""

import math

from modules.petrigon.hex import Hex
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
    
    def __repr__(self):
        return str(self)
    

class Attacker(Power):
    name = "Attaquant"
    icon = "🗡️"
    description = "A un bonus de +1 en attaque"

    def on_attack_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + 1

        return decorated


class Defender(Power):
    name = "Défenseur"
    icon = "🛡️"
    description = "A un bonus de +1 en défense"

    def on_defense_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + 1

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
        async def decorated(*args, **kwargs):
            if self.double_turn: 
                self.player.game.turn += len(self.player.game.players) - 1
                self.double_turn = False
            return await func(*args, **kwargs)

        return decorated


class Pacifist(Power):
    name = "Pacifiste"
    icon = "🕊️"
    description = "Ne peut pas être attaqué par les joueurs qu'il n'a pas attaqué"

    def __init__(self, player):
        super().__init__(player)
        self.war_with = []

    def on_attack_decorator(self, func):
        def decorated(opponent, *args, **kwargs):
            self.war_with.append(opponent.id)
            return func(opponent, *args, **kwargs)

        return decorated

    def on_defense_decorator(self, func):
        def decorated(opponent, *args, **kwargs):
            return func(opponent, *args, **kwargs) + (math.inf if opponent.id not in self.war_with else 0)

        return decorated


class General(Power):
    name = "Général"
    icon = "🚩"
    description = "Une fois par partie, peut doubler la force de ses unités pour deux tours"

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
        async def decorated(*args, **kwargs):
            if self.doubled_turns > 0: self.doubled_turns -= 1
            return await func(*args, **kwargs)

        return decorated

    def get_strength_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) * (2 if self.doubled_turns > 0 else 1)

        return decorated
    
    def info_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + (f" (🚩 {self.doubled_turns} tours)" if self.doubled_turns > 0 else "")
        
        return decorated


class Topologist(Power):
    name = "Topologiste"
    icon = "🍩"
    description = "Considère les bords du plateau comme adjacents"

    def __init__(self, player):
        super().__init__(player)
        n = self.player.game.map_size
        self.mirror_centers = [Hex(2*n + 1, -n).rotate(i) for i in range(6)]

    def wraparound_hex(self, map, hex):
        if not map.is_inside(hex):
            for center in self.mirror_centers:
                moved = hex - center
                if map.is_inside(moved): return moved

        return hex

    def move_tile_decorator(self, func):
        def decorated(map, hex, target, direction, *args, **kwargs):
            target = self.wraparound_hex(map, target)
            return func(map, hex, target, direction, *args, **kwargs)
        
        return decorated
    
    def get_strength_decorator(self, func):
        def decorated(map, hex, direction, *args, **kwargs):
            strength = 0
            while map.get(hex) == self.player.index:
                strength += 1
                hex = self.wraparound_hex(map, hex + direction)

            return strength

        return decorated


class Swarm(Power):
    name = "Essaim"
    icon = "🐝"
    description = "Commence avec trois unités en triangle"

    def place_decorator(self, func):
        def decorated(hex, rotation, *args, **kwargs):
            func(hex, rotation, *args, **kwargs)
            func(hex + Hex(0, -1), rotation, *args, **kwargs)
            func(hex + Hex(1, -1), rotation, *args, **kwargs)
            
        return decorated
