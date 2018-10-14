import time
import random
import discord

import settings.nessos
import utils.usertools
import utils.perms

async def commandHandler(client, message, nessos):

    if message.content == "/nessos start":
        await start(client, message, nessos)

    elif message.content == "/nessos join":
        await join(client, message, nessos)

    elif message.content == "/nessos quit":
        await quit(client, message, nessos)

    elif message.content.startswith("/nessos kick"):
        await kick(client, message, nessos)

    elif message.content == "/nessos players":
        await players(client, message, nessos)

    elif message.content == "/nessos reset":
        await reset(client, message, nessos)

    elif message.content == "/nessos help":
        await help(client, message)

    elif message.content == "/nessos debug":
        await debug(client, message, nessos)

async def reactionHandler(client, reaction, user, nessos, action):
    if not user==client.user:
        if nessos.state == 'player':
            if reaction.message.id == nessos.SPMessage.id :
                if str(reaction.emoji) in nessos.SPList:
                    if action =='add':
                        nessos.SPChosen.append(str(reaction.emoji))
                    elif action =='remove':
                        nessos.SPChosen.remove(str(reaction.emoji))
                    if len(nessos.SPChosen) == 1:
                        await client.add_reaction(nessos.SPMessage, nessos.validator)
                if str(reaction.emoji) == nessos.validator and action=='add' and len(nessos.SPChosen) == 1:
                    nessos.toPlayer = nessos.emotes.index(str(nessos.SPChosen[0]))
        if nessos.state == 'card':
            if reaction.message.id == nessos.SCMessage.id :
                if str(reaction.emoji) in nessos.SCList:
                    if action =='add':
                        nessos.SCChosen.append(str(reaction.emoji))
                    elif action =='remove':
                        nessos.SCChosen.remove(str(reaction.emoji))
                    if len(nessos.SCChosen) == 1:
                        await client.add_reaction(nessos.SCMessage, nessos.validator)
                if str(reaction.emoji) == nessos.validator and action=='add' and len(nessos.SCChosen) == 1:
                    card = nessos.players[nessos.fromPLayer].hand[nessos.SCList.index(str(nessos.SCChosen[0]))]
                    if card == 0:
                        nessos.selectValue()
                    else:
                        nessos.offer(card, card)
        if nessos.state == 'value':
            if reaction.message.id == nessos.SVMessage.id :
                if str(reaction.emoji) in nessos.SVList:
                    if action =='add':
                        nessos.SVChosen.append(str(reaction.emoji))
                    elif action =='remove':
                        nessos.SVChosen.remove(str(reaction.emoji))
                    if len(nessos.SVChosen) == 1:
                        await client.add_reaction(nessos.SVMessage, nessos.validator)
                if str(reaction.emoji) == nessos.validator and action=='add' and len(nessos.SVChosen) == 1:
                    nessos.offer(0, nessos.SVList.index(str(nessos.SVChosen[0]))+1)
        if nessos.state == 'choice':
            if reaction.message.id == nessos.SHMessage.id :
                if str(reaction.emoji) in nessos.SHList:
                    if action =='add':
                        nessos.SHChosen.append(str(reaction.emoji))
                    elif action =='remove':
                        nessos.SHChosen.remove(str(reaction.emoji))
                    if len(nessos.SHChosen) == 1:
                        await client.add_reaction(nessos.SHMessage, nessos.validator)
                if str(reaction.emoji) == nessos.validator and action=='add' and len(nessos.SHChosen) == 1:
                    if nessos.SHChosen[0] == '':
                        nessos.accept()
                    elif nessos.SHChosen[0] == '':
                        nessos.refuse()
                    elif nessos.SHChosen[0] == '':
                        nessos.overbid()


class Player:

    def __init__(self, member):
        self.member = member
        self.hand = []
        self.board = []
        self.chirons = 0

