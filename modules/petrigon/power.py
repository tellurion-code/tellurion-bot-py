"""Power class."""

import math
from copy import deepcopy
from dataclasses import dataclass, field
from modules.petrigon.constants import TILE_EMOJIS

from modules.petrigon.hex import Hex, DIRECTIONS_TO_EMOJIS
from modules.petrigon.types import Announcement
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
            self.data = deepcopy(power.data_from_context(context))
        
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
        powers_data = deepcopy(self.player.powers_data_from_context(context))
        powers_data[self.key] = data
        return context.copy(same_map=same_map, players_powers_data_update={self.player.id: powers_data})

    def use(self, context):
        if not self.data_from_context(context).active: return None
        return context
    
    def send_announcement(self):
        self.player.game.announcements.append(Announcement(
            name=f"{self.icon} Pouvoir du {self.name}",
            value=self.activation_description
        ))

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
        peace_with: set = field(default_factory=set)

    name = "Pacifiste"
    icon = "🕊️"
    description = "Ne peut pas être attaqué par les joueurs qu'il n'a pas attaqué"

    def setup(self):
        self.data.peace_with = set(x for x,p in self.player.game.players.items() if p != self.player)
        return super().setup()

    def get_strength_decorator(self, func):
        def decorated(context, *args, **kwargs):
            opponent = kwargs.get("opponent", None)
            attacking = kwargs.get("attacking", False)

            return (
                math.inf
                if opponent.id in self.data_from_context(context).peace_with and not attacking 
                else func(context, *args, **kwargs)
            )

        return decorated

    def end_turn_decorator(self, func):
        def decorated(result, *args, **kwargs):
            pass_turn, new_context = func(result, *args, **kwargs)

            # The new context is already a copy, it's fine to edit it directly
            for fight in result.fights:
                if fight.attacker == self.player:
                    self.data_from_context(new_context).peace_with.discard(fight.defender.id)
            
            return pass_turn, new_context

        return decorated

    def info_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + (f" ({self.icon} {''.join(TILE_EMOJIS[self.player.game.players[x].index] for x in self.data.peace_with)})" if len(self.data.peace_with) else "")
        
        return decorated


class Topologist(Power):
    name = "Topologiste"
    icon = "🍩"
    description = "Peut traverser les bords comme s'ils étaient adjacents"

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
    
    def evaluate_for_player_decorator(self, func):
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
    description = "Se déplace dans la direction choisie après s'être répliqué"

    def move_decorator(self, func):
        def decorated(context, *args, **kwargs):
            first_result = func(context, *args, **kwargs)
            if not first_result.valid: return first_result

            second_result = self.player.displace(first_result.context, *args, ties_consume_units=True, **kwargs)
            second_result.valid = hash(second_result.context) != hash(context)
            second_result.fights.extend(first_result.fights)
            return second_result
        
        return decorated


class Architect(Power):
    name = "Architecte"
    icon = "🧱"
    description = "Considère les murs adjacents à ses unités comme des unités alliées en combat"

    def get_strength_decorator(self, func):
        def decorated(context, hex, direction, *args, **kwargs):
            strength = 0
            while self.player.get_hex(context, hex) in (self.player.index, 1):
                strength += 1
                hex += direction

            return strength
        
        return decorated


class Navigator(Power):
    @dataclass
    class Data(Power.Data):
        last_direction: Hex = None

    name = "Navigateur"
    icon = "🧭"
    description = "Gagne +1 en combat dans la dernière direction choisie et la direction opposée"

    def move_decorator(self, func):
        def decorated(context, direction, *args, **kwargs):
            result = func(context, direction, *args, **kwargs)
            editor = Power.ContextPowerDataEditor(self, result.context)
            editor.data.last_direction = direction
            result.context = editor.new_context
            return result

        return decorated

    def get_strength_decorator(self, func):
        def decorated(context, hex, direction, *args, **kwargs):
            strength = func(context, hex, direction, *args, **kwargs)
            if not self.data.last_direction:
                return strength
            return strength + (1 if direction in (self.data.last_direction, self.data.last_direction * -1) else 0)
        
        return decorated
    
    def info_decorator(self, func):
        def decorated(*args, **kwargs):
            return func(*args, **kwargs) + (f" ({self.icon} {DIRECTIONS_TO_EMOJIS[self.data.last_direction]})" if self.data.last_direction else "")
        
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

    def info_decorator(self, func):
        def decorated(*args, **kwargs):
            uses_info = self.icon + (f" x{self.data.uses}" if self.data.uses > 1 else "")
            return func(*args, **kwargs) + (f" ({uses_info})" if self.data.uses > 0 else "")
        
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
        func = super().info_decorator(func)

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
                result = self.player.displace(context, *args, **kwargs)
                editor = Power.ContextPowerDataEditor(self, result.context)
                editor.data.moving = False
                result.context = editor.new_context
                return result

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


def get_leaf_subclasses(cls):
    subclasses = cls.__subclasses__()
    if not len(subclasses): yield cls
    
    for subclass in subclasses:
        for subsubclass in get_leaf_subclasses(subclass):
            yield subsubclass

ALL_POWERS = tuple(get_leaf_subclasses(Power))
