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
            "`{prefix}{command}  <role> [role] ...`": "S'attribuer (ou désattribuer) le(s) rôles <role> ([role]...)",
        }
    }
    command_text = "roles"

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"guild":297780867286433792,
                          "roles": {"435559220860157952":"Rôle mentionné lors des jeux."}})

    async def com_list(self, message, args, kwargs):
        response = discord.Embed(title="Roles disponibles", color=self.color)
        for id_ in self.config.roles.keys():
            print(id_,type(id_))
            role = message.guild.get_role(int(id_))
            if role is not None:
                response.add_field(name=role.name, value=f" -> `{self.config.roles[id_]}`", inline=True)
        await message.channel.send(embed=response)

    async def com_add(self, message, args, kwargs):
        guild = self.client.get_guild(self.config.guild)
        member = guild.get_member(message.author.id)
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role_ in args[1:]:
            role = await self.client.id.get_role(name=role_, guild=guild, case_sensitive=False)
            if role is None or str(role.id) not in self.config.roles.keys():
                await message.channel.send(f"Le role {role_} n'est pas disponible.")
            else:
                await self.tryaddrole(message, member, role)

    async def com_remove(self, message, args, kwargs):
        guild = self.client.get_guild(self.config.guild)
        member = guild.get_member(message.author.id)
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role_ in args[1:]:
            role = await self.client.id.get_role(name=role_, guild=guild, case_sensitive=False)
            if role is None or str(role.id) not in self.config.roles.keys():
                await message.channel.send(f"Le role {role_} n'est pas disponible.")
            else:
                await self.tryremoverole(message, member, role)

    async def com_toggle(self, message, args, kwargs):
        guild = self.client.get_guild(self.config.guild)
        member = guild.get_member(message.author.id)
        if len(args) <= 1:
            await message.channel.send("Il manque des arguments à la commande")
        for role_ in args[1:]:
            role = await self.client.id.get_role(name=role_, guild=guild, case_sensitive=False)
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
            role = await self.client.id.get_role(name=role_, guild=guild, case_sensitive=False)
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
