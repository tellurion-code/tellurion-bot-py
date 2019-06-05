import asyncio
import random
import traceback

import collections
import discord

from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "errors"
    description = "Error handling"
    interactive = True
    super_users_list = [431043517217898496]
    color = 0xdb1348
    help = {
        "description": "Montre toutes les erreurs du bot dans discord.",
        "commands": {
            "`{prefix}{command}`": "Renvoie une erreur de test.",
        }
    }
    command_text = "unicorn"

    def __init__(self, client):
        super().__init__(client)
        self.errorsDeque = None
        self.development_chan_id = []
        self.memes = [
            "",
        ]
        self.icon = ""

    async def on_ready(self):
        if self.save_exists('errorsDeque'):
            self.errorsDeque = self.load_object('errorsDeque')
        else:
            self.errorsDeque = collections.deque()
        for i in range(len(self.errorsDeque)):
            try:
                messagelst = self.errorsDeque.popleft()
                channel = self.client.get_channel(messagelst[0])
                delete_message = await channel.fetch_message(messagelst[1])
                await delete_message.delete()
            except:
                raise
        self.save_object(self.errorsDeque, 'errorsDeque')

    async def command(self, message, args, kwargs):
        raise Exception("Si cette erreur apparait, alors tout est normal")

    async def on_error(self, event, *args, **kwargs):
        embed = discord.Embed(title="Aïe :/", description="```PYTHON\n{0}```".format(traceback.format_exc()),
                              color=self.color).set_image(url=random.choice(self.memes))
        message_list = None
        try:
            message = await args[0].channel.send(
                embed=embed.set_footer(text="Ce message va s'autodétruire dans une minute.", icon_url=self.icon))
            message_list = [message.channel.id, message.id]
            self.errorsDeque.append(message_list)
        except:
            try:
                message = args[1].channel.send(
                    embed=embed.set_footer(text="Ce message va s'autodétruire dans une minute.", icon_url=self.icon))
                message_list = [message.channel.id, message.id]
                self.errorsDeque.append(message_list)
            except:
                pass
        for chanid in self.development_chan_id:
            try:
                await self.client.get_channel(chanid).send(
                    embed=embed.set_footer(text="Ce message ne s'autodétruira pas.", icon_url=self.icon))
            except:
                pass
        self.save_object(self.errorsDeque, 'errorsDeque')
        await asyncio.sleep(60)
        try:
            channel = self.client.get_channel(message_list[0])
            delete_message = await channel.fetch_message(message_list[1])
            await delete_message.delete()
        except:
            raise
        finally:
            try:
                self.errorsDeque.remove(message_list)
            except ValueError:
                pass
        self.save_object(self.errorsDeque, 'errorsDeque')
