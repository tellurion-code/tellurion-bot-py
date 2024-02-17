"""Power class."""

import math
from dataclasses import dataclass, field, replace

from modules.petrigon.hex import Hex
from modules.petrigon.types import Context, PowersData
from modules.petrigon.zobrist import zobrist_hash


class Power:
    @dataclass
    @zobrist_hash
    class Data:
        active: bool = False
        extra_turn: bool = False

    
    class ContextPowerDataEditor:
        def __init__(self, power, context, **kwargs) -> None:
            self.power = power
            self.context = context
            self.kwargs = kwargs
            self.data = replace(power.data_from_context(context))
        
        @property
        def new_context(self):
            return self.power.copy_context_with_data(self.context, self.data, **self.kwargs)
    

    name = "Sans Pouvoir"
    icon = "🚫"
    description = "Sans pouvoir spécial"

    activation_description = ""

    def __init__(self, player):
        self.player = player
        self.data = self.Data()

    @property
    def key(self):
        return self.__class__.__name__

    def setup(self):
        # Get all methods ending with "_decorator" and apply them to the player
        for method_name in (func for func in dir(self.__class__) if callable(getattr(self, func)) and func.endswith("_decorator")):
            player_method_name = method_name.removesuffix("_decorator")
            if not hasattr(self.player, player_method_name): continue

            player_method = getattr(self.player, player_method_name)
            decorator = getattr(self, method_name)
            setattr(self.player, player_method_name, decorator(player_method))

    def data_from_context(self, context):
        return self.player.powers_data_from_context(context)[self.key]
    
    def copy_context_with_data(self, context, data, *, same_map=True):
        powers_data = PowersData(self.player.powers_data_from_context(context))
        powers_data[self.key] = data
        return context.copy(same_map=same_map, players_powers_data_update={self.player.id: powers_data})

    def use(self, context):
        if not self.data_from_context(context).active: return None
        return context

    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def __repr__(self):
        return str(self)
    

class Attacker(Power):
    name = "Attaquant"
    icon = "🗡️"
    description = "A un bonus de +1 en attaque"

    def get_strength_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + (1 if kwargs.get("attacking", False) else 0)

        return decorated


class Defender(Power):
    name = "Défenseur"
    icon = "🛡️"
    description = "A un bonus de +1 en défense"

    def get_strength_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + (1 if not kwargs.get("attacking", False) else 0)

        return decorated


class Pacifist(Power):
    @dataclass
    class Data(Power.Data):
        war_with: set = field(default_factory=set)

    name = "Pacifiste"
    icon = "🕊️"
    description = "Ne peut pas être attaqué par les joueurs qu'il n'a pas attaqué"

    def fight_decorator(self, func):
        def decorated(context, hex, target, *args, **kwargs):
            editor = Power.ContextPowerDataEditor(self, context)
            opponent = self.player.game.index_to_player(self.get_hex(context, target))
            editor.data.war_with.add(opponent.id)
            
            return func(editor.new_context, hex, target, *args, **kwargs)

        return decorated

    def get_strength_decorator(self, func):
        def decorated(context, *args, **kwargs):
            opponent = kwargs.get("opponent", None)
            attacking = kwargs.get("attacking", False)

            return (
                math.inf 
                if opponent.id not in self.data_from_context(context).war_with and not attacking 
                else func(*args, **kwargs)
            )

        return decorated


class Topologist(Power):
    name = "Topologiste"
    icon = "🍩"
    description = "Peut traverser les bords, et gagne +1 en combat quand il le fait"

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

    def get_hex_decorator(self, func):
        def decorated(context, hex, *args, **kwargs):
            hex = self.wraparound_hex(context.map, hex)
            return func(context, hex, *args, **kwargs)
        
        return decorated
    
    def move_tile_decorator(self, func):
        def decorated(context, hex, target, direction, *args, **kwargs):
            target = self.wraparound_hex(context.map, target)
            return func(context, hex, target, direction, *args, **kwargs)
        
        return decorated
    
    def get_strength_decorator(self, func):
        def decorated(context, hex, direction, *args, **kwargs):
            strength = 0
            while self.player.get_hex(context, hex) == self.player.index:
                strength += 1
                next_hex = hex + direction
                hex = self.wraparound_hex(context.map, next_hex)
                if hex != next_hex: strength += 1

            return strength

        return decorated
    
    def evaluate_for_player_decorate(self, func):
        def decorated(context, player):
            return sum(context.map.size - hex.length + 1 for hex, value in context.map.items() if value == player.index)

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


class Liquid(Power):
    name = "Liquide"
    icon = "💧"
    description = "Se déplace dans la direction choisie avant de se répliquer"

    def move_decorator(self, func):
        def decorated(context, *args, **kwargs):
            first_result = self.player.displace(context, *args, ties_consume_units=True, **kwargs)
            if not first_result.valid: return first_result

            second_result = func(first_result.context, *args, **kwargs)
            second_result.valid = second_result.context.map != context.map
            second_result.fights.extend(first_result.fights)
            return second_result
        
        return decorated
    

