import discord


class MainClass:
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message']  # events list
        self.command = "%srole" % self.prefix  # command prefix (can be empty to catch every single messages)

        self.name = "Roles"
        self.description = "Module d'auto-attribution des rôles"
        self.interactive = True
        self.color = 0xffb593
        self.help = """\
 </prefix>role list
 => Affiche la liste des rôles
 
 </prefix>role <nom du rôle>
 => Vous donne ou vous retire le rôle donné
"""
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
