from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "NewMember"
    help = {
        "description": "Module d'accueil",
        "commands": {
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"new_role": 0,
                          "motd": "Bienvenue !"})

    async def on_ready(self):
        guild = self.client.get_guild(self.client.config.main_guild)
        for i, member in enumerate(guild.members):
            if len(member.roles) == 1:
                await member.add_roles(self.client.id.get_role(id_=self.config.new_role,
                                                               guilds=[self.client.get_guild(
                                                                   self.client.config.main_guild)]))
            if i % 50 == 0:
                self.client.log(f"Attribution des roles automatique manqués... {i}/{len(guild.members)}")

    async def on_member_join(self, member):
        await member.add_roles(self.client.id.get_role(id_=self.config.new_role,
                                                       guilds=[self.client.get_guild(
                                                           self.client.config.main_guild)]))
        await member.send(self.config.motd)
