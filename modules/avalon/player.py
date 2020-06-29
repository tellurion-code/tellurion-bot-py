import discord
import random

from modules.avalon.reaction_message import ReactionMessage

import modules.avalon.globals as globals

class Player:
    role = ""
    last_vote = ""
    inspected = False
    vote_message = None
    info_message = None
    quest_emojis = [globals.quest_emojis["success"], globals.quest_emojis["failure"]]
    quest_choices = ["Réussite", "Echec"]

    def __init__(self, user):
        self.user = user

    def game_start(self, game):
        await self.team_game_start(game)

        # blaise = [x for x in game.players if x.role == "blaise"]
        # if len(blaise):
        #     await self.user.send(embed = discord.Embed(description = blaise[0] + " est le Père Blaise ✍️. Il ne peut pas être dans une quête mais connaitra le choix d'un personne participant à chacune.",
        #         color = 0x2e64fe
        #     ))

    async def send_vote(self, game):
        emojis = ["✅", "❎"]
        choices = ["Pour", "Contre"]

        async def cast_vote(reactions):
            self.last_vote = emojis[reactions[self.user.id][0]] + " " + choices[reactions[self.user.id][0]]
            await game.check_vote_end()

        async def cond_player(reactions):
            return len(reactions[self.user.id]) == 1

        self.vote_message = ReactionMessage(cond_player,
            cast_vote,
            temporary = False
        )

        await self.vote_message.send(self.user,
            "Equipe proposée",
            "Le Leader `" + str(game.players[game.order[game.turn]].user) + "` a proposé comme Equipe:\n" + '\n'.join([(globals.number_emojis[i] + ' `' + str(game.players[x].user) + '`') for i, x in game.team.items()]) + "\n\nÊtes-vous d'accord avec le départ de cette Equipe?\n",
            globals.color,
            choices,
            validation_emoji = "⭕",
            emojis = emojis,
            fields = [
                {
                    "name": "Votes:",
                    "value": ' '.join(["✉️" for x in game.order])
                }
            ]
        )

    async def send_choice(self, game):
        async def cast_choice(reactions):
            print("☑️", self.quest_emojis[reactions[self.user.id][0]])
            self.last_vote = self.quest_emojis[reactions[self.user.id][0]] + " " + self.quest_choices[reactions[self.user.id][0]]
            await game.check_quest_end()

        async def cond_player(reactions):
            return len(reactions[self.user.id]) == 1

        self.vote_message = ReactionMessage(cond_player,
            cast_choice,
            temporary = False
        )

        await self.vote_message.send(self.user,
            "Equipe acceptée",
            "Êtes-vous pour la réussite la quête?\n\n",
            globals.color,
            self.quest_choices,
            validation_emoji = "⭕",
            emojis = self.quest_emojis
        )

class Good(Player):
    allegiance = "good"
    role = "good"
    color =  0x2e64fe

    async def team_game_start(self, game):
        await self._game_start(game)

    async def _game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie 🟦",
            description = "Vous êtes un Fidèle Vassal d'Arthur. Vous devez faire réussir 3 Quêtes.",
            color = self.color
        ))

class Merlin(Good):
    role = "merlin"

    async def _game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🧙‍♂️",
            description = "Vous êtes Merlin. Vous devez faire réussir 3 Quêtes et ne pas vous révéler. Vous connaissez les méchants.",
            color = self.color
        )

        evils = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "mordred" or game.players[x].role == "karadoc"]
        if len(evils):
            embed.add_field(name = "Vos ennemis:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Percival(Good):
    role = "percival"

    async def _game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🤴",
            description = "Vous êtes Perceval. Vous devez faire réussir 3 Quêtes et protéger Merlin. Vous connaissez Merlin et Morgane.",
            color = self.color
        )

        mages = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role in ["merlin", "morgane"]]
        if len(mages):
            embed.add_field(name = "Les mages:",
                value = '\n'.join(mages)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Lancelot(Good):
    role = "lancelot"
    quest_emojis = [globals.quest_emojis["success"], globals.quest_emojis["failure"], globals.quest_emojis["reverse"]]
    quest_choices = ["Réussite", "Echec", "Inversion"]

    async def _game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie ️🛡️",
            description = "Vous êtes Lancelot. Vous devez faire réussir 3 Quêtes. Vous avez la possibilité d'inverser le résultat de la quête si vous êtes dedans.",
            color = self.color
        ))

class Karadoc(Good):
    role = "karadoc"

    async def _game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie ️🥴",
            description = "Vous êtes Karadoc. Vous devez faire réussir 3 Quêtes et protéger Merlin. Merlin vous voit comme un méchant.",
            color = self.color
        ))

