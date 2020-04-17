import discord
import random

from modules.nosferatu.roles import Renfield, Hunter, Vampire
from modules.nosferatu.reaction_message import ReactionMessage

import modules.nosferatu.globals as globals

class Game:
    def __init__(self, _message):
        self.channel = _message.channel
        self.players = { _message.author.id: Hunter(_message.author) } #Dict pour rapidement accéder aux infos
        self.order = [] #L'ordre de jeu (liste des id des joueurs, n'inclut pas Renfield)
        self.turn = -1 #Le tour en cours (incrémente modulo le nombre de joueurs - Renfield). -1 = pas commencé
        self.clock = [ "dawn" ] #Nuits et Aurore
        self.library = [] #Morsures, Incantations, Nuits et Journaux
        self.stack = [] #Ce qui est passé à Renfield
        self.discard = [] #Ce qui est défaussé
        self.discard_stack = [] #Ce qui a été défaussé durant le tour en cours (copies des cartes, purement pour le visuel)
        self.rituals = [ "mirror", "transfusion", "transfusion", "distortion", "water" ]
        self.renfield = None
        self.info_message = None

        for i in range(16):
            self.library.append("bite")

        for i in range(15):
            self.library.append("spell")

        for i in range(18):
            self.library.append("journal")

    #Envoies l'embed dans le channel et à tous les joueurs
    async def broadcast(self, _embed, **kwargs):
        exceptions = kwargs["exceptions"] if "exceptions" in kwargs else []
        mode = kwargs["mode"] if "mode" in kwargs else "normal"

        if mode == "append":
            if self.info_message:
                embed = self.info_message.embeds[0]
                embed.description += _embed.description

                await self.info_message.edit(embed = embed)
            else:
                self.info_message = await self.channel.send(embed = _embed)

            for id, player in self.players.items():
                if id not in exceptions:
                    if player.info_message:
                        embed = player.info_message.embeds[0]
                        embed.description += _embed.description

                        await player.info_message.edit(embed = embed)
                    else:
                        player.info_message = await player.user.send(embed = _embed)
        elif mode == "replace":
            if self.info_message:
                await self.info_message.edit(embed = _embed)
            else:
                self.info_message = await self.channel.send(embed = _embed)

            for id, player in self.players.items():
                if id not in exceptions:
                    if player.info_message:
                        await player.info_message.edit(embed = _embed)
                    else:
                        player.info_message = await player.user.send(embed = _embed)
        elif mode == "set":
            self.info_message = await self.channel.send(embed = _embed)
            for id, player in self.players.items():
                if id not in exceptions:
                    player.info_message = await player.user.send(embed = _embed)
        else:
            await self.channel.send(embed = _embed)
            for id, player in self.players.items():
                if id not in exceptions:
                    await player.user.send(embed = _embed)

    #Broadcast les infos du jeu à tous les joueurs
    async def send_info(self, title):
        #Infos pour Renfield et le channel
        embed = discord.Embed(
            title = title,
            color = 0x000055,
            description = "Il reste " + str(len(self.rituals)) + " Rituels"
        )

        for i, id in enumerate(self.order):
            value = "__Main :__ "
            for _ in range(len(self.players[id].hand)):
                value += "🔳"

            if self.players[id].bites:
                value += "\n__Morsures :__ "
                for _ in range(self.players[id].bites):
                    value += "🧛"

            if i == 0:
                value += "\nCe joueur a le Pieu Ancestral ✝️"

            embed.add_field(name = globals.number_emojis[i] + " `" + str(self.players[id].user) + "`",
                value = value,
                inline = False
            )

        value = "\n".join(globals.ritual_names[x] for x in self.rituals)
        embed.add_field(name = "Rituels restants :",
            value = value,
            inline = False
        )

        if self.turn > 0:
            embed.add_field(name = "Cartes défaussées :",
                value = '\n'.join(["`" + str(self.players[self.order[i]].user) + "` : " + globals.card_names[card] for i,card in enumerate(self.discard_stack)]),
                inline = False
            )

        if self.info_message:
            await self.info_message.edit(embed = embed)
        else:
            self.info_message = await self.channel.send(embed = embed)

        for id, player in self.players.items():
            if player.role != "Renfield":
                await self.send_personnal_info(player, title)
            else:
                if player.info_message:
                    await player.info_message.edit(embed = embed)
                else:
                    #Infos supplémentaires pour Renfield
                    if self.turn > 0:
                        embed.add_field(name = "Cartes jouées :",
                            value = '\n'.join(["`" + str(self.players[self.order[i]].user) + "` : " + globals.card_names[card] for i,card in enumerate(self.stack)]),
                            inline = False
                        )

                    for i, field in enumerate(embed.fields):
                        if self.players[self.order[i]].role == "Vampire":
                            embed.set_field_at(i,
                                name = field.name + " (🧛)",
                                value = field.value,
                                inline = False
                            )
                            break

                    player.info_message = await player.user.send(embed = embed)

    async def send_personnal_info(self, player, title):
        #Infos pour les joueurs
        goal = 4 if len(self.players) <= 5 else 5
        total_bites = 0
        for id in self.order:
            total_bites += self.players[id].bites

        embed = discord.Embed(
            title = title,
            color = 0x000055,
            description = "Il reste " + str(len(self.rituals)) + " Rituels" + (". Il vous reste " + str(goal - total_bites) + " Morsures à placer" if player.role == "Vampire" else "")
        )

        for i, id in enumerate(self.order):
            if id == player.user.id:
                value = "__Votre main :__\n"
                value += '\n'.join([globals.card_names[x] for x in player.hand])
            else:
                value = "__Main :__ "
                for _ in range(len(self.players[id].hand)):
                    value += "🔳"

            if self.players[id].bites:
                value += "\n__Morsures :__ "
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

        value = "\n".join(globals.ritual_names[x] for x in self.rituals)
        embed.add_field(name = "Rituels restants :",
            value = value,
            inline = False
        )

        if self.turn > 0:
            embed.add_field(name = "Cartes défaussées :",
                value = '\n'.join(["`" + str(self.players[self.order[i]].user) + "` : " + globals.card_names[card] for i,card in enumerate(self.discard_stack)]),
                inline = False
            )

        if player.info_message:
            await player.info_message.edit(embed = embed)
        else:
            player.info_message = await player.user.send(embed = embed)

    async def start_game(self, message):
        for player in self.players.values():
            await player.user.send("||\n\n\n\n\n\n\n\n\n\n||")

        self.turn = 0
        self.order = [x for x in self.players]

        if len(self.players) == 4 :
            await message.channel.send("Il s'agit d'une partie à 4 joueurs, le bot est donc automatiquement Renfield.\n**Le Miroir d'Argent ne pourra pas être joué et ne servira que de dernier Rituel à effectuer.**")
            await self.game_start()
        else:
            await message.channel.send("Début de partie, " + message.author.mention + " va décider du Renfield")

            async def set_renfield(reactions):
                #Change Renfield
                index = reactions[message.author.id][0]
                if index == len(self.players):
                    await message.channel.send("Le bot est maitenant Renfield\n**Le Miroir d'Argent ne pourra pas être joué et ne servira que dedernier Rituel à effectuer.**")
                else:
                    await message.channel.send(str(self.players[self.order[index]].user) + " est maitenant Renfield")

                    self.players[self.order[index]] = Renfield(self.players[self.order[index]].user)
                    self.renfield = self.players[self.order[index]]

                await self.game_start()

            async def cond(reactions):
                return len(reactions[message.author.id]) == 1

            choices = ["`" + str(x.user) + "`" for x in self.players.values()]
            choices.append("`Le bot`")

            await ReactionMessage(cond,
                set_renfield
            ).send(message.author,
                "Choisis le Renfield",
                "",
                0xffff00,
                choices
            )

    async def game_start(self):
        #Détermine au hasard l'ordre et le premier joueur
        random.shuffle(self.order)

        #Ajouter les nuits à l'horloge et à la librairie et les mélange
        for i in range(10):
            if i < len(self.players):
                self.clock.append("night")
            else:
                self.library.append("night")

        random.shuffle(self.library)
        random.shuffle(self.clock)

        if self.renfield:
            self.order.remove(self.renfield.user.id)

            async def set_vampire(reactions):
                #Met à jour les rôles et les envoies
                index = reactions[self.renfield.user.id][0]
                user = self.players[self.order[index]].user
                self.players[self.order[index]] = Vampire(user)

                await self.renfield.user.send(str(user) + " est maitenant le Vampire")

                for id in self.order:
                    player = self.players[id]
                    await player.game_start(self)

                #Tour du premier joueur
                await self.players[self.order[0]].turn_start(self)


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
        else:
            index = random.randrange(len(self.order))
            user = self.players[self.order[index]].user
            self.players[self.order[index]] = Vampire(user)

            for id in self.order:
                player = self.players[id]
                await player.game_start(self)

            #Tour du premier joueur
            await self.players[self.order[0]].turn_start(self)

    #Le tour de table est terminé, les cartes sont étudiées en secret
    async def study_stack(self):
        #Les messages d'infos sont reset par le message de fin de nuit

        self.discard_stack.clear()

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
                ), mode = "set")

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
                        color = 0x00ff00,
                        description = "\n\nLe Miroir révèle que `" + str(choice.user) + "` est " + ("le Vampire!" if choice.role == "Vampire" else "un Chasseur")
                    ), mode = "append")

                    await self.check_if_stack_done()

                async def holy_water(reactions):
                    index = reactions[player.user.id][0] #Le choix revient au joueur avec le Pieu
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        color = 0x00ff00,
                        description = "\n\n`" + str(choice.user) + "` a été aspergé d'Eau Bénite, et a donc défaussé sa main. Il a pioché autant de cartes de la défausse"
                    ), mode = "append")

                    hand_size = len(choice.hand)
                    self.discard.extend(choice.hand)
                    choice.hand.clear()

                    card_index = 0
                    while card_index < len(self.discard) and hand_size > 0:
                        if self.discard[card_index] == "journal":
                            choice.hand.append(self.discard.pop(card_index))
                            hand_size -= 1
                        card_index += 1

                    card_index = 0
                    while card_index < len(self.library) and hand_size > 0:
                        if self.library[card_index] == "journal":
                            choice.hand.append(self.library.pop(card_index))
                            hand_size -= 1
                        card_index += 1


                    await self.check_if_stack_done()

                async def transfuse(reactions):
                    index = reactions[player.user.id][0] #Le choix revient au joueur avec le Pieu
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        color = 0x00ff00,
                        description = "\n\n`" + str(choice.user) + "` a été transfusé et a donc pioché une carte" + (". Il a toujours " + str(player.bites) + " Morsures" if player.bites else "")
                    ), mode = "append")

                    await choice.draw(self, 1)

                    await self.check_if_stack_done()

                async def run_ritual(reactions):
                    index = reactions[player.user.id][0]
                    if not self.renfield:
                        index += 1
                    ritual = self.rituals.pop(index)

                    if ritual == "distortion":
                        await self.broadcast(discord.Embed(
                            title = "Rituel effectué : 🕰️ Distortion temporelle",
                            color = 0x00ff00,
                            description = random.choice(globals.clock_faces) + " Une distortion temporelle s'empare du manoir! " + random.choice(globals.clock_faces) + "\nUne carte Nuit a été retirée de l'Horloge"
                        ), mode = "replace")

                        index_to_remove = -1
                        while self.clock[index_to_remove] == "dawn":
                            index_to_remove -= 1

                        self.clock.pop(index_to_remove)

                        print("moving on")
                        await self.check_if_stack_done()
                    elif ritual == "mirror":
                        await self.broadcast(discord.Embed(
                            title = "Rituel effectué : 🔮 Miroir d'Argent",
                            color = 0x00ff00,
                            description = "`" + str(player.user) + "` regarde dans le Miroir d'Argent pour y voir la véritable identité d'un des Chasseurs...\nRenfield va choisir un joueur dont le rôle sera révélé"
                        ), mode = "replace")

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
                            title = "Rituel effectué : 🧴 Eau Bénite",
                            color = 0x00ff00,
                            description = "`" + str(player.user) + "` se saisit de l'Eau Bénite et s'apprête à purifier un membre de l'équipe\nIl va choisir un joueur qui va défausser sa main et piochera autant de Journaux de la défausse"
                        ), mode = "replace")

                        await ReactionMessage(cond,
                            holy_water
                        ).send(player.user,
                            "Choisis le joueur qui va défausser sa main et piochera autant de Journaux de la défausse",
                            "",
                            0x00ff00,
                            ["`" + str(self.players[x].user) + "`" for x in self.order]
                        )
                    elif ritual == "transfusion":
                        await self.broadcast(discord.Embed(
                            title = "Rituel effectué : 💉 Transfusion Sanguine",
                            color = 0x00ff00,
                            description = "`" + str(player.user) + "` récupère la poche de sang et s'approche d'un de ses collègues pour le soigner\nIl va choisir un joueur qui va piocher une carte, mais garder les Morsures qui sont devant lui"
                        ), mode = "replace")

                        await ReactionMessage(cond,
                            transfuse
                        ).send(player.user,
                            "Choisis le joueur qui va piocher une carte",
                            "",
                            0x00ff00,
                            ["`" + str(self.players[x].user) + "`" for x in self.order]
                        )

                choices = [globals.ritual_names[x] for x in self.rituals]
                if not self.renfield:
                    choices.pop(0)

                await ReactionMessage(cond,
                    run_ritual
                ).send(player.user,
                    "Choisis le Rituel à effectuer",
                    "",
                    0x00ff00,
                    choices
                )
            else:
                await self.broadcast(discord.Embed(
                    title = "**Victoire des Chasseurs**",
                    color = 0x00ff00,
                    description = "Toutes les cartes passées à Renfield étaient des Incantations. Tous les Rituels ont été effectués, le Vampire, `" + str([x for x in self.players.values() if x.role == "Vampire"][0].user) + "`, a été anéanti par le groupe.\n**Les Chasseurs ont gagné!**"
                ))

                await self.end_game()
        else:
            #Prépare le compteur de nuit qui ont été ajoutées
            self.nights = 0

            #Mélange le stack pour brouiller les origines
            random.shuffle(self.stack)

            #Commence la boucle récursive d'étude des cartes
            await self.loop_through_stack()

    async def loop_through_stack(self):
        card = self.stack.pop()

        #Défausses la carte
        self.discard.append(card)

        #Si la carte est une MORSURE, envoies le choix du joueur puis le choix de la carte
        if card == "bite":
            goal = 4 if len(self.players) <= 5 else 5
            total_bites = 1
            for player in self.players.values():
                if player.role != "Renfield":
                    total_bites += player.bites

            if total_bites == goal:
                await self.broadcast(discord.Embed(
                    title = "**Victoire du Mal**",
                    description = "Le nombre requis de Morsures ont été jouées. Le Vampire, `" + str([x for x in self.players.values() if x.role == "Vampire"][0].user) + "`, ayant désormais suffisamment d'influence, a neutralisé l'équipe des Chasseurs.\n**Le Mal a gagné!**",
                    color = 0xff0000
                ))

                await self.end_game()
            else:
                target_player = self.renfield if self.renfield else self.players[self.order[0]]

                #Fonction de morsure pour le premier choix
                async def bite_player(reactions):
                    index = reactions[target_player.user.id][0]
                    player = self.players[self.order[index]]

                    #Ajoute une Morsure au mordu
                    player.bites += 1

                    #Préviens tout le monde
                    await self.broadcast(discord.Embed(
                        title = "**Morsure !**",
                        description = "`" + str(player.user) + "` a été mordu! Renfield va choisir une carte de sa main pour la défausser",
                        color = 0xff0000
                    ))

                    if self.renfield:
                        #Fonction de défausse pour le second choix
                        async def discard(reactions2):
                            card_index = reactions2[self.renfield.user.id][0]
                            card = player.hand.pop(card_index)

                            #Préviens le joueur
                            await self.renfield.user.send("`" + str(player.user) + "` a défaussé sa carte " + globals.card_names[card])
                            await player.user.send("Tu as été forcé de défausser ta carte " + globals.card_names[card])

                            #Défausses la carte
                            self.discard.append(card)

                            await self.check_if_stack_done()

                        #Envoies le choix de la carte à défausser uniquement s'il y a une carte à défausser
                        if len(player.hand):
                            await ReactionMessage(cond,
                                discard
                            ).send(self.renfield.user,
                                "Choisis la carte à défausser",
                                "",
                                0xff0000,
                                [globals.card_names[x] for x in player.hand]
                            )
                        else:
                            #Sinon juste avance le tour
                            await self.renfield.user.send("`" + str(player.user) + "` n'avait aucune carte à défausser")
                            await self.check_if_stack_done()
                    else:
                        #Envoies le choix de la carte à défausser uniquement s'il y a une carte à défausser
                        if len(player.hand):
                            card_index = random.randrange(len(player.hand))
                            card = player.hand.pop(card_index)

                            #Préviens le joueur
                            await player.user.send("Tu as été forcé de défausser ta carte " + globals.card_names[card])

                            #Défausses la carte
                            self.discard.append(card)
                        else:
                            #Sinon juste avance le tour
                            await self.players[self.order[0]].user.send("`" + str(player.user) + "` n'avait aucune carte à défausser")

                        await self.check_if_stack_done()

                async def cond(reactions):
                    return len(reactions[target_player.user.id]) == 1

                #Envoies le message de choix du mordu à Renfield
                await ReactionMessage(cond,
                    bite_player
                ).send(target_player.user,
                    "Choisis qui sera mordu",
                    "Une Morsure a été jouée\n\n",
                    0xff0000,
                    ["`" + str(self.players[x].user) + "`" + (" (🧛)" if self.players[x].role == "Vampire" and target_player is self.renfield else "") for x in self.order]
                )
        else:
            #Rajoute la Nuit à l'Horloge et ajoute un au nombre qui ont été ajoutées
            if card == "night":
                self.clock.append(card)
                await self.broadcast(discord.Embed(
                    description = "\n**Une carte Nuit a été jouée et ajoutée à l'Horloge**",
                    color = 0x000055
                ), mode = "append")

            #Regarde la prochaine carte
            await self.check_if_stack_done()

    async def check_if_stack_done(self):
        if len(self.stack):
            await self.loop_through_stack()
        else:
            if self.clock[self.turn - 1] == "dawn":
                player = self.players[self.order[0]]

                await self.broadcast(discord.Embed(
                    title = "Choix du Pieu Ancestral",
                    description = "Le tour de table s'est fini sur une Aurore. Le Porteur du Pieu Ancestral (`" + str(player.user) + "`) a donc la possibilité de l'utiliser sur un de ses collègues",
                    color = 0x00ff00
                ), mode = "set")

                async def pass_stick(reactions):
                    index = reactions[player.user.id][0] + (1 if not globals.debug else 0)
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        description = "\n\n`" + str(player.user) + "` a passé le Pieu Ancestral à `" + str(choice.user) + "`",
                        color = 0x00ff00
                    ), mode = "append")

                    for i in range(index):
                        self.order.append(self.order.pop(0))

                    await self.next_table_turn(True)

                async def cond(reactions):
                    return len(reactions[player.user.id]) == 1

                async def send_murder_choice(reactions):
                    if reactions[player.user.id][0] == 0:
                        async def stab_player(reactions):
                            index = reactions[player.user.id][0]
                            choice = (self.players[self.order[index]] if index < len(self.order) else None) if player.role == "Hunter" else None

                            if choice:
                                await self.broadcast(discord.Embed(
                                    title = "Le Pieu Ancestral a été planté !",
                                    description = "`" + str(player.user) + "` a décidé de planter le Pieu dans le coeur de `" + str(choice.user) + "`!\n" + ("Le Pieu s'enflamme et tue le Vampire sur-le-champ, ne laissant qu'un tas de cendre. **Les Chasseurs ont gagnés!**" if choice.role == "Vampire" else "Le Pieu reste silencieux alors que le Chasseur s'effondre sur le sol. Le Vampire, `" + str([x for x in self.players.values() if x.role == "Vampire"][0].user) + "`, maintenant que les autres Chasseurs sont sans défense, se révèle et termine le travail\n**Le Mal a gagné!**"),
                                    color = 0x00ff00 if choice.role == "Vampire" else 0xff0000
                                ), mode = "replace")

                                await self.end_game()
                            else:
                                await self.broadcast(discord.Embed(
                                    title = "Choix du Pieu Ancestral",
                                    description = "`" + str(player.user) + "` a décidé de garder le Pieu pour plus tard. Il va cependant décider du joueur qui va recevoir le Pieu pour le prochain Tour",
                                    color = 0x00ff00
                                ), mode = "replace")

                                await ReactionMessage(cond,
                                    pass_stick
                                ).send(player.user,
                                    "Choisis à qui tu veux passer le Pieu",
                                    "",
                                    0x00ff00,
                                    ["`" + str(self.players[x].user) + "`" for x in self.order if x != player.user.id or globals.debug]
                                )

                        choices = ["`" + str(self.players[x].user) + "`" for x in self.order] if player.role == "Hunter" else []
                        choices.append("Personne")

                        await ReactionMessage(cond,
                            stab_player
                        ).send(player.user,
                            "Choisis qui tu veux planter avec le Pieu Ancestral",
                            "",
                            0xff0000,
                            choices
                        )
                    else:
                        await self.broadcast(discord.Embed(
                            title = "Choix du Pieu Ancestral",
                            description = "`" + str(player.user) + "` a décidé de garder le Pieu pour plus tard. Il va cependant décider du joueur qui va recevoir le Pieu pour le prochain Tour",
                            color = 0x00ff00
                        ), mode = "replace")

                        await ReactionMessage(cond,
                            pass_stick
                        ).send(player.user,
                            "Choisis à qui tu veux passer le Pieu",
                            "",
                            0x00ff00,
                            ["`" + str(self.players[x].user) + "`" for x in self.order if x != player.user.id or globals.debug]
                        )

                await ReactionMessage(cond,
                    send_murder_choice
                ).send(player.user,
                    "Voulez vous tuer quelqu'un avec le Pieu Ancestral?",
                    "",
                    0x00ff00,
                    ["Oui", "Non"]
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
        ), mode = "set")

        if not stick_was_passed:
            if self.renfield:
                async def pass_stick(reactions):
                    index = reactions[self.renfield.user.id][0] + (1 if not globals.debug else 0)
                    choice = self.players[self.order[index]]

                    await self.broadcast(discord.Embed(
                        description = "\n\n`" + str(self.renfield.user) + "` a passé le Pieu Ancestral à `" + str(choice.user) + "`",
                        color = 0x000055
                    ), mode = "append")

                    #Met le joueur sélectionné en première position en faisant tourner l'ordre
                    for i in range(index):
                        self.order.append(self.order.pop(0))

                    #Reset les messages d'infos
                    self.info_message = None
                    for player in self.players.values():
                        player.info_message = None

                    await self.players[self.order[0]].turn_start(self)

                async def cond(reactions):
                    return len(reactions[self.renfield.user.id]) == 1

                await ReactionMessage(cond,
                    pass_stick
                ).send(self.renfield.user,
                    "Choisis à qui tu veux passer le Pieu",
                    "",
                    0x000055,
                    ["`" + str(self.players[x].user)  + "`" for x in self.order if x != self.order[0] or globals.debug]
                )
            else:
                index = random.randrange(1, len(self.order))
                choice = self.players[self.order[index]]

                await self.broadcast(discord.Embed(
                    description = "\n\nRenfield a passé le Pieu Ancestral à `" + str(choice.user) + "`",
                    color = 0x000055
                ), mode = "append")

                for i in range(index):
                    self.order.append(self.order.pop(0))

                #Reset les messages d'infos
                self.info_message = None
                for player in self.players.values():
                    player.info_message = None

                await self.players[self.order[0]].turn_start(self)
        else:
            #Reset les messages d'infos
            self.info_message = None
            for player in self.players.values():
                player.info_message = None

            await self.players[self.order[0]].turn_start(self)

    async def end_game(self):
        embed = discord.Embed(
            title = "Fin de partie",
            description = "",
            color = 0xfffffe
        )

        i = 0
        for id in self.order:
            value = "__Main __:\n"
            value += '\n  '.join([globals.card_names[x] for x in self.players[id].hand])

            if self.players[id].bites:
                value += "\n__Morsures :__"
                for _ in range(self.players[id].bites):
                    value += "🧛"

            embed.add_field(name = "`" + str(self.players[id].user) + "`" + (" (🧛)" if self.players[id].role == "Vampire" else ""),
                value = value
            )
            i += 1

        if len(self.rituals):
            value = "\n".join(globals.ritual_names[x] for x in self.rituals)
            embed.add_field(name = "Rituels restants :",
                value = value,
                inline = False
            )
        else:
            embed.add_field(name = "Rituels restants :",
                value = "Aucun!",
                inline = False
            )

        await self.broadcast(embed)

        globals.games.pop(self.channel.id)
