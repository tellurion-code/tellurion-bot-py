#dummy module
import asyncio
import discord
from PIL import Image, ImageDraw, ImageFont
import io
import random
import os
from subprocess import call
import pickle
moduleFiles="gomoku"
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
    def __init__(self, client, modules, owners):
        if not os.path.isdir("storage/%s"%moduleFiles):
            call(['mkdir', 'storage/%s'%moduleFiles])
        self.save=None # format : { 'currently_playing':[id,id,id], 'player_game':{id:gameid} 'games':{gameid:{'White':id,'hist':['h8','h9']}}}
        self.client = client
        self.modules = modules
        self.owners = owners
        self.events=['on_message', 'on_ready'] #events list
        self.command="" #command prefix (can be empty to catch every single messages)

        self.name="Gomoku"
        self.description="Module du jeu Gomoku"
        self.interactive=True
        self.color=0xffff00
        self.help="""\
 /gomoku challenge <@mention>
 => Défie le joueur mentionné pour une partie de Gomoku

 <coordonnées>
 => joue aux coordonnées spécifié si c'est votre tour et que les coordonnées sont valides
 
"""

    async def on_ready(self):
        if self.saveExists('save'):
            self.save=self.loadObject('save')
        else:
            self.save={'currently_playing':[], 'player_game':{}, 'games':{}}
        self.saveObject(self.save, 'save')
    async def send_reactions(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)
    async def on_message(self, message):
        if self.save!=None:
            if message.content.startswith('/gomoku'):
                args=message.content.split()
                if len(args)>1 and args[1]=='challenge':
                    try:
                        if not message.mentions[0].id in self.save['currently_playing']:
                            if not message.author.id in self.save['currently_playing']:
                                self.save['currently_playing'] += [message.author.id, message.mentions[0].id]
                                gameid=0
                                while True:
                                    try:
                                        self.save['games'][gameid]
                                        gameid+=1
                                    except:
                                        break
                                black=random.choice([message.author, message.mentions[0]])
                                self.save['games'].update({gameid:{'Black':black.id, 'hist':[]}})
                                self.save['player_game'].update({message.author.id:gameid, message.mentions[0].id:gameid})
                                await message.channel.send("C'est à %s de commencer"%black.mention, file=self.gen_img_from_hist(self.save['games'][gameid]['hist']))
                            else:
                                await message.channel.send(message.author.mention + ", vous êtes déjà dans une partie, finissez celle là pour commencer. ^^")
                        else:
                            await message.channel.send(message.author.mention + ", le joueur mentionné est déjà en train de jouer...")
                    except KeyError:
                        pass
                else:
                    await self.modules['help'][1].send_help(message.channel, self)
            elif message.author.id in self.save['currently_playing']:
                try:
                    gameid = self.save['player_game'][message.author.id]
                    test=None
                    if self.save['games'][gameid]['Black']==message.author.id:
                        test=len(self.save['games'][gameid]['hist'])%2==0
                    else:
                        test=len(self.save['games'][gameid]['hist'])%2!=0
                    if test:
                        test=self.get_valid_coords(message.content, self.save['games'][gameid]['hist'])
                        if test:
                            testmessage = await message.channel.send(file=self.gen_img_from_hist(self.save['games'][gameid]['hist'] + [test], test=True))
                            asyncio.ensure_future(self.send_reactions(testmessage, ['✅','❌']), loop=self.client.loop)
                            def check(reaction, user):
                                print(reaction.emoji)
                                return reaction.message.id == testmessage.id and user.id == message.author.id and str(reaction.emoji) in ['✅','❌']
                            print("ah")
                            reaction, _ = await self.client.wait_for('reaction_add', check=check)
                            print(reaction.emoji)
                            if str(reaction.emoji)=='✅':
                                await testmessage.delete()
                                self.save['games'][gameid]['hist'].append(test)
                                await message.channel.send(file=self.gen_img_from_hist(self.save['games'][gameid]['hist']))
                            if str(reaction.emoji)=='❌':
                                await testmessage.delete()
                except:
                    raise
    def gen_img_from_hist(self, hist, test=False):
        grid=[[None for i in range(15)] for i in range(15)]
        i=0
        for turn in hist:
            if i%2==0:
                grid[turn[1]][turn[0]]='Black'
            else:
                grid[turn[1]][turn[0]]='White'
            i+=1
        return self.gen_img(grid, test=test)
    def get_valid_coords(self, coordsin, hist):
        try:
            coords=coordsin.upper()
            coordlist=[]
            if coords[0] in "ABCDEFGHIJKLMNO":
                coordlist.append("ABCDEFGHIJKLMNO".index(coords[0]))
            else :
                return False
            if 0<int(coords[1:])<16 :
                coordlist.append(int(coords[1:])-1)
            else:
                return False
            if not coordlist in hist:
                return coordlist
            else:
                return False
        except:
            return False
    def gen_img(self, grid, test=False):
        img=None
        if test:
            img = Image.new('RGB', (640,640), color=(255,200,200))
        else:
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
