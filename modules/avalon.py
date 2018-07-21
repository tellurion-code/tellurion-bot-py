import utils.usertools
import utils.perms
import time
import random
import discord
import settings.avalon
async def commandHandler(client, message, avalonGame):
    if message.content.startswith('/avalon'):
#     -general commands-
        if message.content == '/avalon reset' and await utils.perms.hasrole(message.author, "1"):
            avalonGame.__init__()
            await client.send_message(message.channel, message.author.mention + "La partie a été réinitialisée.")
        if message.content == '/avalon help' :
            aidestr="Commandes générales :\n\n"
            #aidestr+="    [BOT OWNER SEULEMENT] : /avalon reset => Réinitialise la sauvegarde du jeu\n\n"
            aidestr+="    /avalon help \n=> Affiche ce message d'aide\n\n"
            aidestr+="Commandes du lobby :\n\n"
            aidestr+="    /avalon join \n=> Vous ajoute dans la liste des joueurs de la prochaine partie\n\n"
            aidestr+="    /avalon quit \n=> Vous retire de la liste des joueurs de la prochaine partie\n\n"
            aidestr+="    /avalon players list \n=> Affiche la liste des joueurs ayant rejoint\n\n"
            aidestr+="    /avalon players kick <userid> \n=> Retire le joueur spécifié de la liste de joueurs\n\n"
            aidestr+="    /avalon roles list \n=> Affiche la liste des roles pour la prochaine partie\n\n"
            aidestr+="    /avalon roles add <role> \n=> Ajoute le rôle spécifié à la liste de roles\n\n"
            aidestr+="    /avalon roles remove <role> \n=> Retire le rôle spécifié de la lsite de roles\n\n"
            aidestr+="    /avalon start \n=> Lance la partie de avalon\n\n"
            await client.send_message(message.channel, embed=discord.Embed(title='[AVALON] - Aide', description=aidestr, color=0x1aceff))
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
                await client.send_message(message.channel, "Liste des rôles :\n```PYTHON\n{0}```".format(str(avalonGame.roles)))

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
                            ans += "Le rôle {0} n'est pas supporté, veuillez en prendre un parmi `{1}`.\n".format(role, str(avalonGame.implemented_roles))
                    await client.send_message(message.channel, message.author.mention + ",\n{0}".format(ans))
                else:
                    await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique rôle ou une liste de rôles séparés par une virgule.")


            if message.content.startswith('/avalon roles auto') :
                avalonGame.roles = []
                nb_players = len(avalonGame.players)
                repartition = settings.avalon.roles_distribution[nb_players]
                for gentil in range(repartition[0]) :
                    avalonGame.roles.append("gentil")
                for mechant in range(repartition[1]) :
                    avalonGame.roles.append("mechant")
                await client.send_message(message.channel, "Liste des rôles :\n```PYTHON\n{0}```".format(str(avalonGame.roles)))


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
                            ans += "Le rôle {0} n'est pas supporté, veuillez en prendre un parmi `{1}`.".format(role, str(avalonGame.implemented_roles))
                    await client.send_message(message.channel, message.author.mention + ",\n{0}".format(ans))
                else:
                    await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique rôle ou une liste de rôles séparés par une virgule.")

    #     -Start game command-
            if message.content=='/avalon start' :
                if len(avalonGame.players)>=5 or settings.avalon.debug:
                    if len(avalonGame.roles) == len(avalonGame.players) :
                        random.seed(time.time())
                        avalonGame.state='composition'
                        randplayers=random.sample(avalonGame.players, len(avalonGame.players))
                        randroles=random.sample(avalonGame.roles, len(avalonGame.roles))
                        for i in range(len(randplayers)):
                            avalonGame.actors.append({'user':randplayers[i], 'role':randroles[i]})
                        avalonGame.leader=random.randint(0,len(avalonGame.actors)-1)
                        avalonGame.statuschan=message.channel
                        for actor in avalonGame.actors :
                            await client.send_message(actor['user'], "̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉\n̉")
                        await avalonGame.startGame(client)
                    else:
                        await client.send_message(message.channel, message.author.mention + ", le nombre de rôles est différent du nombre de joueurs... :/")
                else:
                    await client.send_message(message.channel, message.author.mention + ", La partie nécessite 5 joueurs au minimum pour être lancée...")


