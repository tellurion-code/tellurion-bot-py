import discord

from modules.base import BaseClassPython
from modules.petrigon import constants
from modules.petrigon.power import Power
from modules.petrigon.game import Game


class MainClass(BaseClassPython):
    name = "Petrigon"
    help = {
        "description": "Module du jeu Petrigon",
        "commands": {
            "`{prefix}{command} create`": "Crée une partie",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} rules`": "Affiche les règles"
        }
    }
    help_active = True
    command_text = "hextri"
    color = 0x00FFBF

    def __init__(self, client):
        super().__init__(client)
        self.config["command_text"] = self.command_text
        self.config["color"] = self.color
        self.config["configured"] = True
        self.config["auth_everyone"] = True

        self.debug = False
        self.games = {}

    async def on_ready(self):
        if self.objects.save_exists("globals"):
            object = self.objects.load_object("globals")
            self.debug = object["debug"]

        if self.objects.save_exists("games"):
            games = self.objects.load_object("games")
            for game in games.values():
                self.games[game["channel"]] = Game(self)
                # await self.games[game["channel"]].reload(game, self.client)

        emoji_ids = (
            (1204413937966391347, 1204430337187389503),
            (1204411914759970816, 1204430329348358255),
            (1204411913031917588, 1204430331713814548),
            (1204411903745462272, 1204430335316725790),
            (1204411907826786324, 1204430503411843093),
            (1204411917821542400, 1204430327758454875),
            (1204411909437132820, 1204430501507633153),
            (1204413940574986274, 1204430603424890920),
            (1204411905330913340, 1204430333383282740),
        )
        for i, ids in enumerate(emoji_ids):
            emojis = list(filter(None, (self.client.get_emoji(id) for id in ids)))
            constants.TILE_COLORS[i] = str(emojis[0] if len(emojis) else constants.TILE_COLORS[i])

    async def command(self, message, args, kwargs):
        if len(args):
            if args[0] == "join't":
                await message.channel.send(message.author.mention + " n'a pas rejoint la partie")

    async def com_create(self, message, args, kwargs):
        if message.channel.id in self.games:
            await message.channel.send("Il y a déjà une partie en cours dans ce channel")
        else:
            self.games[message.channel.id] = Game(self)
            await self.games[message.channel.id].on_creation(message)

    async def com_end(self, message, args, kwargs):
        if message.channel.id in self.games and message.author.id in self.games[message.channel.id].players:
            await self.games[message.channel.id].end()

    # Active le debug: le nombre minimal de joueurs
    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            self.debug = not self.debug
            await message.channel.send("Debug: " + str(self.debug))

            if self.objects.save_exists("globals"):
                save = self.objects.load_object("globals")
            else:
                save = {}

            save["debug"] = self.debug
            self.objects.save_object("globals", save)

    async def com_rules(self, message, args, kwargs):
        if len(args) > 1:
            if args[1] == "powers":
                await message.channel.send(embed=discord.Embed(
                    title=":small_orange_diamond: Pouvoirs :small_orange_diamond:",
                    description="Les pouvoirs actifs sont déclenchés avec l'option 🦸 et ne prennent pas le tour\n\n" + '\n\n'.join(["**" + c.name + "**\n" + c.description for c in Power.__subclasses__()]),
                    color=self.color))
            else:
                await message.channel.send("Sous-section inconnue")
        else:
            await message.channel.send(embed=discord.Embed(
                title=":small_orange_diamond: Règles de Petri :small_orange_diamond:",
                description="""
:small_blue_diamond: **But du jeu** : :small_blue_diamond:
Chaque joueur commence avec une troupe à un endroit aléatoire de la carte de 10x10 au début de la partie.
Le gagnant est le joueur qui est le dernier avec des troupes encore vivantes, ou bien qui arrive à contrôler 50% de la carte.
Après 40 tours de table complets (manche) sans qu'un gagnant ne soit déterminé, le joueur avec le plus de troupes gagne.

:small_blue_diamond: **Déroulement d’un tour** : :small_blue_diamond:
 -  Le joueur choisit une direction
 -  Toutes ses troupes essaient de se répliquer dans cette direction:
   -  Si la case dans cette direction est vide, une nouvelle troupe de sa couleur est créée
   -  Si la case est occupée par une troupe alliée, rien ne se passe
   -  Si la case est occupée par une troupe ennemie, un combat se déclenche entre cette troupe et celle qui essaie de se répliquer

:small_blue_diamond: **Les combats** : :small_blue_diamond:
Pour déterminer qui gagne le combat, il suffit de regarder le nombre de troupes alliées se trouvant en une ligne derrière les deux troupes:
 -  Si l'attaquant en a le plus, il se réplique sur le défenseur
 -  Si le défenseur en a le plus, rien ne se passe
 -  S'il y a égalité, le défenseur est tué mais l'attaquant ne se réplique pas
                """,
                color=self.color))
