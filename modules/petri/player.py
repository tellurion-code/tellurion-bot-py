import discord

from modules.reaction_message.reaction_message import ReactionMessage

import modules.petri.globals as global_values


class Player:
    def __init__(self, user):
        self.user = user
