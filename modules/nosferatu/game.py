import discord

from modules.nosferatu.roles import Hunter

import modules.nosferatu.globals as globals

class Game:
    def __init__(self, _message):
        self.channel = _message.channel
        self.players = { _message.author.id: Hunter(message.author) } #Dict pour rapidement accéder aux infos
        self.order = [], #L'ordre de jeu (liste des id des joueurs, n'inclut pas Renfield)
        self.turn = -1, #Le tour en cours (incrémente modulo le nombre de joueurs - Renfield). -1 = pas commencé
        self.clock = [ "dawn" ], #Nuits et Aurore
        self.library = [], #Morsures, Incantations, Nuits et Journaux
        self.stack = [], #Ce qui est passé à Renfield
        self.discard = [], #Ce qui est défaussé
        self.rituals = [ "mirror", "transfusion", "transfusion", "distortion", "water" ],

        for i in range(16):
            self.library.append("bite")

        for i in range(15):
            self.library.append("spell")

        for i in range(18):
            self.library.append("journal")

    #Envoies l'embed dans le channel et à tous les joueurs
    async def broadcast(self, embed, **kwargs):
        exceptions = kwargs["exceptions"] if "exceptions" in kwargs else []

        await self.channel.send(embed = embed)
        for id, player in self.players.items():
            if id not in exceptions:
                await player.user.send(embed = embed)

    #Broadcast les infos du jeu à tous les joueurs
    async def send_info(self):
        embed = discord.Embed(
            title = "Tour de `" + str(self.players[self.order[self.turn]].user) + "` (Tour " + str(self.turn + 1) + "/" + str(len(self.order)) +")",
            color = 0x000055,
            description = "Il reste " + str(len(self.rituals)) + " Rituels."
        )

        i = 0
        for id in self.order:
            value = "Main: "
            for _ in range(len(self.players[id].hand)):
                value += "🔳"

            if self.players[id].bites:
                value += "\nMorsures:"
                for _ in range(self.players[id].bites):
                    value += "🧛"

            if i == 0:
                value += "\nCe joueur a le Pieu Ancestral ✝️"

            embed.add_field(name = globals.number_emojis[i] + " `" + str(self.players[id].user) + "`",
                value = value,
                inline = False
            )
            i += 1

        value = "\n".join(globals.ritual_names[x] for x in self.rituals)
        embed.add_field(name = "Rituels restants:",
            value = value,
            inline = False
        )

        if self.turn > 0:
            last_player = self.players[self.order[self.turn - 1]]
            embed.add_field(name = "Carte défaussée par `" + str(last_player.user) + "`:",
                value = self.card_names[self.discard[-1]],
                inline = False
            )

        await self.channel.send(embed = embed)

        for id, player in self.players.items():
            if player.role != "Renfield":
                await self.send_personnal_info(player)
            else:
                await player.user.send(embed = embed)

    async def send_personnal_info(self, player):
        embed = discord.Embed(
            title = "Tour de `" + str(self.players[self.order[self.turn]].user) + "` (Tour " + str(self.turn + 1) + "/" + str(len(self.order)) +")",
            color = 0x000055,
            description = "Il reste " + str(len(self.rituals)) + " Rituels."
        )

        i = 0
        for id in self.order:
            if id == player.user.id:
                value = "Votre main:\n  "
                value += '\n  '.join([self.card_names[x] for x in player.hand])
            else:
                value = "Main: "
                for i in range(len(self.players[id].hand)):
                    value += "🔳"

            if self.players[id].bites:
                value += "\nMorsures:"
                for _ in range(self.players[id].bites):
                    value += "🧛"

            if i == 0:
                if player.user.id == id:
                    value += "\nVous avez le Pieu Ancestral ✝️"
                else:
                    value += "\nCe joueur a le Pieu Ancestral ✝️"

            embed.add_field(name = globals.number_emojis[i] + " `" + str(self.players[id].user) + "`",
                value = value,
                inline = False
            )
            i += 1

        value = "\n".join(globals.ritual_names[x] for x in self.rituals)
        embed.add_field(name = "Rituels restants:",
            value = value,
            inline = False
        )

        if self.turn > 0:
            last_player = self.players[self.order[self.turn - 1]]
            embed.add_field(name = "Carte défaussée par `" + str(last_player.user) + "`:",
                value = self.card_names[self.discard[-1]],
                inline = False
            )

        await player.user.send(embed = embed)

    async def game_start(self):
        #Détermine au hasard l'ordre et le premier joueur
        game.order = [x for x in game.players]
        game.order.remove(self.user.id)
        random.shuffle(game.order)

        #Ajouter les nuits à l'horloge et à la librairie et les mélange
        for i in range(10):
            if i < len(game.players):
                game.clock.append("night")
            else:
                game.library.append("night")

        random.shuffle(game.library)
        random.shuffle(game.clock)

        async def set_player(reactions):
            #Met à jour les rôles et les envoies
            index = reactions[self.renfield.user.id][0]
            user = game.players[game.order[index]].user
            game.players[game.order[index]] = Vampire(user)

            await self.renfield.user.send(user.name + " est maitenant le Vampire")

            for id in game.order:
                player = game.players[id]
                await player.game_start(game)

            #Tour du premier joueur
            await game.players[game.order[0]].turn_start(game)


        async def cond(reactions):
            return len(reactions[self.renfield.user.id]) == 1

        #Envoies le message de choix du vampire à Renfield
        await ReactionMessage(cond,
            set_player
        ).send(self.renfield.user,
            "Choix du Vampire",
            "",
            0xff0000,
            [game.players[x].user.name for x in game.order]
        )

    async def next_table_turn(self, stick_was_passed):
        #Mélange l'Horloge
        random.shuffle(self.clock)

        #Remet à 0 les tours
        self.turn = 0

        await self.broadcast(discord.Embed(
            title = "Début d'un nouveau tour de table",
            description = "Toutes les cartes passées à Renfield ont soit été défaussées, soit été jouées.\nL'Horloge a été mélangée" + (".\nRenfield va décider du nouveau Porteur du Pieu Ancestral" if not stick_was_passed else ""),
            color = 0x000055
        ))

        if not stick_was_passed:
            async def pass_stick(reactions):
                index = reactions[self.renfield.user.id][0] + (1 if not globals.debug else 0)
                choice = self.players[self.order[index]]

                await self.broadcast(discord.Embed(
                    title = "Passation du Pieu Ancestral",
                    description = "`" + str(self.renfield.user) + "` a passé le Pieu Ancestral à `" + str(choice.user) + "`",
                    color = 0x000055
                ))

                for i in range(index):
                    self.order.append(self.order.pop(0))

                await self.players[self.order[0]].turn_start(self)

            async def cond(reactions):
                return len(reactions[self.renfield.user.id]) == 1

            await ReactionMessage(cond,
                pass_stick
            ).send(self.renfield.user,
                "Choisis à qui tu veux passer le Pieu",
                "",
                0xffff00,
                [self.players[x].user.name for x in self.order if x != self.order[0] or globals.debug]
            )
        else:
            await self.players[self.order[0]].turn_start(self)

    async def end_game(self):
        embed = discord.Embed(
            title = "Fin de partie",
            description = "",
            color = 0xfffffe
        )

        i = 0
        for id in self.order:
            value = "Main: "
            value += '\n  '.join([self.card_names[x] for x in self.players[id].hand])

            if self.players[id].bites:
                value += "\nMorsures:"
                for _ in range(self.players[id].bites):
                    value += "🧛"

            embed.add_field(name = "`" + str(self.players[id].user) + "`",
                value = value,
                inline = False
            )
            i += 1

        if len(self.rituals):
            value = "\n".join(globals.ritual_names[x] for x in self.rituals)
            embed.add_field(name = "Rituels restants:",
                value = value,
                inline = False
            )
        else:
            embed.add_field(name = "Rituels restants:",
                value = "Aucun!",
                inline = False
            )

        await self.broadcast(embed)

        globals.games.pop(self.channel.id)
