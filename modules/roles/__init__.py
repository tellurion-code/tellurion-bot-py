import discord

from modules.base import BaseClassPython


class RoleAttributionError(Exception):
    pass


class AlreadyHasRoleError(RoleAttributionError):
    pass


class AlreadyRemovedRole(RoleAttributionError):
    pass


class UnavailableRoleError(RoleAttributionError):
    pass


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
            role = message.guild.get_role(role_id=int(id_))
            if role is not None:
                response.add_field(name=role.name, value=f"-> `{self.config.roles[id_]}`", inline=True)
        await message.channel.send(embed=response)

    async def com_add(self, message, args, kwargs):
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role in args[1:]:
            try:
                await self.try_add_role(message.author, role)
            except discord.errors.Forbidden:
                await message.channel.send(f"Je n'ai pas la permission de modifier le role {role}.")
            except AlreadyHasRoleError:
                await message.channel.send(f"Vous avez déjà le role {role}.")
            except UnavailableRoleError:
                await message.channel.send(f"Le role {role} n'est pas une role disponible à l'autoattribution.")

    async def com_remove(self, message, args, kwargs):
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role in args[1:]:
            try:
                await self.try_remove_role(message.author, role)
            except discord.errors.Forbidden:
                await message.channel.send(f"Je n'ai pas la permission de modifier le role {role}.")
            except AlreadyRemovedRole:
                await message.channel.send(f"Vous n'avez pas le role {role}.")
            except UnavailableRoleError:
                await message.channel.send(f"Le role {role} n'est pas une role disponible à l'autoattribution.")

    async def com_toggle(self, message, args, kwargs):
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role in args[1:]:
            try:
                await self.try_toggle_role(message.author, role)
            except discord.errors.Forbidden:
                await message.channel.send(f"Je n'ai pas la permission de modifier le role {role}.")
            except AlreadyHasRoleError:
                await message.channel.send(f"Vous avez déjà le role {role}.")
            except AlreadyRemovedRole:
                await message.channel.send(f"Vous n'avez pas le role {role}.")
            except UnavailableRoleError:
                await message.channel.send(f"Le role {role} n'est pas une role disponible à l'autoattribution.")

    async def command(self, message, args, kwargs):
        if len(args) < 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role in args:
            try:
                await self.try_toggle_role(message.author, role)
            except discord.errors.Forbidden:
                await message.channel.send(f"Je n'ai pas la permission de modifier le role {role}.")
            except AlreadyHasRoleError:
                await message.channel.send(f"Vous avez déjà le role {role}.")
            except AlreadyRemovedRole:
                await message.channel.send(f"Vous n'avez pas le role {role}.")
            except UnavailableRoleError:
                await message.channel.send(f"Le role {role} n'est pas une role disponible à l'autoattribution.")

    def get_member(self, user):
        return self.client.get_guild(self.client.config.main_guild).get_member(user.id)

    def get_role(self, role):
        role = self.client.id.get_role(name=role, guilds=[self.client.get_guild(self.client.config.main_guild)],
                                       check=lambda x: x.name.lower() == role.lower())
        if role is None or str(role.id) not in self.config.roles.keys():
            raise UnavailableRoleError()
        return role

    async def try_toggle_role(self, user, role):
        if self.get_role(role) in self.get_member(user).roles:
            await self.try_remove_role(user, role)
        else:
            await self.try_add_role(user, role)

    async def try_add_role(self, user, role):
        role = self.get_role(role)
        if role in user.roles:
            raise AlreadyHasRoleError()
        await self.get_member(user).add_roles(role, reason="Auto-attribution")

    async def try_remove_role(self, user, role):
        role = self.get_role(role)
        if role not in user.roles:
            raise AlreadyRemovedRole()
        await self.get_member(user).remove_roles(role, reason="Auto-désattribution")
