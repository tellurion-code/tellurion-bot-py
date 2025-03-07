import random
import discord
from modules.base import BaseClassPython

def userstr(user):
    if user:
        return user.name
    else:
        return "None"

class MainClass(BaseClassPython):
    name = "Secret"
    help = {
        "description": "Secret",
        "commands": {
            "There is no commands"
        }
    }
    games = {}

    colors = [
        #878722,
        #8b8722,
        #8e8623,
        #928523,
        #968423,
        #9a8223,
        #9e8123,
        #a27e23,
        #a67c23,
        #a97924,
        #ad7724,
        #b17324,
        #b57024,
        #b96c24,
        #be6823,
        #c26323,
        #c65e23,
        #ca5923,
        #ce5323,
        #d24e23,
        #d64723,
        #db4122,
        #dd3b24,
        #df3626,
        #e03129,
        #e12d2c,
        #e22f35,
        #e4313f,
        #e53448,
        #e63752
    ]

    def __init__(self, client):
        super().__init__(client)
        self.config["auth_everyone"] = True
        self.config["configured"] = True
        self.config["help_active"] = True
        self.config["command_text"] = "roll"
        self.config["color"] = 0x000000

    async def on_ready(self):
        self.change_color.start()

    @discord.ext.task.loop(seconds=10)
    async def change_color(self):
        guild = self.client.get_guild(self.client.config.main_guild)
        role = guild.get_role(1347659937542574140)
        if role:
            new_color = self.colors.pop(0)
            await role.edit(color=new_color)

    @change_color.before_loop
    async def before_loop():
        await discord.commands.bot.wait_until_ready()
