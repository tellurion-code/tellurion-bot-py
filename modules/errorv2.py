import random
import traceback

import discord

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "errorv2"

    super_users = [431043517217898496]

    color = 0x7289da

    help_active = True
    help = {
        "description": "Module gérant les erreurs",
        "commands": {}
    }

    command_text = "errors"

    async def on_error(self, event, *args, **kwargs):
        chan = self.client.get_channel(456142390726623243)
        await chan.send(traceback.format_exc())
