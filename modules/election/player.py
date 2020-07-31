import discord
import random

from modules.reaction_message.reaction_message import ReactionMessage

import modules.election.globals as global_values


class Player:
    name = "💼 Joueur"
    description = "Vous êtes un Joueur. Vous n'avez de pouvoirs spéciaux. Vous devez ne pas être éliminé avant la fin du jeu"
    last_vote = -1
    vote_message = None
    info_message = None
    alive = True
    votes = 0
    bonus = 0

    def __init__(self, user):
        self.user = user
        self.cant_vote = []
        self.embed = None

    async def game_start(self, game):
        self.embed = discord.Embed(
            title=self.name.split()[0] + " Début de partie",
            description=self.description,
            color=global_values.color
        )

        scientists = ["`" + str(x.user) + "`" for x in game.players.values() if x.__class__.__name__ in ["Scientist", "Raoult"]]
        if len(scientists):
            self.embed.add_field(
                name="Scientifiques",
                value='\n'.join(scientists)
            )

        self.add_info(game)

        await self.user.send("||\n\n\n\n\n\n\n\n\n\n||", embed=self.embed)

        await self.post_game_start(game)

    def add_info(self, game):
        pass

    async def post_game_start(self, game):
        pass

    async def send_vote(self, game, **kwargs):
        if await self.other_choice(game):
            return

        choices = [i for i in kwargs["choice"] if game.order[i] not in self.cant_vote and (game.order[i] != self.user.id or global_values.debug)] if "choice" in kwargs else [i for i, x in enumerate(game.order) if x != self.user.id and game.players[x].alive and x not in self.cant_vote]

        async def cast_vote(reactions):
            self.last_vote = choices[reactions[self.user.id][0]]
            await self.vote_power(game)
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
            "Phase de vote",
            "Choisissez pour qui vous souhaitez voter" + (". Vous avez un bonus de " + str(self.bonus) if self.bonus else ""),
            global_values.color,
            ["`" + str(game.players[game.order[i]].user) + "`" for i in choices],
            emojis=[global_values.number_emojis[i] for i in choices],
            fields=[{
                "name": "Votes :",
                "value": ' '.join(["✉️"] * len(game.order))
            }]
        )

    async def other_choice(self, game):
        pass

    async def vote_power(self, game):
        pass

    async def on_kill(self, game, id):
        return "", False

    async def on_tie(self, game, tied):
        return "", False, False


class Martyr(Player):
    name = "🤕 Martyr"
    description = "Vous êtes le Martyr. Vous devez vous faire éliminer avant votre cible. Si votre cible est éliminée, vous serez éliminé à sa place"
    variables = {
        "target": -1
    }

    def add_info(self, game):
        while True:
            self.variables["target"] = random.choice(game.order)
            if self.variables["target"] != self.user.id:
                break

        if not global_values.debug:
            self.cant_vote.append(self.variables["target"])

        self.embed.add_field(
            name="Cible",
            value="`" + str(game.players[self.variables["target"]].user) + "`"
        )

    async def on_kill(self, game, id):
        if id == self.variables["target"]:
            game.players[id].alive = True
            self.variables["target"] = -1

            return " Le Martyr `" + str(self.user) + "` a été tué à la place de sa cible.", await game.eliminate(self.user.id)
        elif id == self.user.id and self.variables["target"] != -1:
            if game.players[self.variables["target"]].alive:
                await game.end_game(str(self.user), "Sacrifice")

                return " Le Martyr a été tué avant sa cible.", True

        return "", False

class Lobbyist(Player):
    name = "🧐 Lobbyiste"
    description = "Vous êtes le lobbyiste. Vous devez ne pas être éliminé avant la fin. Chaque tour, vous pouvez parier sur la personne qui sera éliminé pour gagner une voix en plus au prochain tour. Si vous avez faux, vous prendrez un malus d'une voix au prochain tour"
    variables = {
        "guess": -1
    }

    async def other_choice(self, game):
        if self.variables["guess"] != -1 or not self.alive:
            return False

        choices = [i for i, x in enumerate(game.order) if game.players[x].alive]
        visual_choices = ["`" + str(game.players[game.order[i]].user) + "`" for i in choices]
        emojis = [global_values.number_emojis[i] for i in choices]

        choices.append("-1")
        visual_choices.append("Personne")
        emojis.append("🚫")

        async def choose(reactions):
            if reactions[self.user.id][0] + 1 < len(choices):
                self.variables["guess"] = game.order[choices[reactions[self.user.id][0]]]
            else:
                self.variables["guess"] = -2
            await self.send_vote(game)

        async def cond(reactions):
            return len(reactions[self.user.id]) == 1

        await ReactionMessage(
            cond,
            choose
        ).send(
            self.user,
            "🧐 Pouvoir du Lobbyiste",
            "Choisissez sur qui vous souhaitez parier",
            global_values.color,
            visual_choices,
            emojis=emojis
        )

        return True

    async def on_kill(self, game, id):
        if self.variables["guess"] > -1 and self.alive:
            self.bonus += 1 if id == self.variables["guess"] else -1

        self.variables["guess"] = -1

        return "", False


