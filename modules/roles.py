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
            "`{prefix}roles list`": "Liste les roles",
            "`{prefix}roles <role>": "S'attribuer le role <role>"
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.RoleList = {
            "suspect": [435559220860157952, "Permet d'être notifié pour les mini-jeux"],
            "clash-of-coders": [496372436967882774, "Permet d'être notifié pour les parties de clash-of-code"],
            "civ-e-lization": [513098739515392022, "Donne accès aux salons liés aux parties de Civilization"],
        }

    async def on_message(self, message):
        args = message.content.split()
        if len(args) == 2:
            if args[1] == 'list':
                response = "```\nListe des roles disponibles :\n\n"
                for nom, idgrp in self.RoleList.items():
                    response += nom + "  =>  " + idgrp[1] + "\n\n"
                await message.channel.send(message.author.mention + response + "\n```")
            elif message.channel is discord.TextChannel:
                try:
                    if discord.utils.get(message.guild.roles, id=self.RoleList[args[1]][0]) in message.author.roles:
                        await message.author.remove_roles(
                            discord.utils.get(message.guild.roles, id=self.RoleList[args[1]][0]))
                        await message.channel.send(
                            message.author.mention + ", Vous avez perdu le rôle {args[1]}.".format())
                    else:
                        await message.author.add_roles(
                            discord.utils.get(message.guild.roles, id=self.RoleList[args[1]][0]))
                        await message.channel.send(
                            message.author.mention + ", Vous avez reçu le rôle {args[1]}.".format())
                except KeyError:
                    await message.channel.send(
                        message.author.mention + ", ce rôle n'est pas disponible à l'auto-attribution. Vous pouvez "
                                                 "obtenir la liste des rôles disponibles grâce à la commande `%srole "
                                                 "list`." % self.prefix)
            else:
                try:
                    for member in self.client.get_all_members():
                        if member.id == message.author.id and \
                                discord.utils.get(member.guild.roles, id=self.RoleList[args[1]][0]) \
                                in member.guild.roles:
                            if discord.utils.get(member.guild.roles, id=self.RoleList[args[1]][0]) in member.roles:
                                await member.remove_roles(
                                    discord.utils.get(member.guild.roles, id=self.RoleList[args[1]][0]))
                                await message.channel.send(
                                    message.author.mention + ", Vous avez perdu le rôle %s." % args[1])
                            else:
                                await member.add_roles(
                                    discord.utils.get(member.guild.roles, id=self.RoleList[args[1]][0]))
                                await message.channel.send(
                                    message.author.mention + ", Vous avez reçu le rôle %s." % args[1])
                except KeyError:
                    await message.channel.send(
                        message.author.mention + ", ce rôle n'est pas disponible à l'auto-attribution. Vous pouvez "
                                                 "obtenir la liste des rôles disponibles grâce à la commande `%srole "
                                                 "list`." % self.prefix)
