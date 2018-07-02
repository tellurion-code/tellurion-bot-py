import utils.usertools

async def commandHandler(client, message, avalonGame):
    if message.startswith('/avalon'):

#     -lobby commands-
        if avalonGame.state=='lobby':
    #     -Join command-
            if message.content=='/avalon join':
                if not message.author.id in avalonGame.playersid:
                    if not len(avalonGame.playersid)>=12:
                        avalonGame.playersid.append(message.author.id)
                        await client.send_message(message.channel, message.author.mention + " a rejoint la partie.")
                    else:
                        await client.send_message(message.channel, message.author.mention + ", la partie est complète..")
                else:
                    await client.send_message(message.channel, message.author.mention + ", vous êtes déjà dans la partie..")

    #     -Quit command-
            if message.content=='/avalon quit' and avalonGame.state=='lobby':
                if message.author.id in avalonGame.playersid :
                    avalonGame.playersid.remove(message.author.id)
                    await client.send_message(message.channel, message.author.mention + " a quitté la partie.")
                else:
                    await client.send_message(message.channel, message.author.mention + ", vous n'êtes pas dans la partie..")

    #     -Player list command :
            if message.content=='/avalon players list':
                await client.send_message(message.channel, "Liste des joueurs :\n```PYTHON\n{0}```".format(str(list(map(lambda x:utils.usertools.UserByID(x).name, avalonGame.playersid)))))

    #     -Roles list command-
            if message.content=='/avalon roles list':
                await client.send_message(message.channel, "Liste des roles :\n```PYTHON\n{0}```".format(str(avalonGame.roles)))

    #     -Add Role command-
            if message.content.startswith('/avalon roles add'):
                if len(message.content.split(' '))==3:
                    ans=""
                    for role in message.content.split(' ')[2].split(','):
                        if role in avalonGame.implemented_roles :
                            roles.append(role)
                            ans += "{0} ajouté\n".format(role)
                        else:
                            ans += "Le rôle {0} n'est pas supporté, veuillez en prendre un parmis `{1}`.".format(role, str(avalonGame.implemented_roles))
                else:
                    await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique role ou une liste de roles séparés par une virgule.")

    #     -Remove role command-
            if message.content.startswith('/avalon roles remove'):
                if len(message.content.split(' '))==3:
                    ans=""
                    for role in message.content.split(' ')[2].split(','):
                        if role in avalonGame.implemented_roles :
                            roles.remove(role)
                            ans += "{0} retiré\n".format(role)
                        else:
                            ans += "Le rôle {0} n'est pas supporté, veuillez en prendre un parmis `{1}`.".format(role, str(avalonGame.implemented_roles))
            else:
                    await client.send_message(message.channel, message.author.mention + ", veuillez préciser un unique role ou une liste de roles séparés par une virgule.")


class AvalonSave:
    def __init__(self):
        self.implemented_roles=['gentil', 'mechant', 'merlin', 'perceval', 'morgane', 'assassin', 'mordred']
        self.playersid=[]
        self.state='lobby' # Differents states : {'lobby':'Players are joining and choosing the roles', }
        self.roles=[]
