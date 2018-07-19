#Secret Hitler is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License as in http://secrethitler.com/assets/Secret_Hitler_Rules.pdf
#Using some graphics from https://github.com/cozuya/secret-hitler/
import random
import discord

import settings.hitler
import utils.usertools

async def commandHandler(client, message, hitlerGame):
    
    if message.content == "/game join hitler":
        await hitlerGame.AddPlayer(client, message)
    elif message.content == "/game start hitler":
        await hitlerGame.StartGame(client, message)
    elif message.content == "/game players hitler":
        await client.send_message(message.channel,"```PYTHON\n{0}\n```".format(await hitlerGame.strUsers()))
    elif message.content == "/game reset hitler" :
        hitlerGame.__init__()
    if settings.hitler.debug :
        if message.content == "/hitler distribute" :
            await hitlerGame.Distribute()
        elif message.content.startswith("/hitler add"):
            args = message.content.split(" ")
            if len(args) == 3 :
                if await utils.usertools.UserByName(client, args[2]) is not False :
                    hitlerGame.playerlist.append(await utils.usertools.UserByName(client, args[2]))
                else :
                    await client.send_message(message.channel, message.author.mention + ", member not found.")
            else :
                await client.send_message(message.channel, message.author.mention + ", usage: `/hitler add <username>`")
        elif message.content == "/hitler sendroles" :
            await hitlerGame.SendRoles(client)
async def voteHandler(client, reaction, user, hitlerGame):
    if user is None :
        pass
    elif not (client.user == user) :
        if hitlerGame.state=="CC":
            if reaction.message.id == hitlerGame.CCm.id :
                if str(reaction.emoji) in hitlerGame.elist :
                    await hitlerGame.choseChancelier(client, reaction, user)
        elif hitlerGame.state=="CdV":
            for usergrp in hitlerGame.CdVm :
                if usergrp["message"].id == reaction.message.id :
                    if not usergrp["PID"] in hitlerGame.CdVd :
                        print("Yay, " + str(usergrp["PID"]) + " Et : " + str(reaction.emoji))
                        if reaction.emoji == "❌":
                            hitlerGame.CdVd.update({usergrp["PID"]: False})
                        elif reaction.emoji == "✅":
                            hitlerGame.CdVd.update({usergrp["PID"]: True})
                        if len(hitlerGame.CdVd) == len(hitlerGame.playerlist) - len(hitlerGame.deadlist) :
                            print(str(len(hitlerGame.CdVd)) + "   " + str(len(hitlerGame.playerlist) - len(hitlerGame.deadlist)))
                            forcount = 0
                            for i in range (len(hitlerGame.CdVd)) :
                                if hitlerGame.CdVd[i] == True:
                                    forcount += 1
                            print(forcount)
                            print(len(hitlerGame.playerlist) - len(hitlerGame.deadlist))
                            #TODO Send vote results to every single player.
