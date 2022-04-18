import sys
import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Pin"
    help = {
        "description": "Module gérant les messages épinglés",
        "commands": {
            "📌": "Ajoutez la réaction à un de vos messages pour l'épingler",
            "`{prefix}{command}`": "Épingle ou retire l'épingle du message auquel vous répondez",
            "`{prefix}{command} <id>`": "Épingle ou retire l'épingle du message dont l'id est spécifié",
            "`{prefix}{command} pin`": "Épingle le message auquel vous répondez",
            "`{prefix}{command} pin <id>`": "Épingle le message dont l'id est spécifié",
            "`{prefix}{command} unpin`": "retire l'épingle du message auquel vous répondez",
            "`{prefix}{command} unpin <id>`": "retire l'épingle du message dont l'id est spécifié",
            "`{prefix}{command} toggle`": "Épingle ou retire l'épingle auquel vous répondez",
            "`{prefix}{command} toggle <id>`": "Épingle ou retire l'épingle du message"
        }
    }

    async def command(self, message, args, kwargs):
        if len(args) > 0:
            await self.try_toggle_pin(await message.channel.fetch_message(int(args[0])), message.author)
        else:
            await self.try_toggle_pin(message.reference.resolved, message.author)

    async def com_pin(self, message, args, kwargs):
        if len(args) > 1:
            await self.try_pin(await message.channel.fetch_message(int(args[1])), message.author)
        else:
            await self.try_pin(message.reference.resolved, message.author)

    async def com_unpin(self, message, args, kwargs):
        if len(args) > 1:
            await self.try_unpin(await message.channel.fetch_message(int(args[1])), message.author)
        else:
            await self.try_unpin(message.reference.resolved, message.author)

    async def com_toggle(self, message, args, kwargs):
        if len(args) > 1:
            await self.try_toggle_pin(await message.channel.fetch_message(int(args[1])), message.author)
        else:
            await self.try_toggle_pin(message.reference.resolved, message.author)

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

    async def on_raw_reaction_add(self, payload):
        channel_id, message_id, user_id = payload.channel_id, payload.message_id, payload.user_id
        message = await self.get_message(channel_id, message_id)
        if (message.author.id == user_id) and (payload.emoji.name == "📌") and self.auth(message.author):
            await self.try_pin(message, message.author)

    async def on_raw_reaction_remove(self, payload):
        channel_id, message_id, user_id = payload.channel_id, payload.message_id, payload.user_id
        message = await self.get_message(channel_id, message_id)
        if (message.author.id == user_id) and (payload.emoji.name == "📌") and self.auth(message.author):
            await self.try_unpin(message, message.author)

    #async def on_reaction_add(self, reaction, user):
        #if (reaction.message.author.id == user.id) and (reaction.emoji == "📌") and self.auth(message.author):
            #await self.try_pin(reaction.message, user)

    #async def on_reaction_remove(self, reaction, user):
        #if (reaction.message.author.id == user.id) and (reaction.emoji == "📌") and self.auth(message.author):
            #await self.try_unpin(reaction.message, user)

    async def get_message(self, channel_id, message_id):
        return await self.client.get_channel(channel_id).fetch_message(message_id)