async def reactionHandler(client, reaction, user, avalonGame, action):
    if not user==client.user:
    # -Team composition-
        if avalonGame.state == 'composition':
            if reaction.message.id == avalonGame.leadmsg.id :
                if str(reaction.emoji) in avalonGame.emotes[:len(avalonGame.actors):]:
                    chosenPlayer=avalonGame.emotes.index(str(reaction.emoji))
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
        if avalonGame.state == 'expedition':
            for group in avalonGame.expedvotes.items():
                if group[1]['message'].id == reaction.message.id and (not avalonGame.expedvotes[group[0]]['voted']):
                    if str(reaction.emoji) == '✅' and action == 'add':
                        avalonGame.expedvotes[group[0]]['values'].update({'Yes':True})
                    if str(reaction.emoji) == '✅' and action == 'remove':
                        avalonGame.expedvotes[group[0]]['values'].update({'Yes':False})
                    if str(reaction.emoji) == '❎' and action == 'add':
                        avalonGame.expedvotes[group[0]]['values'].update({'No':True})
                    if str(reaction.emoji) == '❎' and action == 'remove':
                        avalonGame.expedvotes[group[0]]['values'].update({'No':False})
                    if avalonGame.expedvotes[group[0]]['values']['Yes'] == avalonGame.expedvotes[group[0]]['values']['No']:
                        if avalonGame.expedvotes[group[0]]['values']['valid']:
                            avalonGame.expedvotes[group[0]]['values'].update({'valid':False})
                            await client.remove_reaction(group[1]['message'], '⭕', client.user)
                    else :
                        if not avalonGame.expedvotes[group[0]]['values']['valid']:
                            avalonGame.expedvotes[group[0]]['values'].update({'valid':True})
                            await client.add_reaction(group[1]['message'], '⭕')
                    if str(reaction.emoji) == '⭕' and avalonGame.expedvotes[group[0]]['values']['valid'] and action == 'add':
                        avalonGame.expedvotes[group[0]].update({'voted':True})
                        await avalonGame.expeditionStageCheck(client)
        if avalonGame.state == 'assassination':
            if reaction.message.id == avalonGame.assassinmsg.id :
                if str(reaction.emoji) in avalonGame.emotes and avalonGame.emotes.index(str(reaction.emoji)) in avalonGame.assassinlist:
                    chosenPlayer=avalonGame.emotes.index(str(reaction.emoji))
                    if not chosenPlayer in avalonGame.assassinkilllist and action=='add':
                        avalonGame.assassinkilllist.append(chosenPlayer)
                        await avalonGame.assassinationCheck(client)
                    if not chosenPlayer in avalonGame.assassinkilllist and action=='remove':
                        avalonGame.assassinkilllist.remove(chosenPlayer)
                        await avalonGame.assassinationCheck(client)
                if str(reaction.emoji) == '✅' and action=='add' and len(avalonGame.assassinkilllist) == 1 and avalonGame.assassinvalid:
                    avalonGame.state=None
                    avalonGame.killed=avalonGame.assassinkilllist[0]
                    await avalonGame.endGame(client)