class Turtle(Power):
    name = "Tortue"
    icon = "🐢"
    description = "Gagne +1 en combat si l'unité en combat est supportée par deux unités alliées"

    def get_strength_decorator(self, func):
        def decorated(context, hex, direction, *args, **kwargs):
            bonus = 1 if (
                self.player.get_hex(context, hex + direction.rotate(1)) == 
                self.player.get_hex(context, hex + direction.rotate(-1)) == 
                self.player.index
            ) else 0
            
            return func(context, hex, direction, *args, **kwargs) + bonus
        
        return decorated
    

class ActivePower(Power):
    @dataclass
    class Data(Power.Data):
        active: bool = True
        uses: int = 1

    multiple_uses_per_turn = False

    def use(self, context):
        new_context = super().use(context)
        if new_context is None: return None

        editor = Power.ContextPowerDataEditor(self, new_context)
        editor.data.uses -= 1
        editor.data.active = editor.data.uses > 0 and self.multiple_uses_per_turn
        return editor.new_context
    
    def start_turn_decorator(self, func):
        def decorated(context, *args, **kwargs):
            data = self.data_from_context(context)
            if data.uses > 0:
                editor = Power.ContextPowerDataEditor(self, context)
                editor.data.active = True
                context = editor.new_context

            return func(context, *args, **kwargs)

        return decorated
    

class Glitcher(ActivePower):
    name = "Glitcheur"
    icon = "👾"
    description = "Une fois par partie, peut jouer deux tours d'affilée"
    activation_description = "Le Glitcheur va jouer deux tours d'affilée"

    def use(self, context):
        new_context = super().use(context)
        if new_context is None: return None
        
        editor = Power.ContextPowerDataEditor(self, new_context)
        editor.data.extra_turn = True
        return editor.new_context
    

class General(ActivePower):
    @dataclass
    class Data(ActivePower.Data):
        ratio: int = 0

    name = "Général"
    icon = "🚩"
    description = "Une fois par partie, peut tripler puis doubler la force de ses unités sur deux tours"
    activation_description = "Les unités du Général vont être triplées puis doublées sur 2 tours"

    def use(self, context):
        new_context = super().use(context)
        if new_context is None: return None

        editor = Power.ContextPowerDataEditor(self, new_context)
        editor.data.ratio = 2
        return editor.new_context

    def start_turn_decorator(self, func):
        def decorated(context, *args, **kwargs):
            data = self.data_from_context(context)
            if data.ratio > 0: 
                editor = Power.ContextPowerDataEditor(self, context)
                editor.data.ratio -= 1
                context = editor.new_context
            
            return func(context, *args, **kwargs)

        return super().start_turn_decorator(decorated)

    def get_strength_decorator(self, func):
        def decorated(context, *args, **kwargs):
            return func(context, *args, **kwargs) * (self.data_from_context(context).ratio + 1)

        return decorated
    
    def info_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + (f" ({self.icon} x{self.data.ratio + 1})" if self.data.ratio > 0 else "")
        
        return decorated


class Scout(ActivePower):
    @dataclass
    class Data(ActivePower.Data):
        uses: int = 2
        moving: bool = False
    
    name = "Éclaireur"
    icon = "🗺️"
    description = "Deux fois par partie, peut se déplacer dans une direction choisie (ne peut pas attaquer)"
    activation_description = "Les unités de l'Éclaireur vont se déplacer"

    def use(self, context):
        new_context = super().use(context)
        if new_context is None: return None

        editor = Power.ContextPowerDataEditor(self, new_context)
        editor.data.moving = True
        editor.data.extra_turn = True
        return editor.new_context

    def move_decorator(self, func):
        def decorated(context, *args, **kwargs):
            data = self.data_from_context(context)
            if data.moving:
                editor = Power.ContextPowerDataEditor(self, context)
                editor.data.moving = False  # If the move fails, this data won't be applied
                return self.player.displace(editor.new_context, *args, **kwargs)

            return func(context, *args, **kwargs)
        
        return decorated

    def get_strength_decorator(self, func):
        def decorated(context, *args, **kwargs):
            attacking = kwargs.get("attacking", False)
            return (
                -math.inf 
                if self.data_from_context(context).moving and attacking 
                else func(context, *args, **kwargs)
            )

        return decorated

    def info_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + (f" ({self.icon} x{self.data.uses})" if self.data.uses > 0 else "")
        
        return decorated


def get_leaf_subclasses(cls):
    subclasses = cls.__subclasses__()
    if not len(subclasses): yield cls
    
    for subclass in subclasses:
        for subsubclass in get_leaf_subclasses(subclass):
            yield subsubclass

ALL_POWERS = tuple(get_leaf_subclasses(Power))
