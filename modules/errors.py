import asyncio
import collections
import random
import traceback

import discord

from modules.base import BaseClass

moduleFiles = "errors"


class MainClass(BaseClass):
    name = "Error Handling"
    description = "Module de gestions des erreurs"
    interactive = True
    authorized_roles = [431043517217898496]
    color = 0xdb1348
    help = {
        "description": "Module gérant les erreurs",
        "commands": {
            "`{prefix}{command}`": "Retourne une erreur",
        }
    }
    command_text = "licorne"

    def __init__(self, client):
        super().__init__(client)
        self.errorsDeque = None
        self.development_chan_id = [456142390726623243, 473637619310264330, 474267318332030987]
        self.memes = [
            "https://cdn.discordapp.com/attachments/430408983283761152/430433931272126465/Bruce_3.png",
            "https://cdn.discordapp.com/attachments/430408983283761152/430431622521946123/LUNE.jpg",
            "https://cdn.discordapp.com/attachments/326742676672086018/431570139016724480/27th3c.png",
            "https://cdn.discordapp.com/attachments/326742676672086018/431570538868244492/27th8d.png",
            "https://cdn.discordapp.com/attachments/326742676672086018/431570620942123009/lemdpc3.png",
            "https://cdn.discordapp.com/attachments/326742676672086018/431570838026846208/telecharge_15.jpg",
            "https://cdn.discordapp.com/attachments/326742676672086018/431571174078808070/telecharge_16.jpg",
            "https://cdn.discordapp.com/attachments/326742676672086018/431571655115145217/unknown.png",
            "https://cdn.discordapp.com/attachments/326742676672086018/431574206518525963/Bruce_troll_QHwYz39nj7i.png",
            "https://cdn.discordapp.com/attachments/326742676672086018/431572693910028289/telecharge_19.jpg"
            "https://cdn.discordapp.com/attachments/434475794631360512/447168326582665241/2akl04.jpg",
            "https://cdn.discordapp.com/attachments/434475794631360512/447168125067067394/20180519_004620.png",
            "https://cdn.discordapp.com/attachments/434475794631360512/446441679868788736/Sans_titre_0.png",
            "https://cdn.discordapp.com/attachments/434475794631360512/446441465611026443/unknown.png",
            "https://cdn.discordapp.com/attachments/297868535076749323/445789702373638164/image.png",
            "https://cdn.discordapp.com/attachments/297868535076749323/297875363160129540/unknown.png",
            "https://cdn.discordapp.com/attachments/326742316456869888/447887603664945163/unknown.png",
            "https://cdn.discordapp.com/attachments/434475794631360512/460876662414901249/TeslaPLS.png",
            "https://cdn.discordapp.com/attachments/297868535076749323/587687801844269169/C-658VsXoAo3ovC.jpg"
        ]
        self.icon = "https://cdn.discordapp.com/attachments/340620490009739265/431569015664803840/photo.png"
    async def get_message(self, channel, message_id) :
        async for message in channel.history(limit=None):
            if message_id==message.id :
                return message
        return None

    async def on_ready(self):
        if self.save_exists('errorsDeque'):
            self.errorsDeque = self.load_object('errorsDeque')
        else:
            self.errorsDeque = collections.deque()
        if self.errorsDeque is not None:
            for i in range(len(self.errorsDeque)):
                try:
                    messagelst = self.errorsDeque.popleft()
                    channel = self.client.get_channel(messagelst[0])
                    delete_message = await self.get_message(channel, messagelst[1])
                    if delete_message is not None :
                        await delete_message.delete()
                except:
                    raise
        else:
            self.errorsDeque = collections.deque()
        self.save_object(self.errorsDeque, 'errorsDeque')

    async def command(self, message, args, kwargs):
        5 / 0

    async def on_error(self, event, *args, **kwargs):
        embed = discord.Embed(title="Aïe :/", description="```PYTHON\n{0}```".format(traceback.format_exc()),
                              color=self.color).set_image(url=random.choice(self.memes))
        message_list = None
        try:
            message = await args[0].channel.send(
                embed=embed.set_footer(text="Ce message s'autodétruira dans une minute.", icon_url=self.icon))
            message_list = [message.channel.id, message.id]
            self.errorsDeque.append(message_list)
        except:
            try:
                message = args[1].channel.send(
                    embed=embed.set_footer(text="Ce message s'autodétruira dans une minute.", icon_url=self.icon))
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
            if message_list is not None:
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
