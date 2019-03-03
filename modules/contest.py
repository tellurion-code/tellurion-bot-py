import asyncio
import os
import pickle
import random
from subprocess import call

import discord

moduleFiles = "contest"


class MainClass:

    def __init__(self, client, modules, owners, prefix):
        if not os.path.isdir("storage/%s" % moduleFiles):
            call(['mkdir', 'storage/%s' % moduleFiles])
        self.save = None
        # format : {'players':{'player_id':score}, 'turn':turn}
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message', 'on_ready']  # events list
        self.command = "%scontest" % prefix  # command prefix (can be empty to catch every single messages)
        self.contest_role = 0  # Contest Master
        self.emotes = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]  # Emotes used for selection
        self.validator = ['⭕'] # Emote used for validation
        self.votes = {}
        self.channel = None

        self.name = "Contest"
        self.description = "Module du jeu Contest"
        self.interactive = True
        self.color = 0x79f8f8
        self.help = """\
 </prefix>contest join
 => Rejoindre la liste d'attente
 
 </prefix>contest leave
 => Quitter la liste d'attente
 
 </prefix>contest players
 => Affiche la liste d'attente
 
 </prefix>contest start
 => Lancer la partie avec les personnes présentes dans la liste d'attente
 
 </prefix>contest reset
 => Réinitialiser la partie
 
 </prefix>contest stats
 => Affiche les statistiques du jeu (le parametrage du tri viendra plus tard)
 
"""

    def save_object(self, object, object_name):
        with open("storage/%s/" % moduleFiles + object_name + "tmp", "wb") as pickleFile:
            pickler = pickle.Pickler(pickleFile)
            pickler.dump(object)
        call(['mv', "storage/%s/" % moduleFiles + object_name + "tmp", "storage/%s/" % moduleFiles + object_name])

    def load_object(self, object_name):
        if self.save_exists(object_name):
            with open("storage/%s/" % moduleFiles + object_name, "rb") as pickleFile:
                unpickler = pickle.Unpickler(pickleFile)
                return unpickler.load()

    def save_exists(self, object_name):
        return os.path.isfile("storage/%s/" % moduleFiles + object_name)

    async def on_ready(self):
        if self.save is None:
            if self.save_exists('save'):
                self.save = self.load_object('save')
            else:
                self.save = {'players':{}, 'turn':0}
            self.save_object(self.save, 'save')

    async def send_reactions(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def on_message(self, message):
        if self.save is None:
            await self.on_ready()
        args = message.content.split()
        if len(args) != 2:
            await self.modules['help'][1].send_help(message.channel, self)
        elif args[1] == "join" and not self.save['turn']:
            if message.author.id not in self.save['players']:
                self.save['players'][message.author.id] = 0
                await message.channel.send(message.author.mention + ", vous avez bien été ajouté à la liste d'attente.")
            else:
                await message.channel.send(message.author.mention + ", vous êtes déjà dans la liste d'attente.")
        elif args[1] == "leave" and not self.save['turn']:
            if message.author.id in self.save['players']:
                self.save['player'].pop(message.author.id, None)
                await message.channel.send(message.author.mention
                                           + ", vous avez bien été retiré de la liste d'attente.")
            else:
                await message.channel.send(message.author.mention + ", vous n'êtes pas dans la liste d'attente.")
        elif args[1] == "start" and not self.save['turn']:
            if 2 < len(self.save['players']) < 11:
                self.channel = message.channel
                await message.channel.send(message.author.mention + ", la partie va commencer.")
                pass
            else:
                await message.channel.send(message.author.mention + ", vous devez être entre 3 et 10 joueurs (compris).")
        elif args[1] == "reset":
            self.save = {'players':{}, 'turn':0}
            self.save_object(self.save, 'save')
        elif args[1] == "players":
            players=[]
            for id in self.save['players'].keys() :
                players.append(self.client.get_user(id).display_name)
            await message.channel.send("Liste d'attente ({0}):\n```PYTHON\n{1}\n```".format(len(players),players))
        elif args[1] == "stats":
            await message.channel.send(message.author.mention + ", cette fonction n'est pas encore disponible.")
        else:
            await self.modules['help'][1].send_help(message.channel, self)

    def turn(self):
        points = ceil((self.save['turn']+1)/3.0)
        players = list(self.save['players'].keys())


"""
        for player in players:
            self.votes[player] = 0
            playersstr = ""
            other_players = [i for i,p in enumerate(players) if p != player]
            for i in other_players:
                playersstr += " {0} `{1}`\n".format(self.emotes[i], self.client.get_user(players[i]).display_name + '#'
                                                    + str(self.client.get_user(players[i]).discriminator))
            embed = discord.Embed(title = "Phase de vote - Tour " + str(self.save['turn']+1),
                                  description = playersstr, color = self.color)
            message = await message.channel.send(embed = embed)
            self.votes[player] = {'message': message, 'value': None}

        """





        #  create list for every player
        #  send message for every player
        #  wait for players' reaction
        #  sort by number of votes
        #  calculate points
        #  send result message
        #  send recap message
        #  increment turn

