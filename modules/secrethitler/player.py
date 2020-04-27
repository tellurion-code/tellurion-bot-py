import discord

from modules.secrethitler.reaction_message import ReactionMessage

import modules.secrethitler.globals as globals

class Player:
    role = ""
    last_vote = ""
    inspected = False
    vote_message = None
    info_message = None

    def __init__(self, user):
        self.user = user

    async def send_vote(self, game):
        emojis = ["✅", "❎"]
        choices = ["Ja", "Nein"]

        async def cast_vote(reactions):
            self.last_vote = emojis[reactions[self.user.id][0]] + choices[reactions[self.user.id][0]]
            await game.check_vote_end()

        async def cond_player(reactions):
            return len(reactions[self.user.id]) == 1

        self.vote_message = ReactionMessage(cond_player,
            cast_vote,
            temporary = False
        )

        await self.vote_message.send(self.user,
            "Gouvernement proposé",
            "Le Président `" + str(game.players[game.order[game.turn]].user) + "` a proposé comme Chancelier `" + str(game.players[game.chancellor].user) + "`. Êtes-vous d'accord avec ce Gouvernement?\n\n",
            globals.color,
            choices,
            emojis = emojis,
            fields = [
                {
                    "name": "Votes:",
                    "value": ' '.join(["✉️" for x in game.order])
                }
            ]
        )

    async def send_veto_vote(self, game):
        emojis = ["🇯", "🇳"]
        choices = ["Ja", "Nein"]
        self.last_vote = ""

        async def cast_veto_vote(reactions):
            self.last_vote = choices[reactions[self.user.id][0]]
            await game.check_veto_vote()

        async def cond_player(reactions):
            return len(reactions[self.user.id]) == 1

        await ReactionMessage(cond_player,
            cast_veto_vote
        ).send(self.user,
            "Droit de véto : Voulez-vous annuler cette loi?",
            "",
            globals.color,
            choices,
            emojis = emojis,
        )

class Liberal(Player):
    role = "liberal"

    def __init__(self, user):
        super().__init__(user)

    async def game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie 🕊️",
            description = "Vous êtes un Libéral. Vous devez faire élire 5 lois libérales, ou bien trouver Hitler dans vos rangs et l'assassiner",
            color = 0x2e64fe
        ))

class Fascist(Player):
    role = "fascist"

    def __init__(self, user):
        super().__init__(user)

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🐍",
            description = "Vous êtes un Fasciste. Vous devez faire élire 6 lois fascistes, ou bien réussir à faire élire Hitler en tant que Chancelier une fois 3 lois fascistes votées.\n" + ("**Hitler vous connaît**" if len(game.players) <= 6 else "**Hitler ne vous connaît pas**"),
            color = 0xef223f
        )

        fascists = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role == "fascist"]
        if len(fascists):
            embed.add_field(name = "Vos coéquipiers:",
                value = '\n'.join(fascists)
            )

        embed.add_field(name = "Votre leader:",
            value = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role == "hitler"][0]
        )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Hitler(Fascist):
    role = "hitler"

    def __init__(self, user):
        super().__init__(user)

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie ☠️",
            description = "Vous êtes Hitler. Vous devez faire élire 6 lois fascistes, ou bien réussir à vous faire élire en tant que Chancelier une fois 3 lois fascistes votées.\n" + ("**Vous connaissez vos partisans**" if len(game.players) <= 6 else "**Vous ne connaissez pas vos partisans**"),
            color = 0xff0000
        )

        if len(game.players) <= 6:
            embed.add_field(name = "Vos partisans:",
                value = '\n'.join([globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role == "fascist" or game.players[x].role == "hitler" and globals.debug])
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)
