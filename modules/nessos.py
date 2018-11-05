import time
import random
import discord

import settings.nessos
import utils.usertools
import utils.perms

async def commandHandler(client, message, nessos):

    if message.content == "/nessos start" and not nessos.state:
        if len(nessos.players)>=4 and len(nessos.players)<=6 or settings.nessos.debug:
            random.seed(time.time())
            
            deck = ['0']*14 + ['1']*4 + ['2']*4 + ['3']*4 + ['4']*4 + ['5']*4 + ['7']*4 + ['8']*4 + ['9']*4 + ['10']*4
            if len(nessos.players) > 4:
                deck += ['0'] + ['6']*4
            nessos.deck=random.sample(deck, len(deck))

            nessos.points = 30 + 5*(6 - len(nessos.players))

            for i in range(len(nessos.players)):
                nessos.players[i].hand.append(nessos.deck[:5])
                nessos.deck = nessos.deck[5:]

            nessos.leader=random.randint(0,len(nessos.actors)-1)
            nessos.fromPLayer = nessos.leader
            nessos.channel=message.channel
            for player in nessos.players :
                await client.send_message(player.member, "\n\n\n\n\n")
            await nessos.start(client)
        else:
            await client.send_message(message.channel, message.author.mention + ", La partie nécessite entre 4 et 6 joueurs pour être lancée...")

    elif message.content == "/nessos join" and not nessos.state:
        if not message.author.id in [player.member.id for player in nessos.players]:
            nessos.players.append(Player(message.author))
            await client.send_message(message.channel, message.author.mention + " a rejoint la partie !")
        else:
            await client.send_message(message.channel, message.author.mention + ", vous êtes déjà dans la partie.")

    elif message.content == "/nessos quit" and not nessos.state:
        if message.author.id in [player.member.id for player in nessos.players]:
            for player in nessos.players:
                if player.member.id == message.author.id:
                    nessos.players.remove(player)
            await client.send_message(message.channel, message.author.mention + " a quitté la partie.")
        else:
            await client.send_message(message.channel, message.author.mention + ", vous n'êtes pas dans la partie.")

    elif message.content.startswith("/nessos kick") and not nessos.state:
        args=message.content.split(' ')
        if len(args)==3:
            for id in args[2].split(','):
                user=None
                try :
                    user=await utils.usertools.UserByID(client, id)
                except:
                    pass
                if user:
                    if user.id in [player.member.id for player in nessos.players]:
                        for player in nessos.players:
                            if player.member.id == user.id:
                                nessos.players.remove(player)
                        await client.send_message(message.channel, message.author.mention + ", `{0}` a bien été retiré de la liste des participants.".format(user.display_name))
                    else:
                        await client.send_message(message.channel, message.author.mention + ", `{0}` n'a pas rejoint la partie.".format(user.display_name))
                else:
                    await client.send_message(message.channel, message.author.mention + ", `{0}` n'est pas un id valide.".format(id))

    elif message.content == "/nessos players":
        players=[]
        for player in nessos.players :
            players.append(player.member.display_name)
        await client.send_message(message.channel, "Liste des joueurs ({0}):\n```PYTHON\n{1}\n```".format(len(players),players))

    elif message.content == "/nessos reset" and await utils.perms.hasrole(message.author, "1"):
        nessos.__init__()
        await client.send_message(message.channel, message.author.mention + "La partie a été réinitialisée.")

    elif message.content == "/nessos help":
            aidestr="Commandes générales :\n\n"
            aidestr+="    /nessos help \n=> Affiche ce message d'aide\n\n"
            aidestr+="    /nessos join \n=> Vous ajoute dans la liste des joueurs de la prochaine partie\n\n"
            aidestr+="    /nessos quit \n=> Vous retire de la liste des joueurs de la prochaine partie\n\n"
            aidestr+="    /nessos players \n=> Affiche la liste des joueurs ayant rejoint\n\n"
            aidestr+="    /nessos kick <userid> \n=> Retire le joueur spécifié de la liste de joueurs\n\n"
            aidestr+="    /nessos start \n=> Lance la partie de Nessos\n\n"
            await client.send_message(message.channel, embed=discord.Embed(title='[NESSOS] - Aide', description=aidestr, color=0xFFFFFF))

    elif message.content == "/nessos debug" and message.channel == nessos.channel:
        client.send_message(message.channel, embed=discord.Embed(title='[NESSOS] - Aide', description=str(nessos), color=0xFFFFFF))

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
                    nessos.state = 'card'
                    nessos.selectCard(nessos.fromPLayer)
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
                        nessos.state = 'value'
                        nessos.selectValue()
                    else:
                        nessos.state = 'choice'
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
                    nessos.state = 'choice'
                    nessos.selectChoice()
        if nessos.state == 'choice':
            if reaction.message.id == nessos.SHMessage.id :
                if str(reaction.emoji) in nessos.SHList:
                    if action =='add':
                        nessos.SHChosen.append(str(reaction.emoji))
                    elif action =='remove':
                        nessos.SHChosen.remove(str(reaction.emoji))
                    if len(nessos.SHChosen) == 1 and not (len(nessos.offer) == 3 and nessos.SHChosen[0] == '➕'):
                        await client.add_reaction(nessos.SHMessage, nessos.validator)
                if str(reaction.emoji) == nessos.validator and action=='add' and len(nessos.SHChosen) == 1:
                    if nessos.SHChosen[0] == '✅':
                        nessos.accept()
                    elif nessos.SHChosen[0] == '❎':
                        nessos.refuse()
                    elif nessos.SHChosen[0] == '➕' and len(nessos.offer) < 3:
                        nessos.overbid()


