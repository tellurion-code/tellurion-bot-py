import discord
import random

from modules.avalon.reaction_message import ReactionMessage

import modules.avalon.globals as global_values


class Player:
    role = ""
    last_vote = ""
    last_choice = ""
    inspected = False
    vote_message = None
    info_message = None
    quest_emojis = []
    quest_choices = ["Réussite", "Echec"]

    def __init__(self, user):
        self.user = user

    async def game_start(self, game):
        self.quest_emojis = [global_values.quest_emojis["success"], global_values.quest_emojis["failure"]]

        await self.team_game_start(game)

        # blaise = [x for x in game.players if x.role == "blaise"]
        # if len(blaise):
        #     self.embed.add_field(name = "Père Blaise",
        #       value = "`" + str(blaise[0].user) + "``")

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed=self.embed)

        await self.post_game_start(game)

    async def post_game_start(self, game):
        pass

    async def send_vote(self, game):
        emojis = [global_values.quest_emojis["success"], global_values.quest_emojis["failure"]]
        choices = ["Pour", "Contre"]

        async def cast_vote(reactions):
            self.last_vote = emojis[reactions[self.user.id][0]] + " " + choices[reactions[self.user.id][0]]
            await game.check_vote_end()

        async def cond_player(reactions):
            return len(reactions[self.user.id]) == 1

        self.vote_message = ReactionMessage(
            cond_player,
            cast_vote,
            temporary=False
        )

        await self.vote_message.send(
            self.user,
            "Equipe proposée",
            "Le Leader `" + str(game.players[game.order[game.turn]].user) + "` a proposé comme Equipe:\n" + '\n'.join([(global_values.number_emojis[i] + ' `' + str(game.players[x].user) + '`') for i, x in game.team.items()]) + "\n\nÊtes-vous d'accord avec le départ de cette Equipe?\n",
            global_values.color,
            choices,
            validation_emoji="⭕",
            emojis=emojis,
            fields=[{
                "name": "Votes :",
                "value": ' '.join(["✉️"] * len(game.order))
            }]
        )

    async def send_choice(self, game):
        async def cast_choice(reactions):
            self.last_choice = str(self.quest_emojis[reactions[self.user.id][0]]) + " " + self.quest_choices[reactions[self.user.id][0]]
            await game.check_quest_end()

        async def cond_player(reactions):
            return len(reactions[self.user.id]) == 1

        self.vote_message = ReactionMessage(
            cond_player,
            cast_choice,
            temporary=False
        )

        await self.vote_message.send(
            self.user,
            "Quête",
            "Êtes-vous pour la réussite de la quête?",
            global_values.color,
            self.quest_choices,
            validation_emoji="⭕",
            silent=True,
            emojis=self.quest_emojis
        )


class Good(Player):
    allegiance = "good"
    role = "good"
    color = 0x2e64fe

    async def team_game_start(self, game):
        await self._game_start(game)

        galaad = [global_values.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role == "galaad"]
        if len(galaad):
            self.embed.add_field(
                name="🙋 Galaad",
                value='\n'.join(galaad))

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 🟦",
            description="Vous êtes un Fidèle Vassal d'Arthur (Gentil). Vous devez faire réussir 3 Quêtes.",
            color=self.color)


class Merlin(Good):
    role = "merlin"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 🧙‍♂️",
            description="Vous êtes Merlin. Vous devez faire réussir 3 Quêtes et ne pas vous révéler. Vous connaissez les méchants.",
            color=self.color)

        evils = [global_values.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "mordred" or game.players[x].role == "karadoc"]
        if len(evils):
            self.embed.add_field(
                name="Vos ennemis :",
                value='\n'.join(evils))


class Percival(Good):
    role = "percival"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 🤴",
            description="Vous êtes Perceval. Vous devez faire réussir 3 Quêtes et protéger Merlin. Vous connaissez Merlin et Morgane.",
            color=self.color)

        mages = [global_values.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role in ["merlin", "morgane"]]
        if len(mages):
            self.embed.add_field(
                name="Les mages :",
                value='\n'.join(mages))


