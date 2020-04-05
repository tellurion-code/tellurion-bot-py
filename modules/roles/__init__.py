import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Roles"
    help = {
        "description": "Module gérant l'attribution des roles",
        "commands": {
            "`{prefix}{command} list`": "Liste les roles",
            "`{prefix}{command} add <role> [role] ...`": "S'attribuer le(s) rôle(s) <role> ([role]...)",
            "`{prefix}{command} remove <role> [role] ...`": "Se désattribuer  le(s) rôle(s) <role> ([role]...)",
            "`{prefix}{command} toggle <role> [role] ...`": "S'attribuer (ou désattribuer) le(s) rôle(s) <role> ([role]...)",
            "`{prefix}{command} <role> [role] ...`": "Alias de `{prefix}{command} toggle`",
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"roles": {}})

    async def com_list(self, message, args, kwargs):
        response = discord.Embed(title="Roles disponibles", color=self.config.color)
        for id_ in self.config.roles.keys():
            role = message.guild.get_role(id_=int(id_))
            if role is not None:
                response.add_field(name=role.name, value=f"-> `{self.config.roles[id_]}`", inline=True)
        await message.channel.send(embed=response)

    async def com_add(self, message, args, kwargs):
        guild = self.client.get_guild(self.client.config.main_guild)
        member = guild.get_member(message.author.id)
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role_ in args[1:]:
            role = await self.client.id.get_role(name=role_, guilds=[guild],
                                                 check=lambda x: x.name.lower() == role_.lower())
            if role is None or str(role.id) not in self.config.roles.keys():
                await message.channel.send(f"Le role {role_} n'est pas disponible.")
            else:
                await self.tryaddrole(message, member, role)

    async def com_remove(self, message, args, kwargs):
        guild = self.client.get_guild(self.client.config.main_guild)
        member = guild.get_member(message.author.id)
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role_ in args[1:]:
            role = await self.client.id.get_role(name=role_, guilds=[guild],
                                                 check=lambda x: x.name.lower() == role_.lower())
            if role is None or str(role.id) not in self.config.roles.keys():
                await message.channel.send(f"Le role {role_} n'est pas disponible.")
            else:
                await self.tryremoverole(message, member, role)

    async def com_toggle(self, message, args, kwargs):
        guild = self.client.get_guild(self.client.config.main_guild)
        member = guild.get_member(message.author.id)
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role_ in args[1:]:
            role = await self.client.id.get_role(name=role_, guilds=[guild],
                                                 check=lambda x: x.name.lower() == role_.lower())
            if role is None or str(role.id) not in self.config.roles.keys():
                await message.channel.send(f"Le role {role_} n'est pas disponible.")
            else:
                await self.trytogglerole(message, member, role)

    async def command(self, message, args, kwargs):
        guild = self.client.get_guild(self.config.guild)
        member = guild.get_member(message.author.id)
        if len(args) < 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role_ in args:
            role = await self.client.id.get_role(name=role_, guilds=[guild],
                                                 check=lambda x: x.name.lower() == role_.lower())
            if role is None or str(role.id) not in self.config.roles.keys():
                await message.channel.send(f"Le role {role_} n'est pas disponible.")
            else:
                await self.trytogglerole(message, member, role)

    async def trytogglerole(self, message, member, role):
        if role in member.roles:
            await self.tryremoverole(message, member, role)
        else:
            await self.tryaddrole(message, member, role)

    async def tryaddrole(self, message, member, role):
        if role in member.roles:
            await message.channel.send(f"Vous avez déjà le rôle {role}.")
            return
        try:
            await member.add_roles(role, reason="Auto-attribution")
        except discord.errors.Forbidden:
            await message.channel.send(f"Je n'ai pas la permission de vous attribuer le rôle {role}.")
        else:
            await message.channel.send(f"Vous avez reçu le rôle {role}.")

    async def tryremoverole(self, message, member, role):
        if not role in member.roles:
            await message.channel.send(f"Vous n'avez pas le rôle {role}.")
            return
        try:
            await member.remove_roles(role, reason="Auto-désattribution")
        except discord.errors.Forbidden:
            await message.channel.send(f"Je n'ai pas la permission de vous retirer le rôle {role}.")
        else:
            await message.channel.send(f"Vous avez perdu le rôle {role}.")
