import time

import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Panic"
    help = {
        "description": "Dans quel état est Nikola Tesla",
        "commands": {
            "`{prefix}{command}`": "Donne l'état actuel de Nikola Tesla",
        }
    }

    async def command(self, message, args, kwargs):
        temperature = 0
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temperature = int(f.read().rstrip("\n")) / 1000
        with open("/proc/cpuinfo") as f:
            cpu_count = f.read().count('\n\n')
        embed = discord.Embed(title="[Panic] - Infos", color=self.config.color)
        with open("/proc/loadavg") as f:
            load_average = ["**" + str(round((val / cpu_count) * 100, 1)) + '%**' for val in
                            map(float, f.read().split(' ')[0:3])]
        with open("/proc/uptime") as f:
            uptime = time.gmtime(float(f.read().split(' ')[0]))
            uptime = "**" + str(int(time.strftime('%-m', uptime)) - 1) + "** mois, **" + str(
                int(time.strftime('%-d', uptime)) - 1) + "** jours, " + time.strftime(
                '**%H** heures, **%M** minutes, **%S** secondes.', uptime)
        embed.add_field(
            name="Température",
            value="Nikola est à **{temperature}°C**".format(temperature=temperature))

        embed.add_field(
            name="Charge moyenne",
            value=f"{self.client.name} est en moyenne, utilisé à :\n sur une minute : %s\n sur cinq minutes : %s\n sur quinze minutes : %s" % tuple(
                load_average))

        embed.add_field(
            name="Temps d'éveil",
            value=f"{self.client.name} est éveillé depuis {uptime}".format(uptime=uptime))
        await message.channel.send(embed=embed)
