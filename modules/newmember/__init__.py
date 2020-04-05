import discord
import sys
from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "NewMember"
    color = 0xff071f
    help_active = False
    help = {
        "description": "Module d'accueil",
        "commands": {
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"new_role":430845952388104212,
                          "guild":297780867286433792,
                          "motd":"Bienvenue sur le serveur de la communauté d'E-penser. Nous vous prions de lire le règlement afin d'accéder au serveur complet."})

    async def on_ready(self):
        guild = self.client.get_guild(self.config.guild)
        for i, member in enumerate(guild.members):
            if len(member.roles) == 1:
                await member.add_roles(await self.client.id.get_role(id_=self.config.new_role,
                                                                     guild=guild))
            if i%50==0:
                print(i, member)
    
    async def on_member_join(self, member):
        await member.add_roles(await self.client.id.get_role(id_=self.config.new_role,
                                                             guild=self.client.get_guild(self.config.guild)))
        await member.send(self.config.motd)
