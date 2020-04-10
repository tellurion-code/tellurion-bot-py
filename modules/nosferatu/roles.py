import random
import discord

from modules.nosferatu.reaction_message import ReactionMessage

import modules.nosferatu.globals as globals

class Player:
    def __init__(self, _user):
        self.user = _user


class Renfield(Player):
    role = "Renfield"


class HiddenRole(Player):

    def __init__(self, user):
        super().__init__(user)
        self.bites = 0
        self.hand = []
        self.info_message = None
        self.choice_message = None

    async def send_hand(self, game):
        info_message = await self.user.send(embed = discord.Embed(
            title = "Cartes choisies",
            color = 0xffff00,
            description = "Carte à envoyer:\n❌ Manquante\nCarte à défausser:\n❌ Manquante"
        ))

        async def send_card(reactions):
            play = self.hand[reactions[self.user.id][0]]
            discard = self.hand[reactions[self.user.id][1]]

            await self.choice_message.message.delete()
            await info_message.edit(embed = discord.Embed(
                title = "Cartes jouées ✅",
                color = 0x00ff00,
                description = "Carte envoyée:\n" + globals.card_names[play] + "\nCarte défaussée:\n" + globals.card_names[discard]
            ))

            game.stack.append(play)
            game.discard.append(discard)
            self.hand.remove(play)
            self.hand.remove(discard)

            clock_card = game.clock[game.turn]

            game.turn += 1

            if clock_card == "dawn":
                embed = discord.Embed(
                    title = "Tour de table fini (Aurore 🌅)",
                    color = 0x00ff00,
                    description = "Le tour de table a été arrêté par le lever du soleil. Les cartes données à Renfield vont être utilisées"
                )

                last_player = game.players[game.order[game.turn - 1]]
                embed.add_field(name = "Carte défaussée par `" + str(last_player.user) + "`:",
                    value = globals.card_names[game.discard[-1]],
                    inline = False
                )

                await game.broadcast(embed)
                await game.study_stack()
            elif game.turn == len(game.order):
                embed = discord.Embed(
                    title = "Tour de table fini (Tour complété 🌃)",
                    color = 0x000055,
                    description = "Le tour de table a été complété sans que le soleil ne se lève. Le Pieu ne pourra pas être utilisé. Les cartes données à Renfield vont être utilisées"
                )

                last_player = game.players[game.order[game.turn - 1]]
                embed.add_field(name = "Carte défaussée par `" + str(last_player.user) + "`:",
                    value = globals.card_names[game.discard[-1]],
                    inline = False
                )

                await game.broadcast(embed)
                await game.study_stack()
            else:
                await game.players[game.order[game.turn]].turn_start(game)

        async def cond(reactions):
            return len(reactions[self.user.id]) == 2

        async def modify_info(reactions):
            play = self.hand[reactions[self.user.id][0]] if len(reactions[self.user.id]) >= 1 else "none"
            discard = self.hand[reactions[self.user.id][1]] if len(reactions[self.user.id]) >= 2 else "none"

            await info_message.edit(embed = discord.Embed(
                title = "Carte choisies",
                color = 0xffff00,
                description = "Carte à envoyer:\n" + globals.card_names[play] + "\nCarte à défausser:\n" + globals.card_names[discard]
            ))

        self.choice_message = ReactionMessage(cond,
            send_card,
            update = modify_info
        )

        await self.choice_message.send(self.user,
            "Début de tour",
            "Choisis la carte que tu veux envoyez à Renfield, puis la carte que tu veux défausser:\n\n",
            0xffff00,
            [globals.card_names[x] for x in self.hand]
        )

    async def game_start(self, game):
        #Pioche deux cartes
        await self.draw(game, 2)

    async def turn_start(self, game):
        #Pioche deux cartes
        await self.draw(game, 2)

        #Envoies les infos de début de partie
        await game.send_info()

        #Envoies la main et le choix des cartes au joueur
        await self.send_hand(game)

    async def draw(self, game, amount, **kwargs):
        if "origin" in kwargs:
            while len(kwargs["origin"]) and amount > 0:
                self.hand.append(kwargs["origin"].pop(0))
                amount -= 1

        if amount:
            #Si le deck n'a pas assez de cartes, mélange la défausse et l'ajoute au deck
            if len(game.library) < amount:
                random.shuffle(game.discard)
                game.library.extend(game.discard)
                game.discard.clear()

                await game.broadcast(discord.Embed(
                    title = "Pioche rafraichîe",
                    description = "La défausse a été mélangée et remise dans la pioche",
                    color = 0xffffff
                ))

            #Pioche x cartes
            for i in range(amount):
                self.hand.append(game.library.pop(0))


class Hunter(HiddenRole):
    role = "Hunter"

    async def game_start(self, game):
        await super().game_start(game)

        await self.user.send(embed = discord.Embed(
            title = "Début de partie 🤠",
            color = 0x00ff00,
            description = "Tu es un Chasseur. Ton but est de tuer le Vampire avec le Pieu Ancestral, ou bien de réussir à jouer les 5 Rituels."
        ))

    async def turn_start(self, game):
        await super().turn_start(game)


class Vampire(HiddenRole):
    role = "Vampire"

    async def game_start(self, game):
        await super().game_start(game)

        await self.user.send(embed = discord.Embed(
            title = "Début de partie 🧛",
            description = "Tu es le Vampire. Tu es allié avec Renfield.\nTon but est de faire tuer un Chasseur par le Pieu Ancestral, ou bien de réussir à placer " + ("4" if len(game.players) == 5 else "5") + " Morsures.\n**Tu ne peux pas utiliser le Pieu Ancestral si tu l'as.**",
            color = 0xff0000
        ))

    async def turn_start(self, game):
        await super().turn_start(game)
