import asyncio
import random
import traceback

import discord
from discord import Message

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "errors"
    help = {
        "description": "Montre toutes les erreurs du bot dans discord.",
        "commands": {
            "`{prefix}{command}`": "Renvoie une erreur de test.",
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"dev_chan": [], "memes": [""], "icon": ""})
        self.errorsList = None

    async def on_load(self):
        if self.objects.save_exists('errorsList'):
            self.errorsList = self.objects.load_object('errorsList')
        else:
            self.errorsList = []

    async def on_ready(self):
        for i in range(len(self.errorsList)):
            try:
                msg_id = self.errorsList.pop(0)
                channel = self.client.get_channel(msg_id["channel_id"])
                to_delete = await channel.fetch_message(msg_id["msg_id"])
                await to_delete.delete()
            except:
                raise
        self.objects.save_object('errorsList', self.errorsList)

    async def command(self, message, args, kwargs):
        raise Exception("KERNEL PANIC!!!")

    async def on_error(self, event, *args, **kwargs):
        """Send error message"""
        # Search first channel instance found in arg, then search in kwargs
        channel = None
        for arg in args:
            if type(arg) == Message:
                channel = arg.channel
                break
            if type(arg) == discord.TextChannel:
                channel = arg
                break
        if channel is None:
            for _, v in kwargs.items():
                if type(v) == discord.Message:
                    channel = v.channel
                    break
                if type(v) == discord.TextChannel:
                    channel = v
                    break  # Create embed
        embed = discord.Embed(
            title="[Erreur] Aïe :/",
            description="```python\n{0}```".format(traceback.format_exc()),
            color=self.config.color)
        embed.set_image(url=random.choice(self.config.memes))
        message_list = None

        # Send message to dev channels
        for chanid in self.config.dev_chan:
            try:
                await self.client.get_channel(chanid).send(
                    embed=embed.set_footer(text="Ce message ne s'autodétruira pas.", icon_url=self.config.icon))
            except BaseException as e:
                raise e
        # Send message to current channel if exists
        if channel is not None:
            message = await channel.send(embed=embed.set_footer(text="Ce message va s'autodétruire dans une minute",
                                                                icon_url=self.config.icon))
            msg_id = {"channel_id": message.channel.id, "msg_id": message.id}
            self.errorsList.append(msg_id)
            # Save message in errorsList now to keep them if a reboot happend during next 60 seconds
            self.objects.save_object('errorsList', self.errorsList)

            # Wait 60 seconds and delete message
            await asyncio.sleep(60)
            try:
                channel = self.client.get_channel(msg_id["channel_id"])
                delete_message = await channel.fetch_message(msg_id["msg_id"])
                await delete_message.delete()
            except:
                raise
            finally:
                try:
                    self.errorsList.remove(msg_id)
                except ValueError:
                    pass
            # Save now to avoid deleting unkown message
            self.objects.save_object('errorsList', self.errorsList)
