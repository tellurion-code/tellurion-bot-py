import asyncio
import collections
import os.path
import pickle
import random
import traceback
from subprocess import call

import discord

moduleFiles = "errors"


class MainClass:
    def save_object(self, object_instance, object_name):
        with open("storage/%s/" % moduleFiles + object_name + "tmp", "wb") as pickleFile:
            pickler = pickle.Pickler(pickleFile)
            pickler.dump(object_instance)
        call(['mv', "storage/%s/" % moduleFiles + object_name + "tmp", "storage/%s/" % moduleFiles + object_name])

    def load_object(self, objectname):
        if self.save_exists(objectname):
            with open("storage/%s/" % moduleFiles + objectname, "rb") as pickleFile:
                unpickler = pickle.Unpickler(pickleFile)
                return unpickler.load()

    def save_exists(self, objectname):
        return os.path.isfile("storage/%s/" % moduleFiles + objectname)

    def __init__(self, client, modules, owners, prefix):
        if not os.path.isdir("storage/%s" % moduleFiles):
            call(['mkdir', 'storage/%s' % moduleFiles])
        self.errorsDeque = None
        self.developpement_chan_id = [456142390726623243, 473637619310264330, 474267318332030987]
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
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_error', 'on_message', 'on_ready']  # events list
        self.command = "%slicorne" % self.prefix  # command prefix (can be empty to catch every single messages)

        self.name = "Error Handling"
        self.description = "Module de gestions des erreurs"
        self.interactive = True
        self.super_users_list = [431043517217898496]
        self.color = 0xdb1348
        self.help = """\
 </prefix>licorne
 => Crée une erreur.
"""

    async def on_ready(self):
        if self.save_exists('errorsDeque'):
            self.errorsDeque = self.load_object('errorsDeque')
        else:
            self.errorsDeque = collections.deque()
        for i in range(len(self.errorsDeque)):
            try:
                messagelst = self.errorsDeque.popleft()
                channel = self.client.get_channel(messagelst[0])
                delete_message = await channel.get_message(messagelst[1])
                await delete_message.delete()
            except:
                raise
        self.save_object(self.errorsDeque, 'errorsDeque')

    async def on_message(self, message):
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
        for chanid in self.developpement_chan_id:
            try:
                await self.client.get_channel(chanid).send(
                    embed=embed.set_footer(text="Ce message ne s'autodétruira pas.", icon_url=self.icon))
            except:
                pass
        self.save_object(self.errorsDeque, 'errorsDeque')
        await asyncio.sleep(60)
        try:
            channel = self.client.get_channel(message_list[0])
            delete_message = await channel.get_message(message_list[1])
            await delete_message.delete()
        except:
            raise
        finally:
            try:
                self.errorsDeque.remove(message_list)
            except ValueError:
                pass
        self.save_object(self.errorsDeque, 'errorsDeque')
