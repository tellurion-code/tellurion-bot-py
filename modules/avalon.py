import utils.usertools
import random
import discord
async def commandHandler(client, message, avalonGame):
    if message.content.startswith('/avalon'):

#     -lobby commands-
        if avalonGame.state=='lobby':
    #     -Join command-
            if message.content=='/avalon join':
                if not message.author in avalonGame.players:
                    if not len(avalonGame.players)>=10:
                        avalonGame.players.append(message.author)
                        await client.send_message(message.channel, message.author.mention + " a rejoint la partie.")
                    else:
                        await client.send_message(message.channel, message.author.mention + ", la partie est complète..")
                else:
                    await client.send_message(message.channel, message.author.mention + ", vous êtes déjà dans la partie..")

    #     -Quit command-
            if message.content=='/avalon quit':
                if message.author in avalonGame.players :
                    avalonGame.players.remove(message.author)
                    await client.send_message(message.channel, message.author.mention + " a quitté la partie.")
                else:
                    await client.send_message(message.channel, message.author.mention + ", vous n'êtes pas dans la partie..")

    #     -Player list command :
            if message.content=='/avalon players list':
                players=[]
                for user in avalonGame.players :
                    players.append(user.display_name)
                await client.send_message(message.channel, "Liste des joueurs :\n```PYTHON\n{0}```".format(players))

    #     -Kick player command :
            if message.content.startswith('/avalon players kick'):
                args=message.content.split(' ')
                if len(args)==4:
                    ans=""
                    for id in args[3].split(','):
                        user=None
                        try :
                            user=await utils.usertools.UserByID(client, id)
                        except:
                            pass
                        if user:
                            if user in avalonGame.players:
                                avalonGame.players.remove(user)
                                await client.send_message(message.channel, message.author.mention + ", `{0}` a bien été retiré de la liste des participants.".format(user.display_name))
                            else:
                                await client.send_message(message.channel, message.author.mention + ", `{0}` n'a pas rejoint la partie..".format(user.display_name))
                        else:
                            await client.send_message(message.channel, message.author.mention + ", `{0}` n'est pas un id valide..".format(id))

    #     -Roles list command-
            if message.content=='/avalon roles list':
                await client.send_message(message.channel, "Liste des roles :\n```PYTHON\n{0}```".format(str(avalonGame.roles)))

    #     -Add Role command-
            if message.content.startswith('/avalon roles add'):
                args=message.content.split(' ')
                if len(args)==4:
                    ans=""
                    for role in args[3].split(','):
                        if role in avalonGame.implemented_roles :
                            avalonGame.roles.append(role)
                            ans += "le rôle {0} a été ajouté\n".format(role)
                        else:
                            ans += "Le rôle {0} n'est pas supporté, veuillez en prendre un parmis `{1}`.\n".format(role, str(avalonGame.implemented_roles))
                    await client.send_message(message.channel, message.author.mention + ",\n{0}".format(ans))
                else:
                    await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique role ou une liste de roles séparés par une virgule.")

    #     -Remove role command-
            if message.content.startswith('/avalon roles remove'):
                args=message.content.split(' ')
                if len(args)==4:
                    ans=""
                    for role in args[3].split(','):
                        if role in avalonGame.implemented_roles :
                            avalonGame.roles.remove(role)
                            ans += "Le rôle {0} a été retiré\n".format(role)
                        else:
                            ans += "Le rôle {0} n'est pas supporté, veuillez en prendre un parmis `{1}`.".format(role, str(avalonGame.implemented_roles))
                    await client.send_message(message.channel, message.author.mention + ",\n{0}".format(ans))
                else:
                    await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique role ou une liste de roles séparés par une virgule.")

    #     -Start game command-
            if message.content=='/avalon start' :
                if len(avalonGame.players)>=5:
                    if len(avalonGame.roles) == len(avalonGame.players) :
                        avalonGame.state='composition'
                        randplayers=random.sample(avalonGame.players, len(avalonGame.players))
                        randroles=random.sample(avalonGame.roles, len(avalonGame.roles))
                        for i in range(len(randplayers)):
                            avalonGame.actors.append({'user':randplayers[i], 'role':randroles[i]})
                        avalonGame.leader=random.randint(0,len(avalonGame.actors)-1)
                        await avalonGame.startGame(client)
                    else:
                        await client.send_message(message.channel, message.author.mention + ", le nombre de roles est différent du nombre de joueurs.. :/")
                else:
                    await client.send_message(message.channel, message.author.mention + ", la partie ne peut-être lancée qu'avec 5 joueurs au minimum..")

class AvalonSave:
    def __init__(self):
        self.emotes=["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
        self.implemented_roles=['gentil', 'mechant', 'merlin', 'perceval', 'morgane', 'assassin', 'mordred']
        self.gentils=['gentil', 'merlin', 'perceval']
        self.mechants=['mechant', 'assassin', 'mordred', 'morgane']
        self.players=[]
        self.state='lobby' # Differents states : {'lobby':'Players are joining and choosing the roles', 'composition':'The leader is choosing the team'}
        self.roles=[]
        self.actors=[] # format : [{'user':user, 'role':role}]
        self.leader=0
        self.quests=[] # format : [True, True, False] (True = successful)
        self.votefailcount=0
    async def nextLead(self):
        if self.leader+1==len(self.actors):
            self.leader=0
        else:
            self.leader+=1
    async def startGame(self, client):
        for actor in self.actors:
            if actor['role'] in ['gentil']:
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.".format(actor['role']), color=0x1d5687))

            if actor['role'] in ['merlin']:
                mechstr=""
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in ['mechant', 'assassin', 'morgane']:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.\n Sont méchants : \n{1}".format(actor['role'], mechstr), color=0x1d5687))

            if actor['role'] in ['perceval']:
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in ['merlin', 'morgane']:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.\n Vous ne savez pas qui est merlin ou morgane de :\n{1}".format(actor['role'], mechstr), color=0x1d5687))

            if actor['role'] in self.mechants:
                mechstr=""
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in self.mechants:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator)) 
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.\n Sont méchants : \n{1}".format(actor['role'], mechstr), color=0xbd2b34))
        await self.startTurn(client)
    async def startTurn(self, client):
        await self.nextlead()
        
