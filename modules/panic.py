import subprocess

from modules.base import BaseClass


class MainClass(BaseClass):
    nom = "Panic"
    help_active = True
    help = {
        "description": "Dans quel état est Nikola Tesla",
        "commands": {
            "`{prefix}panic`": "Donne l'état actuel de Nikola Tesla",
        }
    }
    command_text = "panic"

    async def command(self, message, args, kwargs):
        temperature = 0
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temperature = f.read()
        await message.channel.send("Nikola est à {temperature}°C".format(temperature=temperature))
