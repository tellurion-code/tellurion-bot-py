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
        self.save=None # format : { 'currently_playing':[id,id,id], 'player_game':{id:gameid} 'games':{gameid:{'White':id,'Black':id, 'hist':['h8','h9']}}}
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
 
 /gomoku spectate <@mention>
 => Permet d'observer la partie d'un joueur en jeu
 
 /gomoku leave
 => Quitte la partie en cours
 
 <coordonnées>
 => Joue aux coordonnées spécifiées si c'est votre tour et que les coordonnées sont valides
 
"""

    async def on_ready(self):
        if self.save==None:
            if self.saveExists('save'):
                self.save=self.loadObject('save')
            else:
                self.save={'currently_playing':[], 'player_game':{}, 'games':{}}
            self.saveObject(self.save, 'save')
        for gameid in self.save['games'].keys() :
            self.save['games'][gameid]['lock']=False
    async def send_reactions(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)
    async def on_message(self, message):
        if self.save==None:
            await self.on_ready()
        else:
            if message.content.startswith('/gomoku'):
                args=message.content.split()
                if len(args)>1 and args[1]=='challenge' and not len(message.mentions)==0:
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
                                white=[message.author, message.mentions[0]][[message.author, message.mentions[0]].index(black)-1]
                                self.save['games'].update({gameid:{'lock':False, 'specs':[], 'Black':black.id, 'White':white.id, 'hist':[]}})
                                self.save['player_game'].update({message.author.id:gameid, message.mentions[0].id:gameid})
                                async def send_messages(condition, messagestr, imgfile):
                                    for user in condition:
                                        await user.send(messagestr, file=imgfile)
                                asyncio.ensure_future(send_messages([self.client.get_user(id) for id in [self.save['games'][gameid][color] for color in ['Black','White']]+ self.save['games'][gameid]['specs']], "C'est à %s de commencer"%black.mention, self.gen_img_from_hist(self.save['games'][gameid]['hist'])), loop=self.client.loop)
                            else:
                                await message.channel.send(message.author.mention + ", vous êtes déjà dans une partie, finissez celle là pour commencer. ^^")
                        else:
                            await message.channel.send(message.author.mention + ", le joueur mentionné est déjà en train de jouer...")
                    except KeyError:
                        pass
                elif len(args)>1 and args[1]=='spectate' and not len(message.mentions)==0:
                    try:
                        if message.mentions[0].id in self.save['currently_playing']:
                            gameid = self.save['player_game'][message.mentions[0].id]
                            if not message.mentions[0].id in self.save['games'][gameid]['specs']:
                                self.save['games'][gameid]['specs'].append(message.mentions[0].id)
                                await message.author.send("Vous observez maintenant une partie.", file=self.gen_img_from_hist(self.save['games'][gameid]['hist']))
                            else:
                                await message.channel.send(message.author.mention + ", vous êtes déjà en train d'observer cette partie...")
                        else:
                            await message.channel.send(message.author.mention + ", le joueur mentionné n'est pas dans une partie...")
                    except KeyError:
                        pass
                elif len(args)==2 and args[1]=='leave':
                    if message.author.id in self.save['currently_playing']:
                        gameid=self.save['player_game'][message.author.id]
                        for playerid in [self.save['games'][gameid][color] for color in ['White', 'Black']]:
                            self.save['currently_playing'].remove(playerid)
                            del self.save['player_game'][playerid]
                            await self.client.get_user(playerid).send("La partie de Gomoku a été annulée.")
                        del self.save['games'][gameid]
                    else:
                        await message.channel.send("%s, vous n'êtes pas dans une partie de Gomoku"%message.author.mention)
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
                        if test and not self.save['games'][gameid]['lock']:
                            self.save['games'][gameid]['lock']=True
                            testmessage = await message.author.send(file=self.gen_img_from_hist(self.save['games'][gameid]['hist'] + [test], test=True))
                            asyncio.ensure_future(self.send_reactions(testmessage, ['✅','❌']), loop=self.client.loop)
                            def check(reaction, user):
                                return reaction.message.id == testmessage.id and user.id == message.author.id and str(reaction.emoji) in ['✅','❌']
                            reaction, _ = await self.client.wait_for('reaction_add', check=check)
                            if str(reaction.emoji)=='✅':
                                await testmessage.delete()
                                self.save['games'][gameid]['hist'].append(test)
                                self.save['games'][gameid]['lock']=False
                                res=self.gen_grid_from_hist(self.save['games'][gameid]['hist'], fin=True)
                                if any(res):
                                    messagestr="%s a gagné, bravo à cette personne !"%self.client.get_user(self.save['games'][gameid][['Black','White'][res.index(True)]]).mention
                                else:
                                    messagestr="C'est au tour de %s !"%(self.client.get_user(self.save['games'][gameid]['White'] if self.save['games'][gameid]['Black']==message.author.id else self.save['games'][gameid]['Black']).mention)
                                imgfile=self.gen_img_from_hist(self.save['games'][gameid]['hist'])
                                async def send_messages(condition, messagestr, imgfile):
                                    for user in condition:
                                        await user.send(messagestr, file=imgfile)
                                asyncio.ensure_future(send_messages([self.client.get_user(id) for id in [self.save['games'][gameid][color] for color in ['Black','White']] + self.save['games'][gameid]['specs']], messagestr, imgfile), loop=self.client.loop)
                                if any(res):
                                    for playerid in [self.save['games'][gameid][color] for color in ['White', 'Black']]:
                                        self.save['currently_playing'].remove(playerid)
                                        del self.save['player_game'][playerid]
                                    del self.save['games'][gameid]
                            if str(reaction.emoji)=='❌':
                                self.save['games'][gameid]['lock']=False
                                await testmessage.delete()
                            self.saveObject(self.save, 'save')
                except KeyError:
                    raise
    def is_win(self, grid, coords=None):
        def isWin(row,check):
            if row[check]!=None:
                for i in range(len(row)):
                    if row[i]==row[check]:
                        if i<=check and i+5>check:
                            if row[i:i+5].count(row[check])>=5:
                                return True
            return False
        def check_coords(Iline, Icase, grid):
            hor=grid[Iline]
            ver=[grid[i][Icase] for i in range(len(grid))]
            diag1=[[Iline-min(Iline,Icase) +i, Icase-min(Iline,Icase) +i]for i in range(15-max(Iline-min(Iline,Icase), Icase-min(Iline,Icase)))]
            diag2=[[Iline-min(Iline,14-Icase)+i, Icase+min(Iline,14-Icase)-i] for i in range(min(15-(Iline-min(Iline,14-Icase)), 15-(14-(Icase+min(Iline,14-Icase)))))]
            return isWin(hor, Icase) or isWin(ver, Iline) or isWin([grid[coords[0]][coords[1]] for coords in diag1], diag1.index([Iline,Icase])) or isWin([grid[coords[0]][coords[1]] for coords in diag2], diag2.index([Iline,Icase]))
        if coords==None:
            for Iline in range(len(grid)):
                for Icase in range(len(grid[Iline])):
                    if check_coords(Iline, Icase, grid):
                        return check_coords(Iline, Icase, grid)
        else:
            Icase,Iline=coords
            return check_coords(Iline, Icase, grid)
        return False
    def gen_img_from_hist(self, hist, test=False):
        return self.gen_img(self.gen_grid_from_hist(hist), test=test)
    def gen_grid_from_hist(self, hist, fin=False):
        grid=[[None for i in range(15)] for i in range(15)]
        i=0
        finalturn=None
        for turn in hist:
            if i%2==0:
                grid[turn[1]][turn[0]]='Black'
            else:
                grid[turn[1]][turn[0]]='White'
            finalturn=turn
            i+=1
        cpgrid=cpgrid=[row.copy() for row in grid]
        i=0
        for turn in hist:
            if self.is_win(cpgrid, coords=turn):
                grid[turn[1]][turn[0]]+='W'
            finalturn=turn
            i+=1
        if finalturn:
            grid[finalturn[1]][finalturn[0]]+='L'
        if not fin:
            return grid
        if fin:
            bwin=any([any([True if 'BlackW' == case else False for case in row]) for row in grid])
            wwin=any([any([True if 'WhiteW' == case else False for case in row]) for row in grid])
            return (bwin,wwin)
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
    def gen_img(self, grid, test=False, m=1):
        img=None
        if test:
            img = Image.new('RGBA', (640*m,640*m), color=(255,200,200,255))
        else:
            img = Image.new('RGBA', (640*m,640*m), color=(200,200,200,255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("assets/Hack-Bold.ttf", size=12*m)
        for i in range(16):
            draw.line((i*40*m,20*m) + (i*40*m,620*m), fill=(128,128,128,255), width=m-1)
        for i in range(16):
            draw.line((20*m,i*40*m) + (620*m,i*40*m), fill=(128,128,128,255), width=m-1)
        draw.ellipse([((7 +1)*40*m -6*m ,(7 +1) * 40*m - 6*m),((7 +1)*40*m + 6*m ,(7 +1) * 40*m + 6*m)], fill=(128,128,128,255))
        for i in range(1,16):
            draw.text((4*m, m*40*i -6*m), str(i),font=font, fill=(255,0,0,255))
        lettres="ABCDEFGHIJKLMNO"
        for i in range(1,16):
            draw.text((m*40*i -4*m, 4*m), lettres[i-1],font=font, fill=(255,0,0,255))
        for Iline in range(len(grid)):
            for Icase in range(len(grid[Iline])):
                #print([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)])
                if grid[Iline][Icase] != None :
                    if 'L' in grid[Iline][Icase][5:]:
                        draw.ellipse([((Icase +1)*40*m -17*m ,(Iline +1) * 40*m - 17*m),((Icase +1)*40*m + 17*m ,(Iline +1) * 40*m + 17*m)], fill=(54,122,57,255))
                    if grid[Iline][Icase].startswith('White'):
                        draw.ellipse([((Icase +1)*40*m -13*m ,(Iline +1) * 40*m - 13*m),((Icase +1)*40*m + 13*m ,(Iline +1) * 40*m + 13*m)], fill=(12,96,153,255))
                    if grid[Iline][Icase].startswith('Black'):
                        draw.ellipse([((Icase +1)*40*m -13*m ,(Iline +1) * 40*m - 13*m),((Icase +1)*40*m + 13*m ,(Iline +1) * 40*m + 13*m)], fill=(10,10,10,255))
                    if 'W' in grid[Iline][Icase][5:]:
                        draw.ellipse([((Icase +1)*40*m -4*m ,(Iline +1) * 40*m - 4*m),((Icase +1)*40*m + 4*m ,(Iline +1) * 40*m + 4*m)], fill=(194,45,48,255))
                else:
                    if [Iline,Icase]==[7,7]:
                        draw.text(((Icase +1)*40*m +5*m ,(Iline +1) * 40*m +5*m), lettres[Icase] + str(Iline +1), font=font, fill=(128,128,128,255))
                    else:
                        draw.text(((Icase +1)*40*m +1*m ,(Iline +1) * 40*m -1*m), lettres[Icase] + str(Iline +1), font=font, fill=(128,128,128,255))
        tmpstr="/tmp/%s.png"%random.randint(1,10000000)
        img.save(tmpstr, "PNG")
        return discord.File(tmpstr)
