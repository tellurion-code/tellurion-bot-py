import discord

from modules.avalon.reaction_message import ReactionMessage

import modules.avalon.globals as globals

class Player:
    role = ""
    last_vote = ""
    inspected = False
    vote_message = None
    info_message = None
    quest_emojis = ["✅", "❌"]
    quest_choices = ["Réussite", "Echec"]

    def __init__(self, user):
        self.user = user

    async def send_vote(self, game):
        emojis = ["✅", "❎"]
        choices = ["Pour", "Contre"]

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
            "Equipe proposée",
            "Le Leader `" + str(game.players[game.order[game.turn]].user) + "` a proposé comme Equipe `" + ', '.join([globals.number_emojis[i] + ' `' + str(game.players[x].user) + '`' for i, x in game.team.items()]) + "`. Êtes-vous d'accord avec le départ ce cet Equipe?\n\n",
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
            self.last_vote = self.quest_emojis[reactions[self.user.id][0]] + self.quest_choices[reactions[self.user.id][0]]
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
    allegeance = "good"
    role = "good"

    async def game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie 🟦",
            description = "Vous êtes un Gentil. Vous devez faire réussir 3 Quêtes.",
            color = 0x2e64fe
        ))
