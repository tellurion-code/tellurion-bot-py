import discord
import sys
from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Restart"
    color = 0xff071f
    help_active = True
    authorized_roles = [431043517217898496]
    help = {
        "description": "Module gérant les redémarrages de Nikola Tesla",
        "commands": {
            "`{prefix}{command}`": "Redémarre le bot.",
        }
    }
    command_text = "restart"

    async def command(self, message, args, kwargs):
        await message.channel.send(f"{message.author.mention}, Le bot va redémarrer.")
        await self.client.logout()
        sys.exit(0)
