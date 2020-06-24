import discord
import random
import math

from modules.secrethitler.player import Liberal, Fascist, Hitler
from modules.secrethitler.reaction_message import ReactionMessage
from modules.secrethitler.law_names import get_law_name

import modules.secrethitler.globals as globals

class Game:
    def __init__(self, mainclass, **kwargs):
        reload = kwargs["reload"] if "reload" in kwargs else False
        message = kwargs["message"] if "message" in kwargs else None
        object = kwargs["object"] if "object" in kwargs else None
        client = kwargs["client"] if "client" in kwargs else None
        self.mainclass = mainclass

        if reload:
            self.deserialize(object, client)

            if object["state"]["type"] == "send_chancellor_choice":
                self.send_chancellor_choice(object["state"]["message"])
            elif object["state"]["type"] == "send_laws":
                self.send_laws()
        else:
            self.channel = message.channel
            self.players = {
                message.author.id: Liberal(message.author)
            } #Dict pour rapidement accéder aux infos
            self.order = [] #Ordre des id des joueurs
            self.turn = -1 #Le tour (index du président) en cours, -1 = pas commencé
            self.chancellor = 0 #Id du chancelier
            self.after_special_election = -1 #Id du prochain président en cas d'Election Spéciale, -1 = pas de président nominé
            self.deck = [] #Liste des lois
            self.discard = [] #Pile de défausse
            self.policies = [] #Pouvoirs des lois fascistes
            self.liberal_laws = 0 #Nombre de lois libérales votées
            self.fascist_laws = 0 #Nombre de lois fascistes votées
            self.term_limited = [] #Listes des id des anciens chanceliers et présidents
            self.refused = 0 #Nombre de gouvernements refusés
            self.info_message = None
            self.played = "" #Dernière carte jouée

            for _ in range(6):
                self.deck.append("liberal")

            for _ in range(11):
                self.deck.append("fascist")

            random.shuffle(self.deck)

    async def start_game(self):
        self.turn = 0
        fascist_amount = max(0, math.floor((len(self.players) - 3)/2))

        policies = [
            ["none", "none", "none", "none", "none", "none"], #0
            ["none", "none", "none", "none", "none", "none"], #1
            ["none", "none", "none", "peek", "elect", "inspect"], #2, Debug
            ["none", "none", "peek", "kill", "kill", "none"], #3
            ["none", "none", "peek", "kill", "kill", "none"], #4
            ["none", "none", "peek", "kill", "kill", "none"], #5
            ["none", "none", "peek", "kill", "kill", "none"], #6
            ["none", "inspect", "elect", "kill", "kill", "none"], #7
            ["none", "inspect", "elect", "kill", "kill", "none"], #8
            ["inspect", "inspect", "elect", "kill", "kill", "none"], #9
            ["inspect", "inspect", "elect", "kill", "kill", "none"], #10
        ]

        if len(self.policies) == 0:
            self.policies = policies[len(self.players)]

        for id in self.players:
            self.order.append(id)

        random.shuffle(self.order)
        self.players[self.order[fascist_amount]] = Hitler(self.players[self.order[fascist_amount]].user)

        for i in range(len(self.order)):
            if i < fascist_amount:
                self.players[self.order[i]] = Fascist(self.players[self.order[i]].user)

        random.shuffle(self.order)

        for i in range(len(self.order)):
            await self.players[self.order[i]].game_start(self)

        await self.send_chancellor_choice("Début de partie\n")

    #Envoies un message à tous les joueurs + le channel
    async def broadcast(self, _embed, **kwargs):
        exceptions = kwargs["exceptions"] if "exceptions" in kwargs else []
        mode = kwargs["mode"] if "mode" in kwargs else "normal"

        if mode == "append": #append = ajoute à la description
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
        elif mode == "replace": #replace = modifie le dernier message
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
        elif mode == "set": #set = nouveau message
            self.info_message = await self.channel.send(embed = _embed)
            for id, player in self.players.items():
                if id not in exceptions:
                    player.info_message = await player.user.send(embed = _embed)
        else: #normal = nouveau message sans mémoire
            await self.channel.send(embed = _embed)
            for id, player in self.players.items():
                if id not in exceptions:
                    await player.user.send(embed = _embed)

    #Envoies le résumé de la partie aux joueurs + le channel
    async def send_info(self, **kwargs):
        mode = kwargs["mode"] if "mode" in kwargs else "replace"
        info = kwargs["info"] if "info" in kwargs else ""
        color = kwargs["color"] if "color" in kwargs else globals.color

        embed = discord.Embed(title = "[SECRET HITLER] Tour de `" + str(self.players[self.order[self.turn]].user) + "` 🎖️",
            description = info,
            color = color
        )

        if self.fascist_laws >= 3:
            embed.description += "⚠️ Victoire des Fascistes par nomination d'Hitler débloquée ⚠️\n"

        if self.fascist_laws >= 5:
            embed.description += "🚫 Droit de véto débloqué 🚫\n"

        embed.description += "__Parlementaires:__\n" + '\n'.join([self.players[x].last_vote[:1] + globals.number_emojis[i] + " `" + str(self.players[x].user) + "` " + ("🎖️" if self.turn == i else ("💼" if self.chancellor == x else ("❌" if x in self.term_limited else ""))) for i, x in enumerate(self.order)])

        embed.add_field(name = "Lois libérales :",
            value = "🟦" * self.liberal_laws + "🔹" * ( 5 - self.liberal_laws )  + "\n" + "⬛" * 5)

        policies_icons = {
            "none": "⬛",
            "peek": "👁️",
            "inspect": "🔍",
            "elect":"🎖️",
            "kill": "🗡️"
        }

        embed.add_field(name = "Lois fascistes :",
            value = "🟥" * self.fascist_laws + "🔻" * max( 0, 3 - self.fascist_laws ) + "🔺" * min( 3, 6 - self.fascist_laws ) + "\n" + ''.join([policies_icons[x] for x in self.policies]))

        embed.add_field(name = "Gouvernements refusés :",
            value = "🟧" * self.refused + "🔸" * ( 2 - self.refused ),
            inline = False)

        # --[ANCIEN BROADCAST]--
        # await self.channel.send(embed = embed)
        # for player in self.players.values():
        #     await player.user.send(embed = embed)

        await self.broadcast(embed, mode = mode)

    #Est aussi un début de tour, envoies le choix de chancelier
    async def send_chancellor_choice(self, info):
        self.save({"type": "send_chancellor_choice", "message": info})

        for player in self.players.values():
            player.last_vote = ""

        self.chancellor = -1

        await self.send_info(mode = "set", info = info)

        president = self.players[self.order[self.turn]] #Tour actuel

        valid_candidates = [x for i, x in enumerate(self.order) if i != self.turn and (x not in self.term_limited or globals.debug)]
        emojis = [globals.number_emojis[self.order.index(x)] for x in valid_candidates]

        choices = ["`" + str(self.players[x].user) + "`" for x in valid_candidates]

        async def propose_chancellor(reactions):
            self.chancellor = valid_candidates[reactions[president.user.id][0]]

            await self.send_info(info = globals.number_emojis[self.order.index(self.chancellor)] + " `" + str(self.players[self.chancellor].user) + "` a été choisi comme Chancelier\n")

            for id in self.order:
                await self.players[id].send_vote(self)

        async def cond(reactions):
            return len(reactions[self.order[self.turn]]) == 1

        await ReactionMessage(cond,
            propose_chancellor
        ).send(president.user,
            "Choisissez votre Chancelier",
            "",
            globals.color,
            choices,
            emojis = emojis
        )

    #Appelé à chaque fois qu'un joueur vote. Vérifie les votes manquants puis la majorité
    #TODO: Trouvez pourquoi il est call 2 fois d'affilée parfois
    async def check_vote_end(self):
        missing = False

        for id in self.order:
            player = self.players[id]

            embed = player.vote_message.message.embeds[0]
            embed.set_field_at(0, name = "Votes:",
                value = ' '.join(["✉️" if self.players[x].last_vote == "" else "📩" for x in self.order])
            )

            if player.last_vote != "":
                embed.description = "Le Président `" + str(self.players[self.order[self.turn]].user) + "` a proposé comme Chancelier `" + str(self.players[self.chancellor].user) + "`.\nVous avez voté " + player.last_vote
                embed.color = 0x00ff00 if player.last_vote[1:] == "Ja" else 0xff0000
            else:
                missing = True

            await player.vote_message.message.edit(embed = embed)

        if not missing:
            for_votes = len([self.players[x] for x in self.order if self.players[x].last_vote[1:] == "Ja"])

            await self.send_info(color = 0x00ff00 if for_votes > len(self.order)/2 else 0xff0000) #Change la couleur du message en fonction

            if for_votes > len(self.order)/2:
                if self.players[self.chancellor].role == "hitler" and self.fascist_laws >= 3:
                    await self.end_game(False, "nomination d'Hitler en tant que Chancelier")
                else:
                    await self.send_laws()
            else:
                self.refused += 1

                if self.refused == 3:
                    cards = await self.draw(1)
                    done = await self.apply_law(cards[0], "🟦 Libérale : " + get_law_name("{type} de {noun_liberal} {adjective}") if cards[0] == "liberal" else "🟥 Fasciste : " + get_law_name("{type} de {noun_fascist} {adjective}"), "*Gouvernement inactif*:", "Les parlementaires n'ont pas réussi à se mettre d'accord sur un Gouvernement.", False)

                    if not done:
                        self.discard.extend(cards)
                        self.refused = 0

                        await self.next_turn()
                elif self.refused >= 1:
                    await self.next_turn("**Le Gouvernement proposé a été refusé**\n")

    async def send_laws(self):
        self.save({"type": "send_laws"})

        await self.broadcast(discord.Embed(title = "Gouvernement accepté",
            description = "Le Gouvernement proposé a été accepté. Le Président et le Chancelier vont maintenant choisir la loi à faire passer parmi les 3 piochées",
            color = 0x00ff00
        ), mode = "set")

        cards = await self.draw(3)
        show_cards = ["🟦 Libérale : " + get_law_name("{type} de {noun_liberal} {adjective}") if x == "liberal" else "🟥 Fasciste : " + get_law_name("{type} de {noun_fascist} {adjective}") for x in cards]

        async def cond_president(reactions):
            return len(reactions[self.order[self.turn]]) == 1

        async def discard_first(reactions):
            discarded = cards.pop(reactions[self.order[self.turn]][0])
            show_discarded = show_cards.pop(reactions[self.order[self.turn]][0])

            await law_message.message.edit(embed = discord.Embed(title = "Loi défaussée",
                description = "Lois restantes :\n" + '\n'.join(show_cards) + "\n\nLoi défaussée :\n" + show_discarded,
                color = 0x00ff00
            ))

            self.discard.append(discarded)

            async def cond_chancellor(reactions):
                return len(reactions[self.chancellor]) == 1

            async def play_law(reactions):
                self.played = cards.pop(reactions[self.chancellor][0])
                show_played = show_cards.pop(reactions[self.chancellor][0])
                self.discard.extend(cards)

                if self.fascist_laws >= 5:
                    await self.players[self.order[self.turn]].send_veto_vote(self)
                    await self.players[self.chancellor].send_veto_vote(self)
                else:
                    await self.apply_law(self.played, show_played)

            await ReactionMessage(cond_chancellor,
                play_law,
                temporary = False
            ).send(self.players[self.chancellor].user,
                "Choisissez la carte à **jouer**",
                "",
                globals.color,
                show_cards
            )

        law_message = ReactionMessage(cond_president,
            discard_first,
            temporary = False
        )

        await law_message.send(self.players[self.order[self.turn]].user,
            "Choisissez la carte à **défausser**",
            "Les deux autres seront passées à votre Chancelier\n\n",
            globals.color,
            show_cards
        )

    #Vérfies la fin du vote de veto, similaire à check_vote_end
    async def check_veto_vote(self):
        if self.players[self.order[self.turn]].last_vote != "" and self.players[self.chancellor].last_vote != "":
            if self.players[self.order[self.turn]] == "Nein" or self.players[self.chancellor].last_vote == "Nein":
                await self.apply_law(self.played)
            else:
                self.discard.append(self.played)

                self.refused += 1

                if self.refused == 3:
                    cards = await self.draw(1)
                    done = await self.apply_law(cards[0], "🟦 Libérale : " + get_law_name("{type} de {noun_liberal} {adjective}") if cards[0] == "liberal" else "🟥 Fasciste : " + get_law_name("{type} de {noun_fascist} {adjective}"), "*Gouvernement inactif*:", "Les parlementaires n'ont pas réussi à se mettre d'accord sur un Gouvernement.", False)

                    if not done:
                        self.discard.extend(cards)
                        self.refused = 0

                        await self.next_turn("**Le Gouvernement a utilisé son droit de véto**\n")
                elif self.refused >= 1:
                    await self.next_turn("**Le Gouvernement a utilisé son droit de véto**\n")

    #Fin de tour, s'occupe des effets des pouvoirs fascistes
    async def apply_law(self, law, name, message = "Gouvernement accepté :", description = "Le Gouvernement proposé a été accepté.", normal = True):
        self.refused = 0
        self.term_limited.clear()

        if normal:
            if len(self.players) > 5:
                self.term_limited.append(self.order[self.turn])

            self.term_limited.append(self.chancellor)

        async def cond_president(reactions):
            return len(reactions[self.order[self.turn]]) == 1

        if law == "liberal":
            await self.broadcast(discord.Embed(title = message + " Loi libérale adoptée 🕊️",
                description = description + " Le Président et le Chancelier ont adopté une loi " + name,
                color = 0x2e64fe
            ), mode = "replace")

            done = await self.pass_law("liberal")

            if not done and normal:
                await self.next_turn()
        else:
            policy = self.policies[self.fascist_laws]

            policies_announcements = {
                "none": "\n**Aucune action spéciale ne prend place**",
                "peek": "\n👁️ **Le Président va regarder les 3 prochaines lois**",
                "inspect": "\n🔍 **Le Président va inspecter l'allégeance d'un des parlementaires**",
                "kill": "\n🗡️ **Le Président va choisir un parlementaire à exécuter**",
                "elect": "\n🎖️ **Le Président va nominer un parlementaire comme prochain Président de manière exceptionnelle**"
            }

            await self.broadcast(discord.Embed(title = message + " Loi fasciste adoptée 🐍",
                description = description + " Le Président et le Chancelier ont adopté une loi " + name + "." + (policies_announcements[policy] if normal else ""),
                color = 0xef223f
            ), mode = "replace")

            done = await self.pass_law("fascist")

            if not done and normal:
                if policy == "peek":
                    if len(self.deck) < 3:
                        self.deck.extend(self.discard)
                        self.discard.clear()
                        random.shuffle(self.deck)

                        await self.broadcast(discord.Embed(description = "La pioche a été reformée à partir des cartes restantes et de la défausse", color = 0xfffffe))

                    await self.players[self.order[self.turn]].user.send(embed = discord.Embed(title = "👁️ Prévision",
                        description = "Voici les 3 prochaines lois :\n" + '\n'.join(["🟦 Libérale" if self.deck[x] == "liberal" else "🟥 Fasciste" for x in range(3)]),
                        color = globals.color
                    ))

                    await self.next_turn()
                elif policy == "inspect":
                    inspectable = [x for i, x in enumerate(self.order) if i != self.turn and not self.players[x].inspected]
                    emojis = [globals.number_emojis[self.order.index(x)] for x in inspectable]

                    async def inspect(reactions):
                        player = self.players[inspectable[reactions[self.order[self.turn]][0]]]

                        player.inspected = True

                        await self.broadcast(discord.Embed(
                            description = ".\n\nL'allégeance de `" + str(player.user) + "` a été inspectée"
                        ), mode = "append")

                        await self.players[self.order[self.turn]].user.send(embed = discord.Embed(title = "🔍 Inspection",
                            description = "L'allégeance de `" + str(player.user) + "` est " + ("🟦 Libérale" if player.role == "liberal" else "🟥 Fasciste"),
                            color = globals.color
                        ))

                        await self.next_turn()

                    await ReactionMessage(cond_president,
                        inspect
                    ).send(self.players[self.order[self.turn]].user,
                        "Choisissez le joueur à inspecter",
                        "",
                        globals.color,
                        ["`" + str(self.players[x].user) + "`" for x in inspectable],
                        emojis = emojis
                    )
                elif policy == "kill":
                    killable = [x for i, x in enumerate(self.order) if i != self.turn]
                    emojis = [globals.number_emojis[self.order.index(x)] for x in killable]

                    async def kill(reactions):
                        id = killable[reactions[self.order[self.turn]][0]]
                        player = self.players[id]

                        await self.broadcast(discord.Embed(
                            description = ".\n\n`" + str(player.user) + "` a été exécuté et retiré du jeu"
                        ), mode = "append")

                        if self.after_special_election == id:
                            self.after_special_election = self.order[self.order.index(id) + 1]

                        self.order.remove(id)

                        if player.role == "hitler":
                            await self.end_game(True, "exécution d'Hitler")
                        elif len(self.order) == 1:
                            await self.end_game(self.players[self.order[0]].role == "liberal", "solitude")
                        else:
                            await self.next_turn()

                    await ReactionMessage(cond_president,
                        kill
                    ).send(self.players[self.order[self.turn]].user,
                        "Choisissez le joueur à exécuter",
                        "",
                        globals.color,
                        ["`" + str(self.players[x].user) + "`" for x in killable],
                        emojis = emojis
                    )
                elif policy == "elect":
                    electable = [x for i, x in enumerate(self.order) if i != self.turn]
                    emojis = [globals.number_emojis[self.order.index(x)] for x in electable]

                    async def elect(reactions):
                        id = electable[reactions[self.order[self.turn]][0]]
                        index = self.order.index(id)
                        player = self.players[id]

                        await self.broadcast(discord.Embed(
                            description = ".\n\n`" + str(player.user) + "` a été nommé Président pour cette Election Spéciale"
                        ), mode = "append")

                        await self.next_turn("**Une Election Spéciale a été convoquée**\n", index)

                    await ReactionMessage(cond_president,
                        elect
                    ).send(self.players[self.order[self.turn]].user,
                        "Choisissez le joueur à nominer pour l'Election Spéciale",
                        "",
                        globals.color,
                        ["`" + str(self.players[x].user) + "`" for x in electable],
                        emojis = emojis
                    )
                else:
                    await self.next_turn()

    #Applique la loi choisie ou piochée et vérifie la fin de la partie
    async def pass_law(self, law):
        if law == "liberal":
            self.liberal_laws += 1
        else:
            self.fascist_laws += 1

        if self.liberal_laws == 5:
            await self.end_game(True, "5 lois libérales votées")
            return True
        elif self.fascist_laws == 6:
            await self.end_game(False, "6 lois fascistes votées")
            return True
        else:
            return False

    #Passe au prochain tour, s'occupe aussi de l'élection spéciale
    async def next_turn(self, message = "", nomination = None):
        if nomination is not None:
            print("Nominated")
            self.after_special_election = self.order[(self.turn + 1) % len(self.order)]
            self.turn = nomination
        elif self.after_special_election != -1:
            print("Restored")
            self.turn = self.order.index(self.after_special_election)
            self.after_special_election = -1
        else:
            print("Normal")
            self.turn = (self.turn + 1) % len(self.order)

        await self.send_chancellor_choice(message)

    #Fin de partie, envoies le message de fin et détruit la partie
    async def end_game(self, liberal_wins, cause):
        if liberal_wins:
            embed = discord.Embed(title = "Victoire des Libéraux 🕊️ par " + cause  + " !", color = 0x2e64fe)
        else:
            embed = discord.Embed(title = "Victoire des Fascistes 🐍 par " + cause  + " !", color = 0xef223f)

        roles = {
            "liberal": "🟦 Libéral",
            "fascist": "🟥 Fasciste",
            "hitler": "☠️ Hitler"
        }

        embed.description = "__Joueurs :__\n" + '\n'.join([globals.number_emojis[i] + " `" + str(self.players[x].user) + "` : " + roles[self.players[x].role] for i,x in enumerate(self.order)]) + '\n' + '\n'.join(["💀 `" + str(x.user) + "` : " + roles[x.role] for i,x in self.players.items() if i not in self.order])

        await self.broadcast(embed)
        self.delete_save()
        globals.games.pop(self.channel.id)

    #Pioche x cartes (remélange le paquet si besoin)
    async def draw(self, amount):
        cards = []
        if len(self.deck) < amount:
            self.deck.extend(self.discard)
            self.discard.clear()
            random.shuffle(self.deck)

            await self.broadcast(discord.Embed(description = "La pioche a été reformée à partir des cartes restantes et de la défausse", color = 0xfffffe))

        for _ in range(amount):
            cards.append(self.deck.pop(0))

        return cards

    def serialize(self, state):
        object = {
            "channel": self.channel.id,
            "order": self.order,
            "turn": self.turn,
            "chancellor": self.chancellor,
            "after_special_election": self.after_special_election,
            "deck": self.deck,
            "discard": self.discard,
            "policies": self.policies,
            "liberal_laws": self.liberal_laws,
            "fascist_laws": self.fascist_laws,
            "term_limited": self.term_limited,
            "refused": self.refused,
            "info_message": self.info_message.id if self.info_message else None,
            "played": self.played,
            "players": {},
            "state": state
        }

        for id, player in self.players.items():
            object["players"][id] = {
                "role": player.role,
                "last_vote": player.last_vote,
                "inspected": player.inspected,
                "vote_message": player.vote_message.id if self.vote_message else None,
                "info_message": player.info_message.id if self.info_message else None,
                "user": player.user.id
            }

        return object

    def deserialize(self, object, client):
        self.channel = client.get_channel(object["channel"]),
        self.order = object["order"],
        self.turn = object["turn"],
        self.chancellor = object["chancellor"],
        self.after_special_election = object["after_special_election"],
        self.deck = object["deck"],
        self.discard = object["discard"],
        self.policies = object["policies"],
        self.liberal_laws = object["liberal_laws"],
        self.fascist_laws = object["fascist_laws"],
        self.term_limited = object["term_limited"],
        self.refused = object["refused"],
        self.info_message = self.channel.fetch_message(object["info_message"]) if object["info_message"] else None,
        self.played = object["played"]
        self.players = {}

        for id, info in game["players"].items():
            player = self.players[id] = Liberal(client.get_user(info.user)) if info.role == "liberal" else (Fascist(client.get_user(info.user)) if info.role == "fascist" else Hitler(client.get_user(info.user)))
            player.last_vote = info.last_vote
            player.inspected = info.inspected
            player.vote_message = player.user.dm_channel.fetch_message(info.vote_message) if info["vote_message"] else None
            player.info_message = player.user.dm_channel.fetch_message(info.info_message) if info["info_message"] else None

    def save(self, state):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.save_object("games")
        else:
            object = {}

        object[game.channel.id] = self.serialize(state)
        self.mainclass.objects.save_object("games", object)

    def delete_save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.save_object("games")
            if game.channel.id in object:
                object.pop(game.channel.id)

            self.mainclass.objects.save_object("games", object)