# class Blaise(Good):
#     role = "blaise"
#
#     async def _game_start(self, game):
#         await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie ️✍️",
#             description = "Vous êtes Blaise. Vous devez faire réussir 3 Quêtes. Tout le monde vout connait, et vousne pouvez pas être dans une quête. A chaque quête, vous connaissez le choix d'une personne au choix.",
#             color = self.color
#         ))

class Evil(Player):
    allegiance = "evil"
    role = "evil"
    evils = []
    color = 0xef223f

    async def team_game_start(self, game):
        evils = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "oberon"]
        await self._game_start(game)

    async def _game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🟥",
            description = "Vous êtes un Serviteur de Mordred. Vous devez faire échouer 3 Quêtes.",
            color = self.color
        )

        if len(evils):
            embed.add_field(name = "Vos co-équipiers:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Assassin(Evil):
    role = "assassin"

    async def _game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🗡️",
            description = "Vous êtes l'Assassin. Vous devez faire échouer 3 Quêtes ou trouver Merlin et l'assassiner.",
            color = self.color
        )

        if len(evils):
            embed.add_field(name = "Vos co-équipiers:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

    async def send_assassin_choice(self, game):
        valid_candidates = [x for x in game.order if game.players[x].allegiance == "good"]
        emojis = [globals.number_emojis[game.order.index(x)] for x in valid_candidates]
        choices = ["`" + str(game.players[x].user) + "`" for x in valid_candidates]

        async def kill(reactions):
            if game.players[valid_candidates[reactions[self.user.id][0]]].role == "merlin":
                await game.end_game(False, "assassinat de Merlin")
            else:
                await game.end_game(True, "3 Quêtes réussies")

        async def cond(reactions):
            return len(reactions[self.user.id]) == 1

        await ReactionMessage(cond,
            kill
        ).send(self.user,
            "Choisissez qui vous souhaitez tuer",
            "",
            globals.color,
            choices,
            emojis = emojis
        )

class Morgane(Evil):
    role = "morgane"

    async def _game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🧙‍♀️",
            description = "Vous êtes Morgane. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Perceval vous voit aux côtés de Merlin.",
            color = self.color
        )

        if len(evils):
            embed.add_field(name = "Vos co-équipiers:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Mordred(Evil):
    role = "mordred"

    async def _game_start(self, game):
        embed = discord.Embed(title = "Début de partie 😈",
            description = "Vous êtes Mordred. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Merlin ne vous connait pas.",
            color = self.color
        )

        if len(evils):
            embed.add_field(name = "Vos co-équipiers:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Oberon(Evil):
    role = "oberon"

    async def _game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie 😶",
            description = "Vous êtes Oberon. Vous devez faire échouer 3 Quêtes. Vous ne connaissez pas les méchants et les méchants ne vous connaisent pas.",
            color = self.color
        ))

class Agrav1(Evil):
    role = "agrav1"
    quest_emojis = [globals.quest_emojis["success"], globals.quest_emojis["failure"], globals.quest_emojis["reverse"]]
    quest_choices = ["Réussite", "Echec", "Inversion"]

    async def _game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie ⚔️️",
            description = "Vous êtes Agravain. Vous devez faire échouer 3 Quêtes. Vous avez la possibilité d'inverser le résultat de la quête si vous êtes dedans. Vous ne connaissez pas les méchants mais les méchants vous connaisent.",
            color = self.color
        ))

class Agrav2(Evil):
    role = "agrav2"
    quest_emojis = [globals.quest_emojis["success"], globals.quest_emojis["failure"], globals.quest_emojis["reverse"]]
    quest_choices = ["Réussite", "Echec", "Inversion"]

    async def _game_start(self, game):
        embed = discord.Embed(title = "Début de partie ⚔️️",
            description = "Vous êtes Agravain. Vous devez faire échouer 3 Quêtes. Vous avez la possibilité d'inverser le résultat de la quête si vous êtes dedans. Vous ne connaissez uniquement un méchant aléatoire mais les méchants vous connaisent.",
            color = self.color
        )

        if len(evils):
            embed.add_field(name = "Un de vos co-équipiers:",
                value = random.choice(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

# class Solo(Player):
#     allegiance = "solo"
#     color = 0x76EE00
#
#     async def team_game_start(self, game):
#         await self._game_start(game)
#
# class Venec(Solo):
#     role = "venec"
#
#     async def _game_start(self, game):
#         embed = discord.Embed(title = "Début de partie 🤘",
#             description = "Vous êtes Venec. Vous devez faire atteindre la 5e quête. Faites en sorte qu'aucun camp ne gagne avant.",
#             color = self.color
#         )
