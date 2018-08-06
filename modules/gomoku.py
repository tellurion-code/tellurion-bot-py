#dummy module
import asyncio
import discord
from PIL import Image, ImageDraw, ImageFont
import io
import random
class MainClass():
    def saveObject(self, object, objectname):
        with open("storage/%s/"%moduleFiles + objectname + "tmp", "wb") as pickleFile:
            pickler = pickle.Pickler(pickleFile)
            pickler.dump(object)
        call(['mv', "storage/%s/"%moduleFiles + objectname + "tmp", "storage/%s/"%moduleFiles + objectname])
    def loadObject(self, objectname):
        if self.saveExists(objectname):
            with open("storage/%s/"%moduleFiles + objectname, "rb") as pickleFile:
                unpickler = pickle.Unpickler(pickleFile)
                return unpickler.load()

    def saveExists(self, objectname):
        return os.path.isfile("storage/%s/"%moduleFiles + objectname)
    def __init__(self, client, modules):
        self.client = client
        self.modules = modules
        self.events=['on_message'] #events list
        self.command="/gomoku" #command prefix (can be empty to catch every single messages)

        self.name="Gomoku"
        self.description="Module du jeu Gomoku"
        self.interactive=True
        self.color=0x000000
        self.help="""\
 Aucune fonction.
"""
    async def on_message(self, message):
        await message.channel.send(file=self.gen_img([['White' for i in range(15)] for i in range(15)]))

    def gen_img(self, grid):
        byteImgIO = io.BytesIO()
        img = Image.new('RGB', (640,640), color=(200,200,200))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("assets/DejaVuSerif-Bold.ttf", size=12)
        for i in range(16):
            draw.line((i*40,20) + (i*40,620), fill=(128,128,128))
        for i in range(16):
            draw.line((20,i*40) + (620,i*40), fill=(128,128,128))
        for i in range(1,16):
            draw.text((4, 40*i -6), str(i),font=font, fill=(255,0,0))
        lettres="ABCDEFGHIJKLMNO"
        for i in range(1,16):
            draw.text((40*i -4, 4), lettres[i-1],font=font, fill=(255,0,0))
        for Iline in range(len(grid)):
            for Icase in range(len(grid[Iline])):
                #print([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)])
                if grid[Iline][Icase]=='White':
                    draw.ellipse([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)], fill=(53,255,134))
                if grid[Iline][Icase]=='Black':
                    draw.ellipse([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)], fill=(10,10,10))
        tmpstr="/tmp/%s.png"%random.randint(1,10000000)
        img.save(tmpstr, "PNG")
        return discord.File(tmpstr)
