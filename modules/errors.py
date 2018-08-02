import asyncio
import traceback
import discord
import random
class MainClass():
    def __init__(self, client, modules, saves):
        self.devchanids=[456142390726623243, 473637619310264330, 474267318332030987]
        self.memes=[
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
        "https://cdn.discordapp.com/attachments/434475794631360512/447168326582665241/2akl04.jpg",
        "https://cdn.discordapp.com/attachments/434475794631360512/447168125067067394/20180519_004620.png",
        "https://cdn.discordapp.com/attachments/434475794631360512/446441679868788736/Sans_titre_0.png",
        "https://cdn.discordapp.com/attachments/434475794631360512/446441465611026443/unknown.png",
        "https://cdn.discordapp.com/attachments/297868535076749323/445789702373638164/image.png",
        "https://cdn.discordapp.com/attachments/297868535076749323/297875363160129540/unknown.png",
        "https://cdn.discordapp.com/attachments/326742316456869888/447887603664945163/unknown.png",
        "https://cdn.discordapp.com/attachments/434475794631360512/460876662414901249/TeslaPLS.png"
        ]
        self.icon="https://cdn.discordapp.com/attachments/340620490009739265/431569015664803840/photo.png"
        self.client = client
        self.modules = modules
        self.saves = saves
        self.events=['on_error', 'on_message'] #events list
        self.command="/licorne" #command prefix (can be empty to catch every single messages)

        self.name="Error Handling"
        self.description="Module de gestions des erreurs"
        self.interactive=True
        self.color=0xdb1348
        self.help="""\
 /licorne
 => Crée une erreur.
"""
    async def on_message(self, message):
        5/0
    async def on_error(self, event, *args, **kwargs):
        embed = discord.Embed(title="Aïe :/", description="```PYTHON\n{0}```".format(traceback.format_exc()), color=self.color).set_image(url=random.choice(self.memes))
        messagelist=[]
        try:
            messagelist.append(await args[0].channel.send(embed=embed.set_footer(text="Ce message s'autodétruira dans une minute.", icon_url=self.icon)))
        except:
            try:
                messagelist.append(args[1].channel.send(embed=embed.set_footer(text="Ce message s'autodétruira dans une minute.", icon_url=self.icon)))
            except:
                pass
        for chanid in self.devchanids:
            try:
                await self.client.get_channel(chanid).send(embed=embed.set_footer(text="Ce message ne s'autodétruira pas.", icon_url=self.icon))
            except:
                pass
        await asyncio.sleep(60)
        for messagetodelete in messagelist:
            await messagetodelete.delete()
