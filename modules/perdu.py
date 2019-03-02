import time

import discord


class MainClass:
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message']  # events list
        self.command = "%sperdu" % prefix  # command prefix (can be empty to catch every single messages)

        self.channel = 431016132040851459
        self.lost_role = 544845665910390784  # grand_perdant
        self.save = {'last_occurence': None, 'messages_dict': None}  # To avoid calling the API each time.

        self.name = "Perdu"
        self.description = "Module donnant les statistiques sur les perdants"
        self.interactive = True
        self.color = 0xff6ba6
        self.help = """\
 </prefix>perdu
 => Donne les statistiques des perdants de la semaine
 
 </prefix>perdu <durée en jours>
 => Donne les statistiques des perdants depuis la durée donnée (exemple </prefix>perdu 30 donnera les statistiques des 30 derniers jours.)
 
 </prefix>perdu all
 => Donne les statistiques des perdants depuis la création du salon
"""

    async def fetch_stats(self, upto, today):  # upto in days (integer)
        message_dict = {}
        if (not self.save['message_dict']) or \
                (time.mktime(today.timetuple()) - time.mktime(self.save['last_occurence'].timetuple())) / 60 > 15:
            for channel in self.client.get_all_channels():
                if channel.id == self.channel:
                    break

            async for message in channel.history(limit=None):
                if message.author.id not in message_dict.keys():
                    message_dict[message.author.id] = [message]
                else:
                    message_dict[message.author.id].append(message)
            self.save.update({'message_dict': message_dict, 'last_occurence': today})
        else:
            message_dict = self.save['message_dict']
        message_dict_reduced = {}
        for user_id, message_list in message_dict.items():
            message_list = message_list[::-1]
            message_list_2 = [message_list[0].author]
            last_message = None
            for message in message_list:
                # 86400 = 60*60*24 (nombre de secondes par jour
                if (time.mktime(today.timetuple()) - time.mktime(message.created_at.timetuple())) / 86400 < upto and \
                        (
                                last_message is None or
                                (
                                        (time.mktime(message.created_at.timetuple()) -
                                         time.mktime(last_message.created_at.timetuple())) / 60 > 26
                                )
                        ) and \
                        (not message.author.id == self.client.user.id):
                    message_list_2.append(message)
                    last_message = message
            message_list = message_list_2
            del message_list_2
            message_dict_reduced.update({user_id: message_list})

        sorted_by_losses = sorted(message_dict_reduced.items(), key=lambda x: len(x[1]))[::-1]
        stats = []
        for user in sorted_by_losses:
            # user mention, number of losses, average time between each loss
            to_append = [user[1][0], len(user[1]) - 1, 0]
            if len(user[1][1::]) > 1:
                to_append[2] = (time.mktime(user[1][1::][-1].created_at.timetuple()) -
                                time.mktime(user[1][1::][0].created_at.timetuple())) / ((len(user[1][1::]) - 1) * 3600)
            stats.append(to_append)
        return sorted(sorted(stats, key=lambda x: x[2])[::-1], key=lambda x: x[1])[::-1][:10:]

    async def on_message(self, message):
        args = message.content.split()
        if len(args) == 1:
            async with message.channel.typing():
                stats = await self.fetch_stats(7, message.created_at)
                if self.lost_role not in [role.id for role in stats[0][0].roles]:
                    for member in self.client.get_all_members():
                        if self.lost_role in [role.id for role in member.roles]:
                            await member.remove_roles(discord.utils.get(member.guild.roles, id=self.lost_role))
                    await stats[0][0].add_roles(discord.utils.get(stats[0][0].guild.roles, id=self.lost_role))
                embed_description = '\n'.join(
                    [
                        "%s : %s a **perdu %s fois** durant les %s derniers jours à en moyenne **%s "
                        "heures d'intervalle.**" % (
                            ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i],
                            user[0].mention, user[1],
                            7,
                            round(user[2], 1)
                        )
                        for i, user in enumerate(stats)
                    ]
                )
                await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                               description=embed_description,
                                                               color=self.color))
        elif args[1] == "all":
            async with message.channel.typing():
                embed_description = '\n'.join(
                    [
                        "%s : %s a **perdu %s fois** depuis la création du salon à en moyenne **%s heures "
                        "d'intervalle.**" % (
                            ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i],
                            user[0].mention,
                            user[1],
                            round(user[2], 1)
                        ) for i, user in enumerate(await self.fetch_stats(1e1000, message.created_at))
                    ]
                )
                await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                               description='\n'.embed_description,
                                                               color=self.color))
        else:
            try:
                int(args[1])
                async with message.channel.typing():
                    embed_description = '\n'.join(
                        [
                            "%s : %s a **perdu %s fois** durant les %s derniers jours à en moyenne **%s heures "
                            "d'intervalle.**" % (
                                ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i],
                                user[0].mention,
                                user[1],
                                int(args[1]),
                                round(user[2], 1)
                            ) for i, user in enumerate(await self.fetch_stats(int(args[1]), message.created_at))
                        ]
                    )
                    await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                                   description=embed_description,
                                                                   color=self.color))
            except ValueError:
                await self.modules['help'][1].send_help(message.channel, self)
