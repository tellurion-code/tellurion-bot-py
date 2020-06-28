import discord

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

    async def game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie 🟦",
            description = "Vous êtes un Gentil. Vous devez faire réussir 3 Quêtes.",
            color = 0x2e64fe
        ))

class Merlin(Good):
    role = "merlin"

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🧙‍♂️",
            description = "Vous êtes Merlin. Vous devez faire réussir 3 Quêtes et ne pas vous révéler. Vous connaissez les méchants:",
            color = 0x2e64fe
        )

        evils = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "mordred"]
        if len(evils):
            embed.add_field(name = "Vos ennemis:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Percival(Good):
    role = "percival"

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🤴",
            description = "Vous êtes Perceval. Vous devez faire réussir 3 Quêtes et protéger Merlin. Vous connaissez Merlin et Morgane:",
            color = 0x2e64fe
        )

        mages = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role in ["merlin", "morgane"]]
        if len(mages):
            embed.add_field(name = "Les mages:",
                value = '\n'.join(mages)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Evil(Player):
    allegiance = "evil"
    role = "evil"

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🟥",
            description = "Vous êtes un Méchant. Vous devez faire échouer 3 Quêtes.",
            color = 0xef223f
        )

        evils = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "oberon"]
        if len(evils):
            embed.add_field(name = "Vos co-équipiers:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Assassin(Evil):
    role = "assassin"

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🗡️",
            description = "Vous êtes l'Assassin. Vous devez faire échouer 3 Quêtes ou trouver Merlin et l'assassiner.",
            color = 0xef223f
        )

        evils = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "oberon"]
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

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie 🧙‍♀️",
            description = "Vous êtes Morgane. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Perceval vous voit aux côtés de Merlin.",
            color = 0xef223f
        )

        evils = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "oberon"]
        if len(evils):
            embed.add_field(name = "Vos co-équipiers:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Mordred(Evil):
    role = "mordred"

    async def game_start(self, game):
        embed = discord.Embed(title = "Début de partie 😈",
            description = "Vous êtes Mordred. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Merlin ne vous connait pas.",
            color = 0xef223f
        )

        evils = [globals.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "oberon"]
        if len(evils):
            embed.add_field(name = "Vos co-équipiers:",
                value = '\n'.join(evils)
            )

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = embed)

class Oberon(Evil):
    role = "oberon"

    async def game_start(self, game):
        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed = discord.Embed(title = "Début de partie 😶",
            description = "Vous êtes Oberon. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Vous ne connaissez pas les méchants et les méchants ne vous connaisent pas.",
            color = 0xef223f
        ))
