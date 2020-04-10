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
    async def send_info():
        embed = discord.Embed(
            title = "Tour de `" + str(self.players[self.order[self.turn]].user) + "` (Tour " + str(self.turn + 1) + "/" + str(len(self.order)) +")",
            color = 0x000055,
            description = "Il reste " + str(len(self.rituals)) + " Rituels"
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
        goal = 4 if len(self.players) == 5 else 5
        total_bites = 0
        for id in self.order:
            total_bites += self.players[id].bites

        embed = discord.Embed(
            title = "Tour de `" + str(self.players[self.order[self.turn]].user) + "` (Tour " + str(self.turn + 1) + "/" + str(len(self.order)) +")",
            color = 0x000055,
            description = "Il reste " + str(len(self.rituals)) + " Rituels" + (". Il vous reste " + str(goal - total_bites) + " Morsures à placer" if player.role == "Vampire" else "")
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

    async def game_start():
        #Détermine au hasard l'ordre et le premier joueur
        self.order = [x for x in self.players]
        self.order.remove(self.user.id)
        random.shuffle(self.order)

        #Ajouter les nuits à l'horloge et à la librairie et les mélange
        for i in range(10):
            if i < len(self.players):
                self.clock.append("night")
            else:
                self.library.append("night")

        random.shuffle(self.library)
        random.shuffle(self.clock)

        async def set_vampire(reactions):
            #Met à jour les rôles et les envoies
            index = reactions[self.renfield.user.id][0]
            user = self.players[self.order[index]].user
            self.players[self.order[index]] = Vampire(user)

            await self.renfield.user.send(str(user) + " est maitenant le Vampire")

            for id in self.order:
                player = self.players[id]
                await player.self_start()

            #Tour du premier joueur
            await self.players[self.order[0]].turn_start()


        async def cond(reactions):
            return len(reactions[self.renfield.user.id]) == 1

        #Envoies le message de choix du vampire à Renfield
        await ReactionMessage(cond,
            set_vampire
        ).send(self.renfield.user,
            "Choix du Vampire",
            "",
            0xff0000,
            ["`" + str(self.players[x].user) + "`" for x in self.order]
        )

    #Le tour de table est terminé, les cartes sont étudiées en secret
    async def study_stack():
        can_make_ritual = True
        for card in self.stack:
            if card != "spell":
                can_make_ritual = False
                break

        if can_make_ritual:
            if len(self.rituals) > 1:
                player = self.players[self.order[0]]

                await self.broadcast(discord.Embed(
                    title = "Rituel réussi",
                    color = 0x00ff00,
                    description = "Toutes les cartes passées à Renfield étaient des Incantations. Le Porteur du Pieu Ancestral (`" + str(player.user) + "`) va maintenant choisir un Rituel à effectuer"
                ))

                #Envoies le stack à la défausse
                self.discard.extend(self.stack)
                self.stack.clear()

                async def cond(reactions):
                    return len(reactions[player.user.id]) == 1

                async def cond_renfield(reactions):
                    return len(reactions[self.renfield.user.id]) == 1

                #Envoies le choix du Rituel au joueur avec le Pieu (premier joueur de l'ordre de jeu)
                async def silver_mirror(reactions):
                    index = reactions[self.renfield.user.id][0] #Le choix revient à Renfield de révéler le rôle
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        title = "Résultat du Miroir d'Argent",
                        color = 0x00ff00,
                        description = "Le Miroir révèle que `" + str(choice.user) + "` est " + ("le Vampire!" if choice.role == "Vampire" else "un Chasseur")
                    ))

                    await self.check_if_stack_done()

                async def holy_water(reactions):
                    index = reactions[player.user.id][0] #Le choix revient au joueur avec le Pieu
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        title = "Résultat de l'Eau Bénite",
                        color = 0x00ff00,
                        description = "`" + str(choice.user) + "` a été aspergé d'Eau Bénite, et a donc défaussé sa main. Il a pioché autant de cartes de la défausse"
                    ))

                    hand_size = len(choice.hand)
                    self.discard.extend(choice.hand)
                    choice.hand.clear()
                    await choice.draw(self, hand_size, origin = "discard")

                    await self.check_if_stack_done()

                async def transfuse(reactions):
                    index = reactions[player.user.id][0] #Le choix revient au joueur avec le Pieu
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        title = "Résultat de la Tranfusion Sanguine",
                        color = 0x00ff00,
                        description = "`" + str(choice.user) + "` a été transfusé et a donc pioché une carte" + (". Il a toujours " + str(player.bites) + " Morsures" if player.bites else "")
                    ))

                    await choice.draw(self, 1)

                    await self.check_if_stack_done()

                async def run_ritual(reactions):
                    index = reactions[player.user.id][0]
                    ritual = self.rituals.pop(index)

                    if ritual == "distortion":
                        await self.broadcast(discord.Embed(
                            title = "Rituel effectué: 🕰️ Distortion temporelle",
                            color = 0x00ff00,
                            description = random.choice(globals.clock_faces) + " Une distortion temporelle s'empare du manoir! " + random.choice(globals.clock_faces) + "\nUne carte Nuit a été retirée de l'Horloge"
                        ))

                        index_to_remove = -1
                        while self.clock[index_to_remove] == "dawn":
                            index_to_remove -= 1

                        self.clock[index_to_remove].pop(index_to_remove)

                        print("moving on")
                        await self.check_if_stack_done()
                    elif ritual == "mirror":
                        await self.broadcast(discord.Embed(
                            title = "Rituel effectué: 🔮 Miroir d'Argent",
                            color = 0x00ff00,
                            description = "`" + str(player.user) + "` regarde dans le Miroir d'Argent pour y voir la véritable identité d'un des Chasseurs...\nRenfield va choisir un joueur dont le rôle sera révélé"
                        ))

                        await ReactionMessage(cond_renfield,
                            silver_mirror
                        ).send(self.renfield.user,
                            "Choisis le joueur dont le rôle sera révélé",
                            "",
                            0x00ff00,
                            ["`" + str(self.players[x].user) + "`" + (" (🧛)" if self.players[x].role == "Vampire" else "") for x in self.order]
                        )
                    elif ritual == "water":
                        await self.broadcast(discord.Embed(
                            title = "Rituel effectué: 🧴 Eau Bénite",
                            color = 0x00ff00,
                            description = "`" + str(player.user) + "` se saisit de l'Eau Bénite et s'apprête à purifier un membre de l'équipe\nIl va choisir un joueur qui va défausser sa main et piochera autant de la défausse"
                        ), exceptions = [player.user.id])

                        await ReactionMessage(cond,
                            holy_water
                        ).send(player.user,
                            "Choisis le joueur qui va défausser sa main et piochera autant de la défausse",
                            "",
                            0x00ff00,
                            ["`" + str(self.players[x].user) + "`" for x in self.order]
                        )
                    elif ritual == "transfusion":
                        await self.broadcast(discord.Embed(
                            title = "Rituel effectué: 💉 Transfusion Sanguine",
                            color = 0x00ff00,
                            description = "`" + str(player.user) + "` récupère la poche de sang et s'approche d'un de ses collègues pour le soigner\nIl va choisir un joueur qui va piocher une carte, mais garder les Morsures qui sont devant lui"
                        ), exceptions = [player.user.id])

                        await ReactionMessage(cond,
                            transfuse
                        ).send(player.user,
                            "Choisis le joueur qui va piocher une carte",
                            "",
                            0x00ff00,
                            ["`" + str(self.players[x].user) + "`" for x in self.order]
                        )

                await ReactionMessage(cond,
                    run_ritual
                ).send(player.user,
                    "Choisis le Rituel à effectuer",
                    "",
                    0x00ff00,
                    [globals.ritual_names[x] for x in self.rituals]
                )
            else:
                await self.broadcast(discord.Embed(
                    title = "**Victoire des Chasseurs**",
                    color = 0x00ff00,
                    description = "Toutes les cartes passées à Renfield étaient des Incantations. Tous les Rituels ont été effectués, le Vampire est anéanti par le groupe.\n**Les Chasseurs ont gagné!**"
                ))

                await self.end_game()
        else:
            #Prépare le compteur de nuit qui ont été ajoutées
            self.nights = 0

            #Mélange le stack pour brouiller les origines
            random.shuffle(self.stack)

            #Commence la boucle récursive d'étude des cartes
            await self.loop_through_stack()

    async def loop_through_stack():
        card = self.stack.pop()

        #Défausses la carte
        self.discard.append(card)

        #Si la carte est une MORSURE, envoies le choix du joueur puis le choix de la carte
        if card == "bite":
            goal = 4 if len(self.players) == 5 else 5
            total_bites = 1
            for player in self.players.values():
                if player.role != "Renfield":
                    total_bites += player.bites

            if total_bites == goal:
                await self.broadcast(discord.Embed(
                    title = "**Victoire du Mal**",
                    description = "`" + str(player.user) + "` a été mordu! Le nombre requis de Morsures ont été jouées. Le Vampire, `" + str([x for x in self.players.values() if x.role == "Vampire"][0].user) + "`, ayant désormais suffisamment d'influence, a neutralisé l'équipe des Chasseurs.\n**Le Mal a gagné!**",
                    color = 0xff0000
                ))

                await self.end_game()
            else:
                #Fonction de défausse pour le second choix
                async def discard(reactions):
                    card_index = reactions[self.renfield.user.id][0]
                    card = player.hand.pop(card_index)

                    #Préviens le joueur
                    await self.user.send("`" + str(player.user) + "` a défaussé sa carte " + self.card_names[card])
                    await player.user.send("Tu as été forcé de défausser ta carte " + self.card_names[card])

                    #Défausses la carte
                    self.discard.append(card)

                    await self.check_if_stack_done()

                #Fonction de morsure pour le premier choix
                async def bite_player(reactions):
                    index = reactions[self.renfield.user.id][0]
                    player = self.players[self.order[index]]

                    #Ajoute une Morsure au mordu
                    player.bites += 1

                    #Préviens tout le monde
                    await self.broadcast(discord.Embed(
                        title = "**Morsure!**",
                        description = "`" + str(player.user) + "` a été mordu! Renfield va choisir une carte de sa main pour la défausser",
                        color = 0xff0000
                    ))

                    #Envoies le choix de la carte à défausser
                    await ReactionMessage(cond,
                        discard
                    ).send(self.user,
                        "Choisis la carte à défausser",
                        "",
                        0xff0000,
                        [self.card_names[x] for x in player.hand]
                    )

                async def cond(reactions):
                    return len(reactions[self.user.id]) == 1

                #Envoies le message de choix du mordu à Renfield
                await ReactionMessage(cond,
                    bite_player
                ).send(self.renfield.user,
                    "Choisis qui sera mordu",
                    "Une Morsure a été jouée\n\n",
                    0xff0000,
                    ["`" + str(self.players[x].user) + "`" + (" (🧛)" if self.players[x].role == "Vampire" else "") for x in self.order]
                )
        else:
            #Rajoute la Nuit à l'Horloge et ajoute un au nombre qui ont été ajoutées
            if card == "night":
                self.clock.append(card)
                await self.broadcast(discord.Embed(
                    titre = "La Nuit s'allonge",
                    description = "Une carte Nuit a été jouée et ajoutée à l'Horloge",
                    color = 0xff0000
                ))

            #Regarde la prochaine carte
            await self.check_if_stack_done()

    async def check_if_stack_done():
        if len(self.stack):
            await self.loop_through_stack(self, self)
        else:
            if self.clock[self.turn - 1] == "dawn":
                player = self.players[self.order[0]]

                await self.broadcast(discord.Embed(
                    title = "Vote du Pieu Ancestral",
                    description = "Le tour de table s'est fini sur une Aurore. Le Porteur du Pieu Ancestral (`" + str(player.user) + "`) a donc la possibilité de l'utiliser sur un de ses collègues",
                    color = 0x00ff00
                ))

                async def cond(reactions):
                    return len(reactions[player.user.id]) == 1

                async def pass_stick(reactions):
                    index = reactions[player.user.id][0] + (1 if not globals.debug else 0)
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        title = "Passation du Pieu Ancestral",
                        description = "`" + str(player.user) + "` a passé le Pieu Ancestral à `" + str(choice.user) + "`",
                        color = 0xffff00
                    ))

                    for i in range(index):
                        self.order.append(self.order.pop(0))

                    await self.next_table_turn(True)

                async def stab_player(reactions):
                    index = reactions[player.user.id][0]
                    choice = (self.players[self.order[index]] if index < len(self.order) else None) if player.role == "Hunter" else None

                    if choice:
                        await self.broadcast(discord.Embed(
                            title = "Le Pieu Ancestral a été planté!",
                            description = "`" + str(player.user) + "` a décidé de planter le Pieu dans le coeur de `" + str(choice.user) + "`!\n" + ("Le Pieu s'enflamme et tue le Vampire sur-le-champ, ne laissant qu'un tas de cendre. **Les Chasseurs ont gagnés!**" if choice.role == "Vampire" else "Le Pieu reste silencieux alors que le Chasseur s'effondre sur le sol. Le Vampire, `" + str([x for x in self.players.values() if x.role == "Vampire"][0].user) + "`, maintenant que les autres Chasseurs sont sans défense, se révèle et termine le travail. **Le Mal a gagné!**"),
                            color = 0x00ff00 if choice.role == "Vampire" else 0xff0000
                        ))

                        await self.end_game()
                    else:
                        await self.broadcast(discord.Embed(
                            title = "Le Pieu Ancestral n'a pas été utilisé",
                            description = "`" + str(player.user) + "` a décidé de garder le Pieu pour plus tard. Il va cependant décider du joueur qui va recevoir le Pieu pour le prochain Tour",
                            color = 0xffff00
                        ))

                        await ReactionMessage(cond,
                            pass_stick
                        ).send(player.user,
                            "Choisis à qui tu veux passer le Pieu",
                            "",
                            0xffff00,
                            ["`" + str(self.players[x].user) + "`" for x in self.order if x != player.user.id or globals.debug]
                        )

                choices = ["`" + str(self.players[x].user) + "`" for x in self.order] if player.role == "Hunter" else []
                choices.append("Personne")

                await ReactionMessage(cond,
                    stab_player
                ).send(player.user,
                    "Choisis qui tu veux planter avec le Pieu Ancestral",
                    "",
                    0xffff00,
                    choices
                )
            else:
                await self.next_table_turn(False)

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

                await self.players[self.order[0]].turn_start()

            async def cond(reactions):
                return len(reactions[self.renfield.user.id]) == 1

            await ReactionMessage(cond,
                pass_stick
            ).send(self.renfield.user,
                "Choisis à qui tu veux passer le Pieu",
                "",
                0xffff00,
                ["`" + str(self.players[x].user)  + "`" for x in self.order if x != self.order[0] or globals.debug]
            )
        else:
            await self.players[self.order[0]].turn_start()

    async def end_game():
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