class Scientist(Player):
    name = "🥼 Scientifique"
    description = "Vous êtes le scientifique. Vous devez ne pas être éliminé avant la fin. Tous les joueurs vous connaîssent. Vous connaissez le rôle de la personne éliminée chaque tour"

    async def on_kill(self, game, id):
        if self.alive:
            await self.user.send(embed=discord.Embed(
                title="🥼 Pouvoir du Scientifique",
                description="Le joueur éliminé, `" + str(game.players[id].user) + "`, avait comme rôle " + game.players[id].name,
                color=global_values.color
            ))

        return "", False


class Raoult(Player):
    name = "👔 Raoult"
    description = "Vous êtes Raoult. Vous devez ne pas être éliminé avant la fin. Tous les joueurs vous connaissent aux côtés du Scientifique"


class Corruptor(Player):
    name = "🤑 Corrupteur"
    description = "Vous êtes le corrupteur. Vous devez ne pas être éliminé avant la fin. Chaque tour, vous pouvez retirer une voix à un autre joueur pour la donner à un troisième. Vous serez éliminé instantannément en cas d'égalité"
    variables = {
        "transfered": False
    }

    async def other_choice(self, game):
        if game.tied or self.variables["transfered"] or len([0 for x in game.players if x.alive]) < 2 or not self.alive:
            return False

        choices = [i for i, x in enumerate(game.order) if game.players[x].alive and (x != self.user.id or global_values.debug)]
        visual_choices = ["`" + str(game.players[game.order[i]].user) + "`" for i in choices]
        emojis = [global_values.number_emojis[i] for i in choices]

        choices.append("-1")
        visual_choices.append("Personne")
        emojis.append("🚫")

        async def transfer(reactions):
            if (len(choices) - 1) not in reactions[self.user.id]:
                game.players[game.order[choices[reactions[self.user.id][0]]]].bonus -= 1
                game.players[game.order[choices[reactions[self.user.id][1]]]].bonus += 1

            self.variables["transfered"] = True

            await self.send_vote(game)

        async def cond(reactions):
            return len(reactions[self.user.id]) == 2 or (len(choices) - 1) in reactions[self.user.id]

        await ReactionMessage(
            cond,
            transfer
        ).send(
            self.user,
            "🤑 Pouvoir du Lobbyiste",
            "Choisissez de qui à qui vous voulez transférer une voix. Le premier joueur choisi aura -1 voix et le second +1 voix",
            global_values.color,
            visual_choices,
            emojis=emojis
        )

        return True

    async def on_tie(self, game, tied):
        return "\nLe Corrupteur a été éliminé par défaut.", True, await game.eliminate(self.user.id)

    async def on_kill(self, game, id):
        self.variables["transfered"] = False

        return "", False


class Journalist(Player):
    name = "📰 Journaliste"
    description = "Vous êtes le journaliste. Vous devez ne pas être éliminé avant la fin. Vous connaissez le rôle de ceux pour qui vous votez. Ils savent que le journaliste a voté pour eux"

    async def vote_power(self, game):
        if not game.tied:
            await self.user.send(embed=discord.Embed(
                title="📰 Pouvoir du Journaliste",
                description="Vous avez appris que `" + str(game.players[game.order[self.last_vote]].user) + "` a comme rôle " + game.players[game.order[self.last_vote]].name,
                color=global_values.color
            ))

            await game.players[game.order[self.last_vote]].user.send(embed=discord.Embed(
                description="Le Journaliste a voté pour vous et a appris votre rôle",
                color=global_values.color
            ))


class Le_Pen(Player):
    name = str(global_values.le_pen_emoji) + " Le Pen"
    description = "Vous êtes Le Pen. Vous devez ne pas être éliminé avant la fin. Vous gagnez si vous êtes éliminé au dernier tour au lieu de le remporter"

    def __init__(self, user):
        super().__init__(user)
        self.name = str(global_values.le_pen_emoji) + " Le Pen"

    async def on_kill(self, game, id):
        if len([0 for x in game.players.values() if x.alive]) == 1:
            if id == self.user.id:
                await game.end_game(str(self.user), "Elimination")
            else:
                await game.end_game(str(game.players[id].user), "Echec de Le Pen")

            return "", True

        return "", False
