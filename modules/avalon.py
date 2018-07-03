import utils.usertools
import random
import discord
import settings.avalon
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
                        await client.send_message(message.channel, message.author.mention + ", la partie est complète...")
                else:
                    await client.send_message(message.channel, message.author.mention + ", vous êtes déjà dans la partie...")

    #     -Quit command-
            if message.content=='/avalon quit':
                if message.author in avalonGame.players :
                    avalonGame.players.remove(message.author)
                    await client.send_message(message.channel, message.author.mention + " a quitté la partie.")
                else:
                    await client.send_message(message.channel, message.author.mention + ", vous n'êtes pas dans la partie...")

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
                                await client.send_message(message.channel, message.author.mention + ", `{0}` n'a pas rejoint la partie...".format(user.display_name))
                        else:
                            await client.send_message(message.channel, message.author.mention + ", `{0}` n'est pas un id valide...".format(id))

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
                if len(avalonGame.players)>=5 or settings.avalon.debug:
                    if len(avalonGame.roles) == len(avalonGame.players) :
                        avalonGame.state='composition'
                        randplayers=random.sample(avalonGame.players, len(avalonGame.players))
                        randroles=random.sample(avalonGame.roles, len(avalonGame.roles))
                        for i in range(len(randplayers)):
                            avalonGame.actors.append({'user':randplayers[i], 'role':randroles[i]})
                        avalonGame.leader=random.randint(0,len(avalonGame.actors)-1)
                        avalonGame.statuschan=message.channel
                        await avalonGame.startGame(client)
                    else:
                        await client.send_message(message.channel, message.author.mention + ", le nombre de roles est différent du nombre de joueurs... :/")
                else:
                    await client.send_message(message.channel, message.author.mention + ", la partie ne peut-être lancée qu'avec 5 joueurs au minimum...")


async def reactionHandler(client, reaction, user, avalonGame, action):
    if not user==client.user:
    # -Team composition-
        if avalonGame.state == 'composition':
            if reaction.message.id == avalonGame.leadmsg.id :
                if str(reaction.emoji) in avalonGame.emotes[:len(avalonGame.actors):]:
                    chosenPlayer=avalonGame.emotes.index(reaction.emoji)
                    if not chosenPlayer in avalonGame.team and action=='add':
                        avalonGame.team.append(chosenPlayer)
                        await avalonGame.updateTeam(client)
                    if chosenPlayer in avalonGame.team and action=='remove':
                        avalonGame.team.remove(chosenPlayer)
                        await avalonGame.updateTeam(client)
                if str(reaction.emoji) == '✅' and action=='add' and avalonGame.validteam:
                    avalonGame.state='voting'
                    await avalonGame.voteStageStart(client)
        if avalonGame.state == 'voting':
            for group in avalonGame.votes.items():
                if group[1]['message'].id == reaction.message.id and (not avalonGame.votes[group[0]]['voted']):
                    if str(reaction.emoji) == '✅' and action == 'add':
                        avalonGame.votes[group[0]]['values'].update({'Yes':True})
                    if str(reaction.emoji) == '✅' and action == 'remove':
                        avalonGame.votes[group[0]]['values'].update({'Yes':False})
                    if str(reaction.emoji) == '❎' and action == 'add':
                        avalonGame.votes[group[0]]['values'].update({'No':True})
                    if str(reaction.emoji) == '❎' and action == 'remove':
                        avalonGame.votes[group[0]]['values'].update({'No':False})
                    if avalonGame.votes[group[0]]['values']['Yes'] == avalonGame.votes[group[0]]['values']['No']:
                        if avalonGame.votes[group[0]]['values']['valid']:
                            avalonGame.votes[group[0]]['values'].update({'valid':False})
                            await client.remove_reaction(group[1]['message'], '⭕', client.user)
                    else :
                        if not avalonGame.votes[group[0]]['values']['valid']:
                            avalonGame.votes[group[0]]['values'].update({'valid':True})
                            await client.add_reaction(group[1]['message'], '⭕')
                    if str(reaction.emoji) == '⭕' and avalonGame.votes[group[0]]['values']['valid'] and action == 'add':
                        avalonGame.votes[group[0]].update({'voted':True})
                        await avalonGame.voteStageCheck(client)
