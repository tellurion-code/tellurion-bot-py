import traceback

from modules.base import BaseClass

moduleFiles = "contest"


class MainClass(BaseClass):
    name = "Contest"
    color = 0x79f8f8
    help_active = True
    help = {
        "description": "Module du jeu Contest",
        "commands": {
            "`{prefix}{command} join`": "Rejoindre la liste d'attente",
            "`{prefix}{command} leave`": "Quitte la liste d'attente",
            "`{prefix}{command} players`": "Affiche la liste d'attente",
            "`{prefix}{command} start`": "Lance la partie",
            "`{prefix}{command} reset`": "Réinitialise la partie",
            "`{prefix}{command} stats`": "Affiche les stats",
        }
    }
    command_text = "contest"

    def __init__(self, client):
        super().__init__(client)
        self.save = None
        # format : {'players':{'player_id':score}, 'turn':turn}
        self.contest_role = 0  # Contest Master
        self.emotes = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]  # Emotes used for selection
        self.validator = ['⭕']  # Emote used for validation
        self.votes = {}
        self.channel = None

    def on_load(self):
        print("onload")
        try:
            if self.save_exists('save'):
                self.save = self.load_object('save')
            else:
                self.save = {'players': {}, 'turn': 0}
            self.save_object(self.save, 'save')
        except Exception as e:
            print(traceback.format_exc())
            print(e)

    async def on_ready(self):
        self.on_load()

    async def send_reactions(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def com_join(self, message, args, kwargs):
        if message.author.id not in self.save['players']:
            self.save['players'][message.author.id] = 0
            await message.channel.send(message.author.mention + ", vous avez bien été ajouté à la liste d'attente.")
        else:
            await message.channel.send(message.author.mention + ", vous êtes déjà dans la liste d'attente.")

    async def com_leave(self, message, args, kwargs):
        if message.author.id in self.save['players']:
            self.save['players'].pop(message.author.id, None)
            await message.channel.send(message.author.mention
                                       + ", vous avez bien été retiré de la liste d'attente.")
        else:
            await message.channel.send(message.author.mention + ", vous n'êtes pas dans la liste d'attente.")

    async def com_start(self, message, args, kwargs):
        if 2 < len(self.save['players']) < 11:
            self.channel = message.channel
            await message.channel.send(message.author.mention + ", la partie va commencer.")
            pass
        else:
            await message.channel.send(
                message.author.mention + ", vous devez être entre 3 et 10 joueurs (compris).")

    async def com_reset(self, message, args, kwargs):
        self.save = {'players': {}, 'turn': 0}
        self.save_object(self.save, 'save')
        await message.channel.send("Partie réinitialisée")

    async def com_players(self, message, args, kwargs):
        players = []
        for id in self.save['players'].keys():
            players.append(self.client.get_user(id).display_name)
        await message.channel.send("Liste d'attente ({0}):\n```PYTHON\n{1}\n```".format(len(players), players))

    async def com_stats(self, message, args, kwargs):
        await message.channel.send(message.author.mention + ", cette fonction n'est pas encore disponible.")

    async def command(self, message, args, kwargs):
        await self.modules['help'][1].send_help(message.channel, self)
"""
    def turn(self):
        points = ceil((self.save['turn'] + 1) / 3.0)
        players = list(self.save['players'].keys())
"""

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
