import sys

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Restart"
    help = {
        "description": "Module gérant les redémarrages de Nikola Tesla",
        "commands": {
            "`{prefix}{command}`": "Redémarre le bot.",
        }
    }

    async def command(self, message, args, kwargs):
        await message.channel.send(f"{message.author.mention}, Le bot va redémarrer.")
        await self.client.logout()
        # TODO: Faut vraiment faire mieux
        sys.exit(0)
