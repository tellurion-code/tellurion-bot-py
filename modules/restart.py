from .base import BaseClass


class MainClass(BaseClass):
    name = "Restart"

    authorized_roles = [431043517217898496]

    color = 0x000000

    help_active = True
    help = {
        "description": "Module gérant les redémarages du bot",
        "commands": {
            "`{prefix}{command} py`": "Redémare le bot",
        }
    }

    command_text = "restart"

    async def command(self, message, args, kwargs):
        await message.channel.send(message.author.mention + ", vous devez utiliser {prefix}restart py pour redémarrer "
                                                            "le bot".format(prefix=self.client.config["prefix"]))

    async def com_py(self, message, args, kwargs):
        await self.client.logout()