class Nessos:

    def __init__(self):
        self.emotes = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
        self.validator = ['⭕']
        self.cards = ['Chiron', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature']
        self.players = []
        self.deadPlayers =[]
        self.targets = []
        self.firstPlayer = 0
        self.actualPlayer = 0
        self.toPlayer = 0
        self.deck = []
        self.offer = []
        self.offerValues = []
        self.points = 0
        self.channel = None
        self.state = None
        self.SPMessage = None
        self.SPList = []
        self.SPChosen = []
        self.SCMessage = None
        self.SCList = []
        self.SCChosen = []
        self.SVMessage = None
        self.SVList = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
        self.SVChosen = []
        self.SHMessage = None
        self.SHList = ['✅', '❎', '➕']
        self.SHChosen = []

    async def nextLeader(self):
        self.firstPlayer += 1
        if self.firstPlayer == len(self.players):
            self.firstPlayer=0
        self.targets = self.players[:self.firstPlayer] + self.players[self.firstPlayer+1:]

    async def draw(self, player):
        player.hand.append(self.deck.pop())

    async def offer(self, card, value):
        self.offer.append(card)
        self.offerValues.append(value)

    async def accept(self):
        self.players[toPlayer].board += self.offer
        self.players[toPlayer].chirons += self.offer.count(0)
        self.offer = []
        self.checkDeath(toPlayer)

    async def refuse(self):
        self.players[fromPLayer].board += self.offer
        self.players[fromPlayer].chirons += self.offer.count(0)
        self.offer = []
        self.checkDeath(fromPlayer)

    async def overbid(self):
        self.fromPLayer = self.toPlayer
        self.selectPlayer()
        self.selectCard(self.fromPLayer)

    async def selectPlayer(self):
        playersstr=""
        for i in range(len(self.players)):
            if not i in [self.firstPlayer, self.fromPLayer, self.toPlayer]:
                playersstr += " {0} `{1}`\n".format(self.emotes[i], self.players[i].member.display_name + '#' + str(self.players[i].member.discriminator))
        
        self.SPMessage = await client.send_message(
            self.players[self.toPlayer], 
            embed=discord.Embed(title="[NESSOS] - Choix du joueur"), 
            description="Veuillez choisir le joueur cible en sélectionnant la réaction correspondante puis validez.\n\nListe des joueurs :\n{0}".format(playersstr), 
            color=0xFFFFFF)
        
        for i in range(len(self.players)):
            if not i in [self.firstPlayer, self.fromPLayer, self.toPlayer]:
                self.SPList.append(self.emotes[i])
                await client.add_reaction(self.SPMessage, self.emotes[i])

    async def selectCard(self, player):
        cardsstr=""
        for i in range(len(player.hand)):
            cardsstr += " {0} `{1}`\n".format(self.emotes[i], self.cards[player.hand[i]] + ' (' + str(player.hand[i]) + ')')
        
        self.SCMessage = await client.send_message(
            self.players[self.toPlayer], 
            embed=discord.Embed(title="[NESSOS] - Choix de la carte"), 
            description="Veuillez choisir la carte a offrir en sélectionnant la réaction correspondante puis validez.\n\nListe des joueurs :\n{0}".format(cardsstr), 
            color=0xFFFFFF)
        
        for i in range(len(player.hand)):
            self.SCList.append(self.emotes[i])
            await client.add_reaction(self.SCMessage, self.emotes[i])

    async def selectValue(self):
        self.SVMessage = await client.send_message(
            self.players[self.toPlayer], 
            embed=discord.Embed(title="[NESSOS] - Choix de la valeur"), 
            description="Veuillez choisir la valeur à annoncer en sélectionnant la réaction correspondante puis validez.", 
            color=0xFFFFFF)
        
        for emote in self.SVList:
            await client.add_reaction(self.SVMessage, emote)

    async def selectChoice(self):
        self.SHMessage = await client.send_message(
            self.players[self.toPlayer], 
            embed=discord.Embed(title="[NESSOS] - Choix de la valeur"), 
            description="Veuillez choisir la valeur à annoncer en sélectionnant la réaction correspondante puis validez.", 
            color=0xFFFFFF)
        
        for emote in self.SHList :
            await client.add_reaction(self.SHMessage, emote)

    async def checkDeath(self, player):
        if self.players[player].chirons >= 3:
            self.deadPlayers.append(self.players.pop(player))

    async def checkEnd(self):
        if sum([p.chirons for p in self.players] + [p.chirons for p in self.deadPlayers]) >= 9:
            self.end(0)
        for player in self.players:
            sets = min([player.board.count(1), player.board.count(2), player.board.count(3)])
            if (sum(player.board) + sets * 10) >= self.points:
                self.end(1)

    async def end(self, one):
        pass

