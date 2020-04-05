import discord
import sys
from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "ReadRules"
    color = 0xff071f
    help_active = False
    help = {
        "description": "Module d'accueil",
        "commands": {
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"accepted_role":430846685380345876,
                          "new_role":430845952388104212,
                          "listen_chan":430995739636793345,
                          "log_chan":429977240202248192,
                          "passwords":["cacahuète","cacahuete","cacahuètes","cacahuetes"],
                          "succes_pm":"Félicitations, vous êtes désormais un **e-penseur** accompli. Bienvenue sur le serveur E-penser.",
                          "succes":" est désormais un **e-penseur** accompli."})

    async def on_message(self, message):
        if message.channel.id == self.config.listen_chan:
            if message.content.lower() in self.config.passwords:
                new_role = await self.client.id.get_role(id_=self.config.new_role, guild=message.channel.guild)
                if new_role in message.author.roles:
                    await message.author.remove_roles(new_role)
                    await message.author.add_roles(await self.client.id.get_role(id_=self.config.accepted_role,
                                                                                guild=message.channel.guild))
                    await message.author.send(self.config.succes_pm)
                    await message.channel.guild.get_channel(self.config.log_chan).send(message.author.mention + self.config.succes)
            else:
                await message.author.send(f"Le mot de passe que vous avez entré est incorrect : `{message.content}`.\nNous vous prions de lire le règlement afin d'accéder au serveur complet.")
