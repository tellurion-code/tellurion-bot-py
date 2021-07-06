# dummy module
import discord

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "Role"
    super_users = []
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
        self.RoleList = {
            "joueur": [435559220860157952, "Permet d'être notifié pour les mini-jeux/jeux"],
            "animation": [861706123254038559, "Permet d'être notifié pour les annonces et rappels d'animations"],
            "rework": [851761080040685568, "Permet d'être notifié pour les évènements liés au rework"]
        }

    async def com_list(self, message, args, kwargs):
        response = "```\nListe des roles disponibles :\n\n"
        for nom, idgrp in self.RoleList.items():
            response += nom + "  =>  " + idgrp[1] + "\n\n"
        await message.channel.send(message.author.mention + response + "\n```")

    async def command(self, message, args, kwargs):
        if len(args) != 1 or args[0] == '':
            await self.send_help(message.channel)
        else:
            if type(message.channel) is discord.TextChannel:
                try:
                    role = discord.utils.get(message.guild.roles, id=self.RoleList[args[0]][0])
                    if role is None:
                        await message.channel.send(message.author.mention + ", Ce rôle est indisponible")
                        return
                    if discord.utils.get(message.guild.roles, id=self.RoleList[args[0]][0]) in message.author.roles:
                        await message.author.remove_roles(
                            discord.utils.get(message.guild.roles, id=self.RoleList[args[0]][0]))
                        await message.channel.send(
                            message.author.mention + ", Vous avez perdu le rôle {}.".format(args[0]))
                    else:
                        await message.author.add_roles(
                            discord.utils.get(message.guild.roles, id=self.RoleList[args[0]][0]))
                        await message.channel.send(
                            message.author.mention + ", Vous avez reçu le rôle {}.".format(args[0]))
                except KeyError:
                    await message.channel.send(
                        message.author.mention + ", ce rôle n'est pas disponible à l'auto-attribution. Vous pouvez "
                                                 "obtenir la liste des rôles disponibles grâce à la commande `{prefix}{commande} "
                                                 "list`.".format(prefix=self.client.config['prefix'], commande=self.command_text))
            else:
                try:
                    for member in self.client.get_all_members():
                        if member.id == message.author.id and \
                                discord.utils.get(member.guild.roles, id=self.RoleList[args[0]][0]) \
                                in member.guild.roles:
                            if discord.utils.get(member.guild.roles, id=self.RoleList[args[0]][0]) in member.roles:
                                await member.remove_roles(
                                    discord.utils.get(member.guild.roles, id=self.RoleList[args[0]][0]))
                                await message.channel.send(
                                    message.author.mention + ", Vous avez perdu le rôle %s." % args[0])
                            else:
                                await member.add_roles(
                                    discord.utils.get(member.guild.roles, id=self.RoleList[args[0]][0]))
                                await message.channel.send(
                                    message.author.mention + ", Vous avez reçu le rôle %s." % args[0])
                except KeyError:
                    await message.channel.send(
                        message.author.mention + ", ce rôle n'est pas disponible à l'auto-attribution. Vous pouvez "
                                                 "obtenir la liste des rôles disponibles grâce à la commande `{prefix}{commande} "
                                                 "list`.".format(prefix=self.client.config['prefix'], commande=self.command_text))
