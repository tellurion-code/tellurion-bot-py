import discord
import random

from modules.reaction_message.reaction_message import ReactionMessage

import modules.tank.globals as global_values


class Player:
    index = -1
    direction = 0
    x = -1
    y = -1
    confirmed = False
    ammo = 3
    ammo_max = 3

    def __init__(self, user):
        self.user = user

    def spawn(self, game, map, x, y, dir):
        self.x = x
        self.y = y
        self.direction = dir

    def kill(self, game, killer):
        killer_name = "`" + str(killer.user) + "`" if isinstance(killer, Player) else killer
        if self.user.id in game.order:
            game.order.remove(self.user.id)

        return random.choice(global_values.kill_phrases).format("`" + str(self.user) + "`", killer_name)