class Gawain(Good):
    role = "gawain"
    quest_choices = ["Réussite", "Inversion"]

    async def _game_start(self, game):
        self.quest_emojis = [global_values.quest_emojis["success"], global_values.quest_emojis["reverse"]]

        self.embed = discord.Embed(
            title="Début de partie ️🛡️",
            description="Vous êtes Gauvain. Vous devez faire réussir 3 Quêtes. Vous avez la possibilité d'inverser le résultat de la quête si vous êtes dedans.",
            color=self.color)


class Karadoc(Good):
    role = "karadoc"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie ️🥴",
            description="Vous êtes Karadoc. Vous devez faire réussir 3 Quêtes et protéger Merlin. Merlin vous voit comme un méchant.",
            color=self.color)


class Galaad(Good):
    role = "galaad"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie ️🙋",
            description="Vous êtes Galaad. Vous devez faire réussir 3 Quêtes. En tant que fils de Lancelot, les gentils vous connaissent.",
            color=self.color)


class Uther(Good):
    role = "uther"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie ️👨‍🦳",
            description="Vous êtes Uther. Vous devez faire réussir 3 Quêtes. Vous pouvez choisir un joueur dont vous connaîtrez le rôle.",
            color=self.color)

    async def post_game_start(self, game):
        valid_candidates = [x for x in game.order if x != self.user.id]
        emojis = [global_values.number_emojis[game.order.index(x)] for x in valid_candidates]
        choices = ["`" + str(game.players[x].user) + "`" for x in valid_candidates]

        async def inspect_role(reactions):
            inspected = game.players[valid_candidates[reactions[self.user.id][0]]]

            await inspection_message.message.edit(embed=discord.Embed(
                title="🔍 Inspection",
                description="Vous avez inspecté `" + str(inspected.user) + "` qui se révèle être " + global_values.visual_roles[inspected.role],
                color=global_values.color))

        async def cond(reactions):
            return len(reactions[self.user.id]) == 1

        inspection_message = ReactionMessage(
            cond,
            inspect_role,
            temporary=False
        )

        await inspection_message.send(
            self.user,
            "Choisissez le joueur que vous souhaitez inspecter",
            "",
            global_values.color,
            choices,
            emoji=emojis
        )

class Arthur(Good):
    role = "arthur"
    quest_choices = ["Réussite", "Echec", "Annulation"]

    async def _game_start(self, game):
        self.quest_emojis = [global_values.quest_emojis["success"], global_values.quest_emojis["failure"], global_values.quest_emojis["cancel"]]

        self.embed = discord.Embed(
            title="Début de partie 👑",
            description="Vous êtes Arthur. Vous devez faire réussir 3 Quêtes. Vous avez la possibilité d'annuler la quête si vous êtes dedans.",
            color=self.color)


# class Blaise(Good):
#     role = "blaise"
#
#     async def _game_start(self, game):
#         self.embed = discord.Embed(title = "Début de partie ️✍️",
#             description = "Vous êtes Blaise. Vous devez faire réussir 3 Quêtes. Tout le monde vous connait, et vousne pouvez pas être dans une quête. A chaque quête, vous connaissez le choix d'une personne au choix.",
#             color = self.color
#         )


class Evil(Player):
    allegiance = "evil"
    role = "evil"
    evils = []
    color = 0xef223f

    async def team_game_start(self, game):
        await self._game_start(game)

        evils = [global_values.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "oberon"]
        if len(evils):
            self.embed.add_field(
                name="Vos co-équipiers :",
                value='\n'.join(evils))

        lancelot = [global_values.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role in ["agrav1", "agrav2"]]
        if len(lancelot):
            self.embed.add_field(
                name="Lancelot ⚔️️",
                value='\n'.join(evils))

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 🟥",
            description="Vous êtes un Serviteur de Mordred (Méchant). Vous devez faire échouer 3 Quêtes.",
            color=self.color)


