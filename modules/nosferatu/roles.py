import random
import discord

from modules.nosferatu.reaction_message import ReactionMessage

import modules.nosferatu.globals as globals

class Player:
    card_names = {
        "bite": "🧛 Morsure",
        "spell": "📖 Incantation",
        "journal": "🧾 Journal",
        "night": "🌃 Nuit",
        "none": "❌ Manquante"
    }

    def __init__(self, _user):
        self.user = _user


class Renfield(Player):
    role = "Renfield"

    #Le tour de table est terminé, les cartes sont étudiées en secret
    async def study_stack(self, game):
        can_make_ritual = True
        for card in game.stack:
            if card != "spell":
                can_make_ritual = False
                break

        if can_make_ritual:
            if len(game.rituals) > 1:
                player = game.players[game.order[0]]

                await game.broadcast(discord.Embed(
                    title = "Rituel réussi",
                    color = 0x00ff00,
                    description = "Toutes les cartes passées à Renfield étaient des Incantations. Le Porteur du Pieu Ancestral (`" + str(player.user) + "`) va maintenant choisir un Rituel à effectuer"
                ))

                #Envoies le stack à la défausse
                game.discard.extend(game.stack)
                game.stack.clear()

                async def cond(reactions):
                    return len(reactions[player.user.id]) == 1

                async def cond_renfield(reactions):
                    return len(reactions[self.user.id]) == 1

                #Envoies le choix du Rituel au joueur avec le Pieu (premier joueur de l'ordre de jeu)
                async def silver_mirror(reactions):
                    index = reactions[self.user.id][0] #Le choix revient à Renfield de révéler le rôle
                    choice = game.players[game.order[index]]

                    await game.broadcast(discord.Embed(
                        title = "Résultat du Miroir d'Argent",
                        color = 0x00ff00,
                        description = "Le Miroir révèle que `" + choice.user.name + "` est " + ("le Vampire!" if choice.role == "Vampire" else "un Chasseur")
                    ))

                    await self.check_if_stack_done(game)

                async def holy_water(reactions):
                    index = reactions[player.user.id][0] #Le choix revient au joueur avec le Pieu
                    choice = game.players[game.order[index]]

                    await game.broadcast(discord.Embed(
                        title = "Résultat de l'Eau Bénite",
                        color = 0x00ff00,
                        description = "`" + choice.user.name + "` a été aspergé d'Eau Bénite, et a donc défaussé sa main. Il a pioché autant de cartes de la défausse"
                    ))

                    hand_size = len(choice.hand)
                    game.discard.extend(choice.hand)
                    choice.hand.clear()
                    await choice.draw(game, hand_size, origin = "discard")

                    await self.check_if_stack_done(game)

                async def transfuse(reactions):
                    index = reactions[player.user.id][0] #Le choix revient au joueur avec le Pieu
                    choice = game.players[game.order[index]]

                    await game.broadcast(discord.Embed(
                        title = "Résultat de la Tranfusion Sanguine",
                        color = 0x00ff00,
                        description = "`" + choice.user.name + "` a été transfusé et a donc pioché une carte" + (". Il a toujours " + str(player.bites) + " Morsures" if player.bites else "")
                    ))

                    await choice.draw(game, 1)

                    await self.check_if_stack_done(game)

                async def run_ritual(reactions):
                    index = reactions[player.user.id][0]
                    ritual = game.rituals.pop(index)

                    if ritual == "distortion":
                        await game.broadcast(discord.Embed(
                            title = "Rituel effectué: 🕰️ Distortion temporelle",
                            color = 0x00ff00,
                            description = random.choice(globals.clock_faces) + " Une distortion temporelle s'empare du manoir! " + random.choice(globals.clock_faces) + "\nUne carte Nuit a été retirée de l'Horloge"
                        ))

                        index_to_remove = -1
                        while game.clock[index_to_remove] == "dawn":
                            index_to_remove -= 1

                        game.clock[index_to_remove].pop(index_to_remove)

                        print("moving on")
                        await self.check_if_stack_done(game)
                    elif ritual == "mirror":
                        await game.broadcast(discord.Embed(
                            title = "Rituel effectué: 🔮 Miroir d'Argent",
                            color = 0x00ff00,
                            description = "`" + str(player.user) + "` regarde dans le Miroir d'Argent pour y voir la véritable identité d'un des Chasseurs...\nRenfield va choisir un joueur dont le rôle sera révélé"
                        ))

                        await ReactionMessage(cond_renfield,
                            silver_mirror
                        ).send(self.user,
                            "Choisis le joueur dont le rôle sera révélé",
                            "",
                            0x00ff00,
                            [game.players[x].user.name + (" (🧛)" if game.players[x].role == "Vampire" else "") for x in game.order]
                        )
                    elif ritual == "water":
                        await game.broadcast(discord.Embed(
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
                            [game.players[x].user.name for x in game.order]
                        )
                    elif ritual == "transfusion":
                        await game.broadcast(discord.Embed(
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
                            [game.players[x].user.name for x in game.order]
                        )

                await ReactionMessage(cond,
                    run_ritual
                ).send(player.user,
                    "Choisis le Rituel à effectuer",
                    "",
                    0x00ff00,
                    [globals.ritual_names[x] for x in game.rituals]
                )
            else:
                await game.broadcast(discord.Embed(
                    title = "**Victoire des Chasseurs**",
                    color = 0x00ff00,
                    description = "Toutes les cartes passées à Renfield étaient des Incantations. Tous les Rituels ont été effectués, le Vampire est anéanti par le groupe.\n**Les Chasseurs ont gagné!**"
                ))

                await game.end_game()
        else:
            #Prépare le compteur de nuit qui ont été ajoutées
            self.nights = 0

            #Mélange le stack pour brouiller les origines
            random.shuffle(game.stack)

            #Commence la boucle récursive d'étude des cartes
            await self.loop_through_stack(game)

    async def loop_through_stack(self, game):
        card = game.stack.pop()

        #Défausses la carte
        game.discard.append(card)

        #Si la carte est une MORSURE, envoies le choix du joueur puis le choix de la carte
        if card == "bite":
            goal = 4 if len(game.players) == 5 else 5
            total_bites = 1
            for player in game.players.values():
                if player.role != "Renfield":
                    total_bites += player.bites

            if total_bites == goal:
                await game.broadcast(discord.Embed(
                    title = "**Victoire du Mal**",
                    description = "`" + str(player.user) + "` a été mordu! Le nombre requis de Morsures ont été jouées. Le Vampire, `" + str([x for x in game.players.values() if x.role == "Vampire"][0].user) + "`, ayant désormais suffisamment d'influence, a neutralisé l'équipe des Chasseurs.\n**Le Mal a gagné!**",
                    color = 0xff0000
                ))

                await self.end_game(game)
            else:
                #Fonction de défausse pour le second choix
                async def discard(reactions):
                    card_index = reactions[self.user.id][0]
                    card = player.hand.pop(card_index)

                    #Préviens le joueur
                    await self.user.send("`" + str(player.user) + "` a défaussé sa carte " + self.card_names[card])
                    await player.user.send("Tu as été forcé de défausser ta carte " + self.card_names[card])

                    #Défausses la carte
                    game.discard.append(card)

                    await self.check_if_stack_done(game)

                #Fonction de morsure pour le premier choix
                async def bite_player(reactions):
                    index = reactions[self.user.id][0]
                    player = game.players[game.order[index]]

                    #Ajoute une Morsure au mordu
                    player.bites += 1

                    #Préviens tout le monde
                    await game.broadcast(discord.Embed(
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
                ).send(self.user,
                    "Choisis qui sera mordu",
                    "Une Morsure a été jouée\n\n",
                    0xff0000,
                    [game.players[x].user.name + (" (🧛)" if game.players[x].role == "Vampire" else "") for x in game.order]
                )
        else:
            #Rajoute la Nuit à l'Horloge et ajoute un au nombre qui ont été ajoutées
            if card == "night":
                game.clock.append(card)
                await game.broadcast(discord.Embed(
                    titre = "La Nuit s'allonge",
                    description = "Une carte Nuit a été jouée et ajoutée à l'Horloge",
                    color = 0xff0000
                ))

            #Regarde la prochaine carte
            await self.check_if_stack_done(game)

    async def check_if_stack_done(self, game):
        if len(game.stack):
            await self.loop_through_stack(self, game)
        else:
            if game.clock[game.turn - 1] == "dawn":
                player = game.players[game.order[0]]

                await game.broadcast(discord.Embed(
                    title = "Vote du Pieu Ancestral",
                    description = "Le tour de table s'est fini sur une Aurore. Le Porteur du Pieu Ancestral (`" + str(player.user) + "`) a donc la possibilité de l'utiliser sur un de ses collègues",
                    color = 0x00ff00
                ))

                async def cond(reactions):
                    return len(reactions[player.user.id]) == 1

                async def pass_stick(reactions):
                    index = reactions[player.user.id][0] + (1 if not globals.debug else 0)
                    choice = game.players[game.order[index]]

                    await game.broadcast(discord.Embed(
                        title = "Passation du Pieu Ancestral",
                        description = "`" + str(player.user) + "` a passé le Pieu Ancestral à `" + choice.user.name + "`",
                        color = 0xffff00
                    ))

                    for i in range(index):
                        game.order.append(game.order.pop(0))

                    await game.next_table_turn(True)

                async def stab_player(reactions):
                    index = reactions[player.user.id][0]
                    choice = (game.players[game.order[index]] if index < len(game.order) else None) if player.role == "Hunter" else None

                    if choice:
                        await game.broadcast(discord.Embed(
                            title = "Le Pieu Ancestral a été planté!",
                            description = "`" + str(player.user) + "` a décidé de planter le Pieu dans le coeur de `" + str(choice.user) + "`!\n" + ("Le Pieu s'enflamme et tue le Vampire sur-le-champ, ne laissant qu'un tas de cendre. **Les Chasseurs ont gagnés!**" if choice.role == "Vampire" else "Le Pieu reste silencieux alors que le Chasseur s'effondre sur le sol. Le Vampire, `" + str([x for x in game.players.values() if x.role == "Vampire"][0].user) + "`, maintenant que les autres Chasseurs sont sans défense, se révèle et termine le travail. **Le Mal a gagné!**"),
                            color = 0x00ff00 if choice.role == "Vampire" else 0xff0000
                        ))

                        await self.end_game(game)
                    else:
                        await game.broadcast(discord.Embed(
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
                            [game.players[x].user.name for x in game.order if x != player.user.id or globals.debug]
                        )

                choices = [game.players[x].user.name for x in game.order] if player.role == "Hunter" else []
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
                await game.next_table_turn(False)


class HiddenRole(Player):

    def __init__(self, user):
        super().__init__(user)
        self.bites = 0
        self.hand = []

    async def send_hand(self, game):
        info_message = await self.user.send(embed = discord.Embed(
            title = "Cartes choisies",
            color = 0xffff00,
            description = "Carte à envoyer:\n❌ Manquante\nCarte à défausser:\n❌ Manquante"
        ))

        async def send_card(reactions):
            play = self.hand[reactions[self.user.id][0]]
            discard = self.hand[reactions[self.user.id][1]]

            await info_message.edit(embed = discord.Embed(
                title = "Cartes jouées ✅",
                color = 0x00ff00,
                description = "Carte envoyée:\n" + self.card_names[play] + "\nCarte défaussée:\n" + self.card_names[discard]
            ))

            game.stack.append(play)
            game.discard.append(discard)
            self.hand.remove(play)
            self.hand.remove(discard)

            clock_card = game.clock[game.turn]

            game.turn += 1

            if clock_card == "dawn":
                await game.broadcast(discord.Embed(
                    title = "Tour de table fini (Aurore 🌅)",
                    color = 0x00ff00,
                    description = "Le tour de table a été arrêté par le lever du soleil. Les cartes données à Renfield vont être utilisées"
                ))
                await [x for x in game.players.values() if x.role == "Renfield"][0].study_stack(game)
            elif game.turn == len(game.order):
                await game.broadcast(discord.Embed(
                    title = "Tour de table fini (Tour complété 🌃)",
                    color = 0x000055,
                    description = "Le tour de table a été complété sans que le soleil ne se lève. Le Pieu ne pourra pas être utilisé. Les cartes données à Renfield vont être utilisées"
                ))
                await [x for x in game.players.values() if x.role == "Renfield"][0].study_stack(game)
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
                description = "Carte à envoyer:\n" + self.card_names[play] + "\nCarte à défausser:\n" + self.card_names[discard]
            ))

        await ReactionMessage(cond,
            send_card,
            update = modify_info
        ).send(self.user,
            "Début de tour",
            "Choisis la carte que tu veux envoyez à Renfield, puis la carte que tu veux défausser:\n\n",
            0xffff00,
            [self.card_names[x] for x in self.hand]
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
            while len(game[kwargs["origin"]]) and amount > 0:
                self.hand.append(game[kwargs["origin"]].pop(0))
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

        goal = 4 if len(game.players) == 5 else 5
        total_bites = 0
        for player in game.players.values():
            if player.role != "Renfield":
                total_bites += player.bites

        await self.user.send("Il reste " + str(goal - total_bites) + " Morsures à placer.")