class AvalonSave:
    def __init__(self):
        self.emotes=["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
        self.implemented_roles=['gentil', 'mechant', 'merlin', 'perceval', 'morgane', 'assassin', 'mordred', 'oberon']
        self.gentils=['gentil', 'merlin', 'perceval']
        self.mechants=['mechant', 'assassin', 'mordred', 'morgane', 'oberon']
        self.players=[]
        self.state='lobby' # Differents states : {'lobby':'Players are joining and choosing the roles', 'composition':'The leader is choosing the team', 'voting':'The players are voting the team made by the leader', 'expedition':T'he team chosen by the leader votes for the success or the failure of a quest'}
        self.roles=[]
        self.actors=[] # format : [{'user':user, 'role':role}]
        self.leader=0
        self.quests=[] # format : [True, True, False] (True = successful)
        self.team=[] # format : [0, 3, 4]
        self.validteam=False
        self.questfailcount=0 # ❌ * 2 for example
        self.votefailcount=0
        self.leadmsg=None
        self.leadconfirmmsg=None
        self.votes={}
        self.statuschan=None

    async def nextLead(self):
        if self.leader+1==len(self.actors):
            self.leader=0
        else:
            self.leader+=1
        self.team=[] # format : [0, 3, 4]
        self.validteam=False
        self.leadmsg=None
        self.leadconfirmmsg=None

    async def startGame(self, client):
        for actor in self.actors:
            if actor['role'] == 'gentil' :
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.".format(actor['role']), color=0x1d5687))
            if actor['role'] == 'oberon' :
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.".format(actor['role']), color=0xbd2b34))
            if actor['role'] == 'merlin':
                mechstr=""
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in ['mechant', 'assassin', 'morgane', 'oberon']:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.\n Sont méchants : \n{1}".format(actor['role'], mechstr), color=0x1d5687))

            if actor['role'] == 'perceval':
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in ['merlin', 'morgane']:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.\n Vous ne savez pas qui est merlin ou morgane de :\n{1}".format(actor['role'], mechstr), color=0x1d5687))

            if actor['role'] in ['mechant', 'assassin', 'mordred', 'morgane']:
                mechstr=""
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in self.mechants:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator)) 
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Vous êtes {0}.\n Sont méchants : \n{1}".format(actor['role'], mechstr), color=0xbd2b34))
        await self.startTurn(client)

    async def startTurn(self, client):
        await self.nextLead()
        sumquest=""
        playerstr=""
        for i in range(len(self.actors)):
            playerstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
        for quest in self.quests :
            if quest:
                sumquest+="✅ "
            else:
                sumquest+="❌ "
        for team in settings.avalon.teams[len(self.actors)][len(self.quests)::] :
            sumquest += "{0} ".format(self.emotes[team-1])
        lastquest=""
        if self.quests:
            if self.questfailcount:
                lastquest="❌ *{0}\n".format(str(questfailcount))
            else:
                lastquest="✅\n"
        embed=discord.Embed(title="AVALON", description="{0}\n{1}\n\nNombre d'équipes rejetées : {2}\nLe prochain leader est : {3}".format(lastquest, sumquest, str(self.votefailcount), "{0} `{1}`\n".format(self.emotes[self.leader], self.actors[self.leader]['user'].display_name + '#' + str(self.actors[self.leader]['user'].discriminator))), color=0x75dd63)
        await client.send_message(self.statuschan, embed=embed)
        for i in range(len(self.actors)):
            await client.send_message(self.actors[i]['user'], embed=embed)
            if i==self.leader:
                self.leadmsg = await client.send_message(self.actors[i]['user'], embed=discord.Embed(title="AVALON", description="Vous êtes le leader, vous devez choisir une équipe. Ajoutez les réactions correspondantes, puis validez.\n\nListe des joueurs :\n{0}".format(playerstr), color=0xddc860))
        for emote in self.emotes[:len(self.actors):]:
            await client.add_reaction(self.leadmsg, emote)
        await self.updateTeam(client)

    async def updateTeam(self, client):
        teamstr=""
        for i in self.team :
            teamstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
        if self.leadconfirmmsg:
            await client.edit_message(self.leadconfirmmsg, embed=discord.Embed(title="AVALON", description="L'équipe enregistrée :\n{0}".format(teamstr), color=0xddc860))
        else:
            self.leadconfirmmsg = await client.send_message(self.actors[self.leader]['user'], embed=discord.Embed(title="AVALON", description="L'équipe enregistrée :\n{0}".format(teamstr), color=0xddc860))
        if len(self.team) == settings.avalon.teams[len(self.actors)][len(self.quests)::][0]:
            if not self.validteam :
                await client.add_reaction(self.leadmsg, '✅')
                self.validteam=True
        elif self.validteam:
            await client.remove_reaction(self.leadmsg, '✅', client.user)
            self.validteam=False

    async def voteStageStart(self, client):
        teamstr=""
        for i in self.team :
            teamstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
        await client.send_message(self.statuschan, embed=discord.Embed(title="AVALON", description="L'équipe proposée par {0}:\n{1}".format(" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator)), teamstr), color=0xddc860))
        for i in range(len(self.actors)):
            self.votes.update({i:{'message':await client.send_message(self.actors[i]['user'], embed=discord.Embed(title="AVALON", description="L'équipe proposée par {0}:\n{1}".format(" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator)), teamstr), color=0xddc860)), 'values':{'Yes':False, 'No':False, 'valid':False}, 'voted':False}})
            for emote in ['✅', '❎'] :
                await client.add_reaction(self.votes[i]['message'], emote)
    async def voteStageCheck(self, client):
        votes=[]
        for playergrp in self.votes.items():
            if playergrp[1]['values']['valid']:
                votes.append(playergrp[1]['values']['Yes'])
        if len(votes) == len(self.votes):
            if votes.count(False) >= votes.count(True):
                self.state='composition'
                self.votefailcount += 1
            else:
                self.state='expedition'
                self.votefailcount = 0
            votesstr=""
            for i in range(len(self.votes)):
                votesstr+=" {0} `{1}` : {2}\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator), {True:'✅', False:'❎'}[self.votes[i]['values']['Yes']])
            for actor in self.actors :
                await client.send_message(actor['user'], embed=discord.Embed(title="AVALON", description="Les joueurs ont voté :\n{0}".format(votesstr), color=0x75dd63))
            await client.send_message(self.statuschan, embed=discord.Embed(title="AVALON", description="Les joueurs ont voté :\n{0}".format(votesstr), color=0x75dd63))
