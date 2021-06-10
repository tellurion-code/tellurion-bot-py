import discord

import modules.codenames.globals as global_values

class Player():
    team = -1

    def __init__(self, user):
        self.user = user