class Player:

    def __init__(self, member):
        self.member = member  # Discord member object
        self.hand = []  # List of card in the hand of the player
        self.board = []  # List of card on the board of the player
        self.chirons = 0  # Number of "Chiron" cards on the board of the player

class Nessos:

    def __init__(self):
        self.emotes = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]  # Emotes used for selection
        self.validator = ['⭕'] # Emote used for validation
        self.cards = ['Chiron', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature', 'Créature']  # Will be use later
        self.players = []  # List of all alive players
        self.deadPlayers =[]  # List of all deads players
        self.targets = []  # List of all targetable players
        self.firstPlayer = 0  # Id of the first Player of the turn
        self.fromPlayer = 0  # Id of the current Player
        self.toPlayer = 0  # Id of the targeted Player
        self.deck = []  # List of all remaining cards
        self.offer = []  # List of offered cards
        self.offerValues = []  # List of offered values
        self.points = 0  # Minimum points to win
        self.channel = None  # Channel where recap will be display
        self.state = None  # State of the game [target selection|card selection|value selection|choice]
        self.SPMessage = None  # SelectPlayerMessage
        self.SPList = []  # SelectPlayerList
        self.SPChosen = []  # SelectPlayerChosen
        self.SCMessage = None  # SelectCardMessage / Id of the message
        self.SCList = []  # SelectCardList / List of reaction for selection
        self.SCChosen = []  # SelectCardChosen / List of selected reaction
        self.SVMessage = None  # SelectValueMessage / Id of the message
        self.SVList = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]  # SelectValueList / List of reaction for selection
        self.SVChosen = []  # SelectValueChosen / List of selected reaction
        self.SHMessage = None  # SelectChoiceMessage / Id of the message
        self.SHList = ['✅', '❎', '➕']  # SelectChoiceList / List of reaction for selection
        self.SHChosen = []  # SelectChoiceChosen / List of selected reaction

    async def start(client):
        pass

    async def turn(client):
        pass

    async def recap(client):
        playersstr = ""
        for i in range(len(players)):
            sets = min([player.board.count(1), player.board.count(2), player.board.count(3)])
            playersstr += " {0} `{1}`\n".format(self.emotes[i], self.players[i].member.display_name + '#' + str(self.players[i].member.discriminator))
            playersstr += "    Points : {0}\n".format(str(self.players[i].board))
            playersstr += "    **Total  : {0}**\n".format(str(sum(self.players[i].board) + sets * 10))
            playersstr += "    Chiron : {0}\n\n".format(str(self.players[i].chirons))

        await client.send_message(
            self.channel, 
            embed=discord.Embed(title="[NESSOS] - Récap"), 
            description="Liste des joueurs :\n\n{0}".format(playersstr), 
            color=0xFFFFFF)

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
        self.draw(self.fromPLayer)

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
        playersstr = ""
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
        cardsstr = ""
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
            embed=discord.Embed(title="[NESSOS] - Choix de l'action"), 
            description="Veuillez choisir votre action en sélectionnant la réaction correspondante puis validez.", 
            color=0xFFFFFF)
        
        for emote in self.SHList :
            await client.add_reaction(self.SHMessage, emote)
        if len(nessos.offer) == 3:
            await client.remove_reaction(self.SHMessage, '➕')

    async def checkDeath(self, player):
        if self.players[player].chirons >= 3:
            self.deadPlayers.append(self.players.pop(player))

    async def checkEnd(self):
        if len(players) == 1:
            self.end(player)
        if sum([p.chirons for p in self.players] + [p.chirons for p in self.deadPlayers]) >= 9:
            self.end()
        for player in self.players:
            sets = min([player.board.count(1), player.board.count(2), player.board.count(3)])
            if (sum(player.board) + sets * 10) >= self.points:
                self.end(player)

    async def end(self, player=None):
        self.SHMessage = await client.send_message(
            self.players[self.toPlayer], 
            embed=discord.Embed(title="[NESSOS] - Fin de la partie"), 
            description="A coder.", 
            color=0xFFFFFF)