class AvalonSave:
    def __init__(self):
        self.emotes=["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
        self.implemented_roles=['gentil', 'mechant', 'merlin', 'perceval', 'morgane', 'assassin', 'mordred', 'oberon']
        self.gentils=['gentil', 'merlin', 'perceval']
        self.mechants=['mechant', 'assassin', 'mordred', 'morgane', 'oberon']
        self.players=[]
        self.state='lobby' # Differents states : {'lobby':'Players are joining and choosing the roles', 'composition':'The leader is choosing the team', 'voting':'The players are voting the team made by the leader', 'expedition':The team chosen by the leader votes for the success or the failure of a quest', 'assassination':'The assassin chooses someone to kill him.'}
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
        self.expedvotes={}
        self.statuschan=None
        self.killed=None
        self.assassinmsg=None
        self.assassinlist=[]
        self.assassinkilllist=[]
        self.assassinvalid=False
        self.teamvoteembed=None
        self.teamvotestatuschanmsg=None
    async def nextLead(self):
        if self.leader+1==len(self.actors):
            self.leader=0
        else:
            self.leader+=1
        self.team=[] # format : [0, 3, 4]
        self.validteam=False
        self.leadmsg=None
        self.leadconfirmmsg=None
        self.teamvoteembed=None
    async def endGame(self, client):
        rolesstr="**RECAP DE PARTIE**\n"
        for actor in self.actors:
            rolesstr+= " {0} `{1}` : `{2}`\n".format(self.emotes[self.actors.index(actor)], actor['user'].display_name + '#' + str(actor['user'].discriminator), actor['role'])
        if self.killed is not None:
            rolesstr+="L'assassin tue {0} qui était {1}.\n".format(" {0} `{1}`".format(self.emotes[self.killed], self.actors[self.killed]['user'].display_name + '#' + str(self.actors[self.killed]['user'].discriminator)), self.actors[self.killed]['role'])
            if self.actors[self.killed]['role']=='merlin':
                rolesstr+="**Les méchants gagnent !**"
            else:
                rolesstr+="**Les gentils gagnent !**"
        elif self.quests.count(False)==3 or self.votefailcount==5:
            rolesstr+="**Les méchants gagnent !**"
        elif self.quests.count(True)==3:
            rolesstr+="**Les gentils gagnent !**"
        embed=discord.Embed(title="[AVALON] - Recap de partie", description=rolesstr, color=0xffffff)
        Alix = await utils.usertools.UserByID(client, "118399702667493380")
        embedmain=discord.Embed(title="[AVALON] - Recap de partie", description=rolesstr, color=0xffffff)
        await client.send_message(self.statuschan, Alix.mention, embed=embedmain)
        for actor in self.actors:
            await client.send_message(actor['user'], embed=embed)
        self.__init__()
    async def startGame(self, client):
        playerliststr=""
        for i in range(len(self.actors)):
            playerliststr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
        await client.send_message(self.statuschan, embed=discord.Embed(title="[AVALON] - Liste des joueurs", description=playerliststr, color=0xffffff))
        for actor in self.actors:
            if actor['role'] == 'gentil' :
                await client.send_message(actor['user'], embed=discord.Embed(title="[AVALON] - Distribution des rôles", description="Vous êtes **{0}**.".format(actor['role'].upper()), color=0x1d5687))
            if actor['role'] == 'oberon' :
                await client.send_message(actor['user'], embed=discord.Embed(title="[AVALON] - Distribution des rôles", description="Vous êtes **{0}**.".format(actor['role'].upper()), color=0xbd2b34))
            if actor['role'] == 'merlin':
                mechstr=""
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in ['mechant', 'assassin', 'morgane', 'oberon']:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
                await client.send_message(actor['user'], embed=discord.Embed(title="[AVALON] - Distribution des rôles", description="Vous êtes **{0}**.\n Sont méchants : \n{1}".format(actor['role'].upper(), mechstr), color=0x1d5687))

            if actor['role'] == 'perceval':
                mechstr=""
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in ['merlin', 'morgane']:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
                await client.send_message(actor['user'], embed=discord.Embed(title="[AVALON] - Distribution des rôles", description="Vous êtes **{0}**.\n Vous ne savez pas qui est merlin ou morgane entre:\n{1}".format(actor['role'].upper(), mechstr), color=0x1d5687))

            if actor['role'] in ['mechant', 'assassin', 'mordred', 'morgane']:
                mechstr=""
                for i in range(len(self.actors)):
                    if self.actors[i]['role'] in ['mechant', 'assassin', 'mordred', 'morgane']:
                        mechstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
                await client.send_message(actor['user'], embed=discord.Embed(title="[AVALON] - Distribution des rôles", description="Vous êtes **{0}**.\n Sont méchants : \n{1}".format(actor['role'].upper(), mechstr), color=0xbd2b34))
        await self.startTurn(client)

    async def startTurn(self, client):
        if self.quests.count(True) == 3 or self.quests.count(False) == 3 or self.votefailcount==5 :
            if self.quests.count(True) == 3 and 'assassin' in self.roles:
                self.state='assassination'
                await self.assassinationStart(client)
            else:
                await self.endGame(client)
            return
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
                lastquest="❌ *{0}\n".format(str(self.questfailcount))
            else:
                lastquest="✅\n"
        embed=discord.Embed(title="[AVALON] - Début de tour - Quête n°" + str(len(self.quests) + 1), description="{0}\n{1}\n\nNombre d'équipes rejetées : {2}\nLe prochain leader est : {3}".format(lastquest, sumquest, str(self.votefailcount), "{0} `{1}`\n".format(self.emotes[self.leader], self.actors[self.leader]['user'].display_name + '#' + str(self.actors[self.leader]['user'].discriminator))), color=0x75dd63)
        await client.send_message(self.statuschan, embed=embed)
        for i in range(len(self.actors)):
            await client.send_message(self.actors[i]['user'], embed=embed)
            if i==self.leader:
                self.leadmsg = await client.send_message(self.actors[i]['user'], embed=discord.Embed(title="[AVALON] - Composition de l'équipe - Quête n°" + str(len(self.quests) + 1), description="Vous êtes le leader, vous devez choisir une équipe. Ajoutez les réactions correspondantes, puis validez.\n\nListe des joueurs :\n{0}".format(playerstr), color=0xddc860))
        for emote in self.emotes[:len(self.actors):]:
            await client.add_reaction(self.leadmsg, emote)
        await self.updateTeam(client)

    async def updateTeam(self, client):
        teamstr=""
        for i in self.team :
            teamstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
        if self.leadconfirmmsg:
            await client.edit_message(self.leadconfirmmsg, embed=discord.Embed(title="[AVALON] - Composition de l'équipe - Quête n°" + str(len(self.quests) + 1), description="L'équipe enregistrée :\n{0}".format(teamstr), color=0xddc860))
        else:
            self.leadconfirmmsg = await client.send_message(self.actors[self.leader]['user'], embed=discord.Embed(title="[AVALON] - Composition de l'équipe - Quête n°" + str(len(self.quests) + 1), description="L'équipe enregistrée :\n{0}".format(teamstr), color=0xddc860))
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
        self.teamvoteembed=discord.Embed(title="[AVALON] - Vote de l'équipe - Quête n°" + str(len(self.quests) + 1), description="L'équipe proposée par {0} :\n{1}".format(" {0} `{1}`".format(self.emotes[self.leader], self.actors[self.leader]['user'].display_name + '#' + str(self.actors[self.leader]['user'].discriminator)), teamstr), color=0xddc860)
        self.teamvotestatuschanmsg = await client.send_message(self.statuschan, embed=self.teamvoteembed)
        for i in range(len(self.actors)):
            self.votes.update({i:{'message':await client.send_message(self.actors[i]['user'], embed=self.teamvoteembed), 'values':{'Yes':False, 'No':False, 'valid':False}, 'voted':False}})
            for emote in ['✅', '❎'] :
                await client.add_reaction(self.votes[i]['message'], emote)
    async def voteStageCheck(self, client):
        votes=[]
        for playergrp in self.votes.items():
            if playergrp[1]['voted']:
                votes.append(playergrp[1]['values']['Yes'])
        teamstr=""
        for i in self.team :
            teamstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
        votecountstr=""
        if len(self.actors)-len(votes) == 1 :
            votecountstr="1 joueur n'a pas encore validé son vote."
        elif len(self.actors)-len(votes) > 1 :
            votecountstr="{0} joueurs n'ont pas encore validé leur vote.".format(len(self.actors)-len(votes))
        self.teamvoteembed=discord.Embed(title="[AVALON] - Vote de l'équipe - Quête n°" + str(len(self.quests) + 1), description="L'équipe proposée par {0} :\n{1}\n\n{2}".format(" {0} `{1}`".format(self.emotes[self.leader], self.actors[self.leader]['user'].display_name + '#' + str(self.actors[self.leader]['user'].discriminator)), teamstr, votecountstr), color=0xddc860)
        await client.edit_message(self.teamvotestatuschanmsg, embed=self.teamvoteembed)
        for votegrp in self.votes.items():
            await client.edit_message(votegrp[1]['message'], embed=self.teamvoteembed)
        if len(votes) == len(self.votes):
            votesstr=""
            for i in range(len(self.votes)):
                votesstr+=" {2} : {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator), {True:'✅', False:'❎'}[self.votes[i]['values']['Yes']])
            embed=discord.Embed(title="[AVALON] - Vote de l'équipe - Quête n°" + str(len(self.quests) + 1), description="Les joueurs ont voté :\n\n ✅:{1}    ❎:{2}\n\n{0}".format(votesstr, str(votes.count(True)),str(votes.count(False))), color=0x75dd63)
            await client.send_message(self.statuschan, embed=embed)
            for actor in self.actors :
                await client.send_message(actor['user'], embed=embed)
            self.votes={}
            if votes.count(False) >= votes.count(True):
                self.state='composition'
                self.votefailcount += 1
                await self.startTurn(client)
            else:
                self.state='expedition'
                self.votefailcount = 0
                self.questfailcount = 0
                await self.expeditionStart(client)
    async def expeditionStart(self,client):
        for i in self.team:
            self.expedvotes.update({i:{'message':await client.send_message(self.actors[i]['user'], embed=discord.Embed(title="[AVALON] - Expedition - Quête n°" + str(len(self.quests) + 1), description="Vous participez à une quête.\n**Étes vous pour la réussite de cette quête ?**", color=0xffffff)), 'values':{'Yes':False, 'No':False, 'valid':False}, 'voted':False}})
            for emote in ['✅', '❎'] :
                await client.add_reaction(self.expedvotes[i]['message'], emote)
    async def expeditionStageCheck(self, client):
        votes=[]
        for playergrp in self.expedvotes.items():
            if playergrp[1]['voted']:
                votes.append(playergrp[1]['values']['Yes'])
        if len(votes) == len(self.expedvotes):
            self.questfailcount=votes.count(False)
            #await client.send_message(self.statuschan, 'self.quests=`{0}`\nvotefailcount=`{1}`\nvotes=`{2}`\nself.questvotes=`{3}`'.format(str(self.quests), str(self.questfailcount),str(votes), str(self.expedvotes)))
            if len(self.actors) >= 7:
                if len(self.quests) == 3:
                    if self.questfailcount >= 2:
                        self.quests.append(False)
                    else:
                        self.quests.append(True)
                else:
                    if self.questfailcount >= 1:
                        self.quests.append(False)
                    else:
                        self.quests.append(True)
            else:
                if self.questfailcount >= 1:
                    self.quests.append(False)
                else:
                    self.quests.append(True)
            self.state='composition'
            self.expedvotes={}
            await self.startTurn(client)

    async def assassinationStart(self, client):
        playerstr=""
        for i in range(len(self.actors)):
            if not self.actors[i]['role'] in ['mechant', 'assassin', 'mordred', 'morgane', 'oberon'] :
                playerstr+=" {0} `{1}`\n".format(self.emotes[i], self.actors[i]['user'].display_name + '#' + str(self.actors[i]['user'].discriminator))
        for actor in self.actors:
            if actor['role'] == 'assassin' :
                self.assassinmsg = await client.send_message(actor['user'], embed=discord.Embed(title="[AVALON] - Assassinat - Quête n°" + str(len(self.quests) + 1), description="Vous êtes l'assassin, et trois quêtes ont été un succès. Vous devez assassiner Merlin pour gagner. Ajoutez la réaction correspondante, puis validez.\n\nListe des joueurs :\n{0}".format(playerstr), color=0xbd2b34))
        for i in range(len(self.actors)):
            if not self.actors[i]['role'] in ['mechant', 'assassin', 'mordred', 'morgane', 'oberon'] :
                self.assassinlist.append(i)
                await client.add_reaction(self.assassinmsg, self.emotes[i])
        await client.send_message(self.statuschan, embed=discord.Embed(title="[AVALON] - Assassinat - Quête n°" + str(len(self.quests) + 1), description="Les méchants vont débattre pour choisir celui qu'ils pensent être merlin. Que les gentils coupent leur micro."))
        for actor in self.actors:
            if actor['role'] in self.gentils :
                await client.send_message(actor['user'], embed=discord.Embed(title="[AVALON] - Assassinat - Quête n°" + str(len(self.quests) + 1), description="Les méchants vont débattre pour choisir celui qu'ils pensent être merlin. Coupez votre micro."))
    async def assassinationCheck(self, client):
        if len(self.assassinkilllist) == 1 :
            if not self.assassinvalid:
                await client.add_reaction(self.assassinmsg, '✅')
                self.assassinvalid=True
        elif self.assassinvalid :
            await client.remove_reaction(self.assassinmsg, '✅')
            self.assassinvalid=False
