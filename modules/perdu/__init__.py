import datetime

import discord

import utils.emojis
from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Perdu"
    help = {
        "description": "Module donnant les statistiques sur les perdants",
        "commands": {
            "`{prefix}{command}`": "Donne le classement des perdants de la semaine",
            "`{prefix}{command} all`": "Donne le classement des perdants depuis toujours",
            "`{prefix}{command} <nombre de jours>`": "Donne le classement des perdants sur la durée spécifiée",
            "`{prefix}{command} stats [@mention]`": "Donne les statistiques d'un perdant",
        }
    }
    help_active = True
    command_text = "perdu"
    color = 0xff6ba6

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"channel": 0, "lost_role": 0, "min_delta": datetime.timedelta(minutes=30).total_seconds()})

    async def on_load(self):
        if self.objects.save_exists('history'):
            self.history = self.objects.load_object('history')
        else:
            self.history = {}

    async def on_message(self, message: discord.Message):
        # Fill history
        if message.channel.id == self.config.channel:
            if message.author.id not in self.history.keys():
                # Add new user if not found
                self.history.update(
                    {message.author.id: ([(message.created_at, datetime.timedelta(seconds=0)), ])}
                )
            else:
                # Update user and precompute timedelta
                delta = message.created_at - self.history[message.author.id][-1][0]
                if delta.total_seconds() >= self.config.min_delta:
                    self.history[message.author.id].append((message.created_at, delta))
            self.objects.save_object("history", self.history)
        await self.parse_command(message)

    async def fill_history(self):
        self.history = {}
        async for message in self.client.get_channel(self.config.channel).history(limit=None):
            if message.author.id not in self.history.keys():
                # Add new user if not found
                self.history.update({message.author.id: ([(message.created_at, datetime.timedelta(seconds=0)), ])})
            else:
                # Update user and precompute timedelta
                delta = self.history[message.author.id][-1][0] - message.created_at
                if delta.total_seconds() >= self.config.min_delta:
                    self.history[message.author.id].append((message.created_at, delta))
        self.objects.save_object("history", self.history)

    def get_top(self, top=10, since=datetime.datetime(year=1, month=1, day=1)):
        """Return [(userid, [(date, delta), (date,delta), ...]), ... ]"""
        # Extract only messages after until
        messages = []
        for user in self.history.keys():
            if self.history[user][-1][0] > since:
                messages.append((user, [message for message in self.history[user] if message[0] > since]))
        messages.sort(key=lambda x: len(x[1]), reverse=True)
        # Extract top-ten
        messages = messages[:min(top, len(messages))]
        return messages

    async def com_fill(self, message: discord.Message, args, kwargs):
        if await self.auth(message.author):
            async with message.channel.typing():
                await self.fill_history()
            await message.channel.send("Fait.")

    async def com_all(self, message: discord.Message, args, kwargs):
        # Get all stats
        top = self.get_top()
        embed_description = "\n".join(
            f"{utils.emojis.write_with_number(i)} : <@{top[i][0]}> a **perdu {len(top[i][1])} fois** depuis la"
            f" création du salon à en moyenne **{sum(list(zip(*top[i][1]))[1], datetime.timedelta(0)) / len(top[i][1])} heures d'intervalle.**"
            for i in range(len(top))
        )[:2000]
        await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                       description=embed_description,
                                                       color=self.color))

    async def com_stats(self, message: discord.Message, args, kwargs):
        pass

    async def command(self, message, args, kwargs):
        if message.mentions:
            await self.com_stats(message, args, kwargs)
        since = datetime.datetime.now() - datetime.timedelta(days=7)
        if args[0]:
            try:
                since = datetime.datetime.now() - datetime.timedelta(days=float(args[0]))
            except ValueError:
                pass
        top = self.get_top(10, since)
        embed_description = "\n".join(
            f"{utils.emojis.write_with_number(i)} : <@{top[i][0]}> a **perdu {len(top[i][1])} fois** depuis la"
            f" création du salon à en moyenne **{sum(list(zip(*top[i][1]))[1], datetime.timedelta(0)) / len(top[i][1])} heures d'intervalle.**"
            for i in range(len(top))
        )[:2000]
        await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores",
                                                       description=embed_description,
                                                       color=self.color))
