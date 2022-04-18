import sys
import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Pin"
    help = {
        "description": "Module gérant les messages épinglés",
        "commands": {
            "`{prefix}{command} <id>`": "Épingle ou retire l'épingle du message",
            "`{prefix}{command} pin <id>`": "Épingle le message",
            "`{prefix}{command} unpin <id>`": "retire l'épingle du message",
            "`{prefix}{command} toggle <id>`": "Épingle ou retire l'épingle du message"
        }
    }

    async def command(self, message, args, kwargs):
        if len(args) > 0:
            await self.try_toggle_pin(await message.channel.fetch_message(int(args[0])), message.author)

    async def com_pin(self, message, args, kwargs):
        if len(args) > 1:
            await self.try_pin(await message.channel.fetch_message(int(args[1])), message.author)

    async def com_unpin(self, message, args, kwargs):
        if len(args) > 1:
            await self.try_unpin(await message.channel.fetch_message(int(args[1])), message.author)

    async def com_toggle(self, message, args, kwargs):
        if len(args) > 1:
            await self.try_toggle_pin(await message.channel.fetch_message(int(args[1])), message.author)

    async def try_pin(self, message, user):
        try:
            await message.pin(reason=f"Épinglé par {user.display_name}")
            return True
        except discord.Forbidden:
            return False

    async def try_unpin(self, message, user):
        try:
            await message.unpin(reason=f"Désépinglé par {user.display_name}")
            return True
        except discord.Forbidden:
            return False

    async def try_toggle_pin(self, message, user):
        if message.pinned:
            return await self.try_unpin(message, user)
        else:
            return await self.try_pin(message, user)
