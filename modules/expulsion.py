# dummy module
import discord
import asyncio

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "Expulsion"
    super_users = []
    authorized_roles = [431043517217898496]
    color = 0xffb593
    eviewer=430845952388104212
    help_active = True
    help = {
        "description": "Modulé gérant l'expulsion des e-viewers",
        "commands": {
            "`{prefix}{command} purge`": "Expulse les e-viewers", 
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.lock = asyncio.Lock()

    async def com_purge(self, message, args, kwargs):
        async with self.lock:
            for member in self.client.get_all_members():
                if member.id == message.author.id and \
                        discord.utils.get(member.guild.roles, id=self.eviewer) \
                        in member.guild.roles:
                    if discord.utils.get(member.guild.roles, id=self.eviewer) in member.roles:
                        #await member.remove_roles(
                            #discord.utils.get(member.guild.roles, id=self.eviewer))
                        await message.channel.send(
                            message.author.mention + ", Toi tu meurs.")
                    else:
                        await message.channel.send(
                            message.author.mention + ", Toi tu vis.")