class HitlerSave :
    def __init__(self):
        self.playerlist=[]
        self.deadlist=[]
        self.started=False
        self.fascists=[]
        self.liberals=[]
        self.hitler=""
        self.turn=0
        self.state="ND" # states : ND = Not Defined ; CC = Choosing chancelier ; CdV = Choosed, Voting ; 
        self.CCm=None #message du chancelier
        self.elist=[]
        self.CdC=None
        self.CdVm=[]
        self.CdVd={} #La liste des votes par id
    async def addVote(self, client, reaction, user):
        pass
    async def choseChancelier(self, client, reaction, user) :
        if user == self.playerlist[self.turn] :
            for i in range(10):
                if str(reaction.emoji) == ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i]:
                    self.CdC=i
                    self.state = "CdV"
                    for i2 in range(len(self.playerlist)) :
                        m=None
                        if self.playerlist[i2] in self.liberals :
                            m = await client.send_message(self.playerlist[i2], embed=await self.CreateEmbed(True, ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][self.turn] + self.playerlist[self.turn].name + '#' + self.playerlist[self.turn].discriminator + " a choisi " + ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][self.CdC] + self.playerlist[self.CdC].name + '#' + self.playerlist[self.CdC].discriminator + " pour être chancelier.", "Stimme ja ✅ oder nein ❌.\n(Votez oui ou non)"))
                        elif self.playerlist[i2] in self.fascists :
                            m = await client.send_message(self.playerlist[i2], embed=await self.CreateEmbed(False, ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][self.turn] + self.playerlist[self.turn].name + '#' + self.playerlist[self.turn].discriminator + " a choisi " + ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][self.CdC] + self.playerlist[self.CdC].name + '#' + self.playerlist[self.CdC].discriminator + " pour être chancelier.", "Stimme ja ✅ oder nein ❌.\n(Votez oui ou non)"))
                        listemote=["✅", "❌"]
                        if not (self.playerlist[i2] in self.deadlist) :
                            for emote in listemote :
                                await client.add_reaction(m, emote)
                            self.CdVm.append({"PID":i2, 'message':m})
                            
    async def startTurn(self, client) :
        self.state = "CC"
        self.elist=[]
        for i in range(len(self.playerlist)) :
            if i == self.turn :
                plist="\n"
                for i2 in range(len(self.playerlist)) :
                    if not (self.playerlist[i2] in self.deadlist) :
                        if not (i2 == i) :
                            listemote=["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
                            plist+= listemote[i2] + " " + self.playerlist[i2].name + '#' + self.playerlist[i2].discriminator + "\n"
                            self.elist.append(listemote[i2])
                m = None
                if self.playerlist[i] in self.liberals :
                    self.CCm = await client.send_message(self.playerlist[i], embed=await self.CreateEmbed(True, "Vous êtes le président.", "Vous devez choisir le chancelier.\n Voici la liste des joueurs ainsi que leur numéros :\n" + plist + "\n\nFaites attention, en votant, c'est votre première réaction qui sera prise en compte, aucun retour n'est possible."))
                elif self.playerlist[i] in self.fascists :
                    self.CCm = await client.send_message(self.playerlist[i], embed=await self.CreateEmbed(False, "Vous êtes le président.", "Vous devez choisir le chancelier.\n Voici la liste des joueurs ainsi que leur numéros :\n" + plist + "\n\nFaites attention, en votant, c'est votre première réaction qui sera prise en compte, aucun retour n'est possible." ))
                for i2 in range(len(self.playerlist)) :
                    if not (self.playerlist[i2] in self.deadlist) :
                        if not (i2 == i) :
                            listemote=["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
                            await client.add_reaction(self.CCm, listemote[i2])
            else :
                if self.playerlist[i] in self.liberals :
                    await client.send_message(self.playerlist[i], embed=await self.CreateEmbed(True, self.playerlist[self.turn].name + '#' + self.playerlist[self.turn].discriminator + " est le président.", "Il va choisir le chancelier."))
                elif self.playerlist[i] in self.fascists :
                    await client.send_message(self.playerlist[i], embed=await self.CreateEmbed(False, self.playerlist[self.turn].name + '#' + self.playerlist[self.turn].discriminator + " est le président.", "Il va choisir le chancelier."))
    async def nextPresident(self) :
        self.turn += 1
        if self.turn >= len(self.playerlist) :
            self.turn = 0
        if playerlist[self.turn] in self.deadlist :
            await self.nextPresident()
    async def CreateEmbed(self, liberal, Title, Description, Image=None) :
        if liberal :
            color=0x0cc2f9
            iconurl="https://github.com/cozuya/secret-hitler/raw/master/public/images/emotes/LibBird.png"
        else : 
            color=0xd11717
            iconurl="https://github.com/cozuya/secret-hitler/raw/master/public/images/emotes/FasSnake.png"
        embed = discord.Embed(title=Title, description=Description, color=color)
        embed.set_footer(text="Secret Hitler", icon_url=iconurl)
        if not Image == None :
            embed.set_image(url=Image)
        return embed
    async def isPlaying(self, cmember):
        for member in self.playerlist :
            if member.id == cmember.id :
                return True
        return False
    async def isFascist(self, cmember):
        for member in self.fascists:
            if member.id == cmember.id :
                return True
        return False
    async def isLiberal(self, cmember):
        for member in self.liberals :
            if member.id == cmember.id :
                return True
        return False
    async def isHitler(self, cmember):
        if cmember.id == self.hitler.id :
            return True
        else : 
            return False
    async def strUsers(self):
        retlist="Joueurs [secret-hitler] :\n\n"
        for member in self.playerlist:
            retlist += (member.name + '#' + member.discriminator + '\n')
        return retlist
    
    async def AddPlayer(self, client, message):
        if not self.started :
            if len(self.playerlist) >= 10 :
                await client.send_message(message.channel, message.author.mention + ", la partie est pleine. Vous ne pouvez pas rejoindre.")
            elif await self.isPlaying(message.author) :
                await client.send_message(message.channel, message.author.mention + ", Vous êtes déjà dans la partie.")
            else :
                self.playerlist.append(message.author)
                await client.send_message(message.channel,"```PYTHON\n{0}\n```".format(await self.strUsers()))
        else :
            await client.send_message(message.channel, message.author.mention + ", Vous ne pouvez pas rejoindre une partie en cours.")
        pass
    
    async def SendRoles(self, client) :
        for member in self.liberals :
            await client.send_message(member, embed=await self.CreateEmbed(True, "Vous êtes un libéral.", "Vous êtes contre les vilains fascistes.", random.choice(settings.hitler.liberalImage)))
        for member in self.fascists :
            fasclist="```PYTHON\n"
            for fag in self.fascists :
                fasclist += (fag.name + '#' + fag.discriminator + '\n')
            fasclist += "```"
            if await self.isHitler(member) :
                await client.send_message(member, embed=await self.CreateEmbed(False, "Vous êtes Hitler", "Vous êtes contre les libéraux.\nSont fascistes : " + fasclist, settings.hitler.hitlerImage))
            else : 
                await client.send_message(member, embed=await self.CreateEmbed(False, "Vous êtes un fasciste.", "Vous êtes contre les libéraux. \nSont fascistes : " + fasclist + "\nHitler est : " + self.hitler.name + "#" + self.hitler.discriminator, random.choice(settings.hitler.fascistImage) ))
    async def StartGame(self, client, message):
        if not self.started :
            if len(self.playerlist) >= 5 and len(self.playerlist) <= 10 :
                self.started = True
                await self.Distribute()
                await self.SendRoles(client)
                await self.startTurn(client)
            else :
                await client.send_message(message.channel, message.author.mention + ", secret-hitler se joue de 5 à 10 joueurs")
        else :
            await client.send_message(message.channel, message.author.mention + ", La partie a déjà commencé.")

    async def Distribute(self): #Should only be called within StartGame;
        self.fascists=[]
        self.liberals=[]
        tmpl = random.sample(self.playerlist, len(self.playerlist))
        for i in range(len(tmpl)) :
            if len(tmpl) == 5 or len(tmpl) == 6:
                if i < 2 :
                    self.fascists.append(tmpl[i])
                else:
                    self.liberals.append(tmpl[i])
            if len(tmpl) == 7 or len(tmpl) == 8:
                if i < 3 :
                    self.fascists.append(tmpl[i])
                else:
                    self.liberals.append(tmpl[i])
            if len(tmpl) == 9 or len(tmpl) == 10:
                if i < 4 :
                    self.fascists.append(tmpl[i])
                else:
                    self.liberals.append(tmpl[i])
        self.hitler=random.choice(self.fascists)
