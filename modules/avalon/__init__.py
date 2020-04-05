import datetime

import discord

import utils.emojis
from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Avalon"
    help = {
        "description": "Maître du jeu Avalon.",
        "commands": {
            "`{prefix}{command} join`": "",
            "`{prefix}{command} quit`": "",
            "`{prefix}{command} players list`": "",
            "`{prefix}{command} players kick (<user_id>/<@mention>)`": "",
            "`{prefix}{command} roles setup`": "",
            "`{prefix}{command} roles list`": "",
        }
    }
    help_active = True
    command_text = "perdu"
    color = 0xff6ba6

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"spectate_channel": 0,
                          "illustrations":{"merlin":"",
                                           "perceval":"",
                                           "gentil":"",
                                           "assassin":"",
                                           "mordred":"",
                                           "morgane":"",
                                           "oberon":"",
                                           "mechant":""},
                          "couleurs":{"merlin":"",
                                      "perceval":0,
                                      "gentil":0,
                                      "assassin":0,
                                      "mordred":0,
                                      "morgane":0,
                                      "oberon":0,
                                      "mechant":0,
                                      "test":15},
                          "test":{"merlin":"",
                                           "perceval":0,
                                           "gentil":0,
                                           "assassin":0,
                                           "mordred":0,
                                           "morgane":0,
                                           "oberon":0,
                                           "mechant":0,
                                           "test":15}
                          })