class Assassin(Evil):
    role = "assassin"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 🗡️",
            description="Vous êtes l'Assassin. Vous devez faire échouer 3 Quêtes ou trouver Merlin et l'assassiner.",
            color=self.color)

    async def send_assassin_choice(self, game):
        valid_candidates = [x for x in game.order if game.players[x].allegiance != "evil"]
        emojis = [global_values.number_emojis[game.order.index(x)] for x in valid_candidates]
        choices = ["`" + str(game.players[x].user) + "`" for x in valid_candidates]

        async def kill(reactions):
            killed = game.players[valid_candidates[reactions[self.user.id][0]]]

            if killed.role == "merlin":
                await game.end_game(False, "assassinat de Merlin (`" + str(killed.user) + "`)")
            elif killed.role == "elias":
                await game.end_game(global_values.visual_roles[killed.role], "usurpation (`" + str(killed.user) + "`)")
            else:
                await game.end_game(True, "3 Quêtes réussies (Assassinat de `" + str(killed.user) + "` qui était " + global_values.visual_roles[killed.role] + ")")

        async def cond(reactions):
            return len(reactions[self.user.id]) == 1

        await ReactionMessage(
            cond,
            kill
        ).send(
            self.user,
            "Choisissez qui vous souhaitez tuer",
            "",
            global_values.color,
            choices,
            emojis=emojis)


class Morgane(Evil):
    role = "morgane"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 🧙‍♀️",
            description="Vous êtes Morgane. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Vous apparaissez aux yeux de Perceval.",
            color=self.color)


class Mordred(Evil):
    role = "mordred"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 😈",
            description="Vous êtes Mordred. Vous devez faire échouer 3 Quêtes ou trouver Merlin. Merlin ne vous connait pas.",
            color=self.color)


class Oberon(Evil):
    role = "oberon"

    async def team_game_start(self, game):
        await self._game_start(game)

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 😶",
            description="Vous êtes Oberon. Vous devez faire échouer 3 Quêtes. Vous ne connaissez pas les méchants et les méchants ne vous connaisent pas.",
            color=self.color)


class Lancelot(Evil):
    role = "lancelot"
    quest_choices = ["Réussite", "Inversion"]

    async def team_game_start(self, game):
        await self._game_start(game)

    async def _game_start(self, game):
        self.quest_emojis = [global_values.quest_emojis["success"], global_values.quest_emojis["reverse"]]

        self.embed = discord.Embed(
            title="Début de partie ⚔️️",
            description="Vous êtes Lancelot. Vous devez faire échouer 3 Quêtes. Vous avez la possibilité d'inverser le résultat de la quête si vous êtes dedans. Vous ne connaissez uniquement un méchant aléatoire mais les méchants vous connaisent en tant que Lancelot.",
            color=self.color)

        if game.game_rules["lancelot_know_evil"]:
            evils = [global_values.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].allegiance == "evil" and game.players[x].role != "oberon" and game.players[x].user.id != self.user.id]
            if len(evils):
                self.embed.add_field(
                    name="Un de vos co-équipiers :",
                    value=random.choice(evils))


class Solo(Player):
    allegiance = "solo"
    color = 0x76ee00

    async def team_game_start(self, game):
        await self._game_start(game)


class Elias(Solo):
    role = "elias"

    async def _game_start(self, game):
        self.embed = discord.Embed(
            title="Début de partie 🧙",
            description="Vous êtes Elias. Vous devez vous faire assassiner pour prendre la place de Merlin. Vous connaissez Merlin.",
            color=self.color
        )

        merlin = [global_values.number_emojis[i] + " `" + str(game.players[x].user) + "`" for i, x in enumerate(game.order) if game.players[x].role == "merlin"]
        if len(merlin):
            self.embed.add_field(
                name="Merlin :",
                value=random.choice(merlin))


# class Maleagant(Solo):
#     role = "maleagant"
#
#     async def _game_start(self, game):
#         self.embed = discord.Embed(title = "Début de partie 🧿",
#             description = "Vous êtes Méléagant. A chaque quête, vous devrez parier sur sa réussite ou son échec. Si vous faites un sans-faute, vous gagnez seul. Sinon, vous devrez gagner avec les méchants.",
#             color = self.color
#         )
