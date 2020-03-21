import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Roles"
    color = 0xffb593
    help_active = True
    help = {
        "description": "Modulé gérant l'attribution des roles",
        "commands": {
            "`{prefix}{command} list`": "Liste les roles",
            "`{prefix}{command} <role>`": "S'attribuer le role <role>"
        }
    }
    command_text = "roles"

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"roles": {}})

    async def com_list(self, message, args, kwargs):
        response = discord.Embed(title="Roles disponibles", color=self.color)
        for id_ in self.config.roles.keys():
            role = await self.client.id.get_role(int(id_))
            response.add_field(name=role.name, value=self.config.roles[id_], inline=True)
        await message.channel.send(embed=response)

    async def com_add(self, message, args, kwargs):
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role in args[0:]:
            role = await self.client.id.get_role(name = role)
            print(role.name)
