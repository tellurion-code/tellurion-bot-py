import time

import discord
import random
from modules.base import BaseClass

import numpy as np
import matplotlib.pyplot as plt

class MainClass(BaseClass):
    name = "Perdu"
    super_users = []
    command_text = "perdu"
    color = 0xff6ba6
    help_active = True
    help = {
        "description": "Module donnant les statistiques sur les perdants",
        "commands": {
            "`{prefix}{command}`": "Donne le classement des perdants de la semaine",
            "`{prefix}{command} all`": "Donne le classement des perdants depuis toujours",
            "`{prefix}{command} <nombre de jours>`": "Donne le classement des perdants sur la durée spécifiée",
            "`{prefix}{command} stats [@mention]`": "Donne les statistiques d'un perdant",
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel = 431016132040851459
        self.lost_role = 544845665910390784  # grand_perdant
        self.save = {'last_occurence': None, 'message_dict': None}  # To avoid calling the API each time.

    async def fetch_stats(self, upto, today, user=None):
        message_dict = {}
        if (not self.save['message_dict']) or \
                (time.mktime(today.timetuple()) - time.mktime(self.save['last_occurence'].timetuple())) / 60 > 15:
            async for message in self.client.get_channel(self.channel).history(limit=None):
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
                # 86400 = 60*60*24 (nombre de secondes par jour)
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
            if len(message_list)>1:
                message_dict_reduced.update({user_id: message_list})
        if user is not None:
            user_activity=[] #order : recent -> older
            i=0
            remaining=True
            while remaining:
                week_messages=[]
                remaining=[]
                for message in message_dict_reduced[user.id][1:]:
                    if time.mktime(today.timetuple()) + 86400*7*i > time.mktime(message.created_at.timetuple()) > time.mktime(today.timetuple()) + 86400*7*(i-1):
                        week_messages.append(message)
                    elif time.mktime(message.created_at.timetuple()) < time.mktime(today.timetuple()) + 86400*7*(i-1):
                        remaining.append(message)
                user_activity.append(week_messages)
                i=i-1
            return user_activity
        sorted_by_losses = sorted(message_dict_reduced.items(), key=lambda x: len(x[1]))[::-1]
        stats = []
        for user in sorted_by_losses:
            # user, number of losses, average time between each loss
            to_append = [user[1][0], len(user[1]) - 1, 0]
            if len(user[1][1::]) > 1:
                to_append[2] = (time.mktime(user[1][1::][-1].created_at.timetuple()) -
                                time.mktime(user[1][1::][0].created_at.timetuple())) / ((len(user[1][1::]) - 1) * 3600)
            stats.append(to_append)
        return sorted(sorted(stats, key=lambda x: x[2])[::-1], key=lambda x: x[1])[::-1]
    
    async def reduce_stats(self, stats, user):
        if len(stats)<5:
            return (0,stats)
        else:
            if user.id in [element[0].id for element in stats[:3]] :
                return (0,stats[:5])
            else:
                for i in range(len(stats)):
                    if stats[i][0].id==user.id:
                        return (i-2,stats[i-2:i+3])
        return None

    async def com_stats(self, message, args, kwargs):
        if self.client.get_channel(self.channel) is None:
            await message.channel.send("Désolé ce module est indisponible")
            return
        async with message.channel.typing():
            if message.mentions:
                target_user=message.mentions[0]
            else:
                target_user=message.author
            today=message.created_at
            week_list=list(await self.fetch_stats(1e1000, today, user=target_user))[::-1]
            N = len(week_list)
            ind = np.arange(N)
            width = 0.35
            plt.figure(num=None, figsize=(25, 6), dpi=120, facecolor='w', edgecolor='k')
            p1 = plt.bar(ind, list(map(len,week_list)), width)
            plt.ylabel('Scores')
            plt.title('Scores par semaine au cours du temps')
            plt.xticks(ind, [time.strftime("%d/\n%m/\n%y" , time.localtime(time.mktime(today.timetuple()) + 86400*7*(-i-1))) for i in list(range(N))[::-1]])
            step=int(max(list(map(len,week_list)))/10)
            if step==0:
                step=1
            plt.yticks(np.arange(0, max(list(map(len,week_list))), step))
            file_name = "/tmp/%s.png" % random.randint(1, 10000000)
            plt.savefig(file_name)
            response = await message.channel.send(embed=discord.Embed(title="G-Perdu - Statistiques individuelles", description="Calcul en cours...", color=self.color), file=discord.File(file_name))
            stats=[({7:"dans la semaine",30:"dans le mois",1e1000:"depuis la création du salon"}[i], await self.reduce_stats(await self.fetch_stats(i, today), target_user)) for i in [7,30,1e1000]]
            embed=discord.Embed(title="G-Perdu - Statistiques individuelles", color=self.color)
            for element in stats:
                if element[1] is not None:
                    embed.add_field(
                        name="Classement "+element[0],
                        value='\n'.join(
                            [
                            "%s : %s a **perdu %s fois** %s à en moyenne **%s heures "
                            "d'intervalle.**" % (
                                ''.join([["\N{DIGIT ZERO}\N{COMBINING ENCLOSING KEYCAP}", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"][int(t)] for t in str(1+i+element[1][0])]),
                                user[0].mention,
                                user[1],
                                element[0],
                                round(user[2], 1)
                            ) for i, user in enumerate(element[1][1])
                            ]
                        )
                    )
            await response.edit(embed=embed)
        

    async def com_all(self, message, args, kwargs):
        if self.client.get_channel(self.channel) is None:
            await message.channel.send("Désolé ce module est indisponible")
            return
        async with message.channel.typing():
            embed_description = '\n'.join(
                [
                    "%s : %s a **perdu %s fois** depuis la création du salon à en moyenne **%s heures "
                    "d'intervalle.**" % (
                        ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i],
                        user[0].mention,
                        user[1],
                        round(user[2], 1)
                    ) for i, user in enumerate(list(await self.fetch_stats(1e1000, message.created_at))[:10:])
                ]
            )
            await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                           description=embed_description,
                                                           color=self.color))

    async def command(self, message, args, kwargs):
        if self.client.get_channel(self.channel) is None:
            await message.channel.send("Désolé ce module est indisponible")
            return
        if not message.mentions:
            async with message.channel.typing():
                number = 7
                try:
                    number = int(args[0])
                except ValueError:
                    pass
                stats = list(await self.fetch_stats(7, message.created_at))[:10:]
                if self.lost_role not in [role.id for role in stats[0][0].roles]:
                    for member in self.client.get_all_members():
                        if self.lost_role in [role.id for role in member.roles]:
                            await member.remove_roles(discord.utils.get(member.guild.roles, id=self.lost_role))
                    await stats[0][0].add_roles(discord.utils.get(stats[0][0].guild.roles, id=self.lost_role))
                stats = list(await self.fetch_stats(number, message.created_at))[:10:]
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
        else:
            await self.com_stats(message, args, kwargs)
                
