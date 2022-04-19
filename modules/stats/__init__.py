import sys
import discord
import asyncio
import datetime
import utils.emojis
import humanize
import matplotlib.pyplot as plt
import time

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Stats"
    help = {
        "description": "Module gérant les statistiques",
        "commands": {
            "`{prefix}{command} [options]`": "Calcule les statistiques du serveur",
            "`Options:`": "",
            "`-c | --channel`": "Ne traite que le salon courant",
            "`-s <jours> | --since <jours>`": "Ne traite que les <jours> derniers jours"
                }
        }

    def __init__(self, client):
        super().__init__(client)
        self.history = {"global": {}, "channel": {}}
        self.lock = asyncio.Lock()

    async def on_ready(self):
        await self.fill_history()

    def fill_message(self, message):
        # Create user in global dict
        if message.author.id not in self.history["global"].keys():
            self.history["global"].update({message.author.id: []})
        # Create channel in channel dict
        if message.channel.id not in self.history["channel"].keys():
            self.history["channel"].update({message.channel.id: {message.author.id: []}})

        # Create user in channel specific dict
        if message.author.id not in self.history["channel"][message.channel.id].keys():
            self.history["channel"][message.channel.id].update({message.author.id: []})

        self.history["global"][message.author.id].append(message.created_at)
        self.history["channel"][message.channel.id][message.author.id].append(message.created_at)


    async def on_message(self, message: discord.Message):
        asyncio.ensure_future(self.parse_command(message))
        # Fill history
        if message.author.bot:
            return
        async with self.lock:
            self.fill_message(message)

    async def fill_history(self):
        async with self.lock:
            self.history = {"global": {}, "channel": {}}
            for channel in self.client.get_guild(self.client.config.main_guild).channels:
                if isinstance(channel, discord.TextChannel):
                    async for message in channel.history(limit=None):
                        self.fill_message(message)
            # Sort global dict
            for user in self.history["global"].keys():
                self.history["global"][user].sort(key=lambda x: x)
            # Sort chan specific dict
            for chan in self.history["channel"].keys():
                for user in self.history["channel"][chan].keys():
                    self.history["channel"][chan][user].sort(key=lambda x: x)


    def get_top(self, top=10, since=datetime.datetime(year=1, month=1, day=1), channel=None, with_user=None, only_users=None):
        """Return [(userid, [date, date, ...]), ... ]"""
        # Extract only messages after until
        source_dict = self.history["global"]
        if channel is not None:
            source_dict = self.history["channel"][channel]
        if only_users is not None:
            # Extract data for only_users
            messages = []
            for user in only_users:
                try:
                    if source_dict[user][-1] >= since:
                        messages.append((user, [message for message in source_dict[user] if message > since]))
                except KeyError:
                    pass
            # messages.sort(key=lambda x: len(x[1]), reverse=True)
            return messages
        if with_user is None:
            with_user = []
        # Extract TOP top users, and with_users data
        messages = []
        for user in source_dict.keys():
            if source_dict[user][-1] >= since:
                messages.append((user, [message for message in source_dict[user] if message > since]))
        # messages.sort(key=lambda x: len(x[1]), reverse=True)
        # Extract top-ten
        saved_messages = messages[:min(top, len(messages))]
        # Add with_user
        saved_messages.extend([message for message in messages if message in with_user])
        return saved_messages

    async def com_fill(self, message: discord.Message, args, kwargs):
        if self.auth(message.author):
            async with message.channel.typing():
                await self.fill_history()
            await message.channel.send("Fait.")

    async def com_all(self, message: discord.Message, args, kwargs):
        # Get all stats
        top = self.get_top()
        # intervales = [sum(list(zip(*top[i][1]))[1], datetime.timedelta(0)) / len(top[i][1]) for i in range(len(top))]
        embed_description = "\n".join(
            f"{utils.emojis.write_with_number(i)} : <@{top[i][0]}> a **perdu {len(top[i][1])} fois** depuis la"
            f" création du salon à en moyenne **"
            # f"{(str(intervales[i].days) + ' jours et' if intervales[i].days else '')} "
            # f"{str(int(intervales[i].total_seconds() % (24 * 3600) // 3600)) + ':' if intervales[i].total_seconds() > 3600 else ''}"
            # f"{int((intervales[i].total_seconds() % 3600) // 60)} "
            # f"{'heures' if intervales[i].total_seconds() > 3600 else 'minutes'} d'intervalle.**"
            for i in range(len(top))
        )[:2000]
        await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                       description=embed_description,
                                                       color=self.config.color))

    async def com_stats(self, message: discord.Message, args, kwargs):
        # TODO: Finir sum
        async with message.channel.typing():
            if "sum" in args:
                if message.mentions:
                    top = self.get_top(only_users=[mention.id for mention in message.mentions] + [message.author.id])
                else:
                    # TOP 5 + auteur
                    top = self.get_top(top=5, with_user=[message.author.id])
                dates = []
                new_top = {}
                for t in top:
                    for date, _ in t[1]:
                        dates.append(date)
                dates.sort()
                dates.append(datetime.datetime.today() + datetime.timedelta(days=1))
                for t in top:
                    user = t[0]
                    new_top.update({user: ([dates[0]], [0])})
                    i = 0
                    for date, _ in t[1]:
                        while date < dates[i]:
                            new_top[user][0].append(dates[i])
                            new_top[user][1].append(new_top[user][1][-1])
                            i += 1
                        new_top[user][0].append(date)
                        new_top[user][1].append(new_top[user][1][-1] + 1)

                to_plot = [t[1][1:] for t in new_top.values()]
                plt.xlabel("Temps", fontsize=30)
                plt.ylabel("Score", fontsize=30)
                plt.title("Évolution du nombre de perdu au cours du temps.", fontsize=40)
                plt.legend()
                file_name = f"/tmp/{time.time()}.png"
                plt.savefig(file_name, bbox_inches='tight')
                await message.channel.send(file=discord.File(file_name))

            if "history" in args:
                since = datetime.datetime(year=1, month=1, day=1)
                debut_message = "la création du salon"
                top = 5
                if "s" in [k[0] for k in kwargs]:
                    try:
                        d = [k[1] for k in kwargs if k[0] == "s"][0]
                        since = datetime.datetime.now() - datetime.timedelta(days=float(d))
                        debut_message = humanize.naturalday(since.date(), format='le %d %b')
                    except ValueError:
                        pass
                if "t" in [k[0] for k in kwargs]:
                    try:
                        top = int([k[1] for k in kwargs if k[0] == "t"][0])
                    except ValueError:
                        pass
                # Si mention, alors uniquement les mentions
                if message.mentions:
                    top = self.get_top(since=since,
                                    only_users=[mention.id for mention in message.mentions])
                else:
                    # TOP 5 + auteur
                    top = self.get_top(since=since, top=top, with_user=[message.author.id])
                new_top = {}
                for t in top:
                    c = 0
                    counts = []
                    dates = []
                    for date, _ in t[1]:
                        c += 1
                        counts.append(c)
                        dates.append(date)
                    new_top.update({t[0]: (dates, counts)})
                plt.figure(num=None, figsize=(25, 15), dpi=120, facecolor='w', edgecolor='k')
                for user, (dates, counts) in new_top.items():
                    plt.plot_date(dates, counts, linestyle='-', label=str(self.client.get_user(user).name))
                plt.xlabel("Temps", fontsize=30)
                plt.ylabel("Score", fontsize=30)
                plt.legend(fontsize=20)
                plt.title(f"Évolution du nombre de perdu au cours du temps depuis {debut_message}.", fontsize=35)
                file_name = f"/tmp/{time.time()}.png"
                plt.savefig(file_name, bbox_inches='tight')
                await message.channel.send(file=discord.File(file_name))

    async def command(self, message, args, kwargs):
        if message.mentions:
            await self.com_stats(message, args, kwargs)
        since = datetime.datetime.now() - datetime.timedelta(days=7)
        if len(args):
            try:
                since = datetime.datetime.now() - datetime.timedelta(days=float(args[0]))
            except ValueError:
                pass
        tkwargs = {}
        if 'channel' in map(lambda x: x[0], kwargs):
            tkwargs.update({'channel': message.channel.id})
        top = self.get_top(10, since)
        # intervales = [sum(list(zip(*top[i][1]))[1], datetime.timedelta(0)) / len(top[i][1]) for i in range(len(top))]
        embed_description = "\n".join(
            f"{utils.emojis.write_with_number(i)} : <@{top[i][0]}> a **perdu {len(top[i][1])} fois** depuis "
            f"{humanize.naturalday(since.date(), format='le %d %b')} à en moyenne **"
            # f"{(str(intervales[i].days) + ' jours et' if intervales[i].days else '')} "
            # f"{str(int(intervales[i].total_seconds() % (24 * 3600) // 3600)) + ':' if intervales[i].total_seconds() > 3600 else ''}"
            # f"{int((intervales[i].total_seconds() % 3600) // 60)} "
            # f"{'heures' if intervales[i].total_seconds() > 3600 else 'minutes'} d'intervalle.**"
            for i in range(len(top))
        )[:2000]
        await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                       description=embed_description,
                                                       color=self.config.color))

