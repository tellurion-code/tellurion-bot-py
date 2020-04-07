import sys
import random
import discord
import asyncio

from modules.nosferatu.reaction_message import ReactionMessage
from modules.nosferatu.roles import Renfield, Vampire, Hunter
from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "Nosferatu"
    help_active = True
    help = {
        "description": "Module du jeu Nosferatu",
        "commands": {
            "`{prefix}{command}`": "Démarre une partie de Nosferatu",
            "`{prefix}{command} join`": "Rejoint la partie de Nosferatu",
            "`{prefix}{command} quit`": "Quitte la partie de Nosferatu",
            "`{prefix}{command} start`": "Démarre la partie de Nosferatu (réservé à Renfield)",
            "`{prefix}{command} nominate`": "Nomine un nouveau Renfield pour la partie de Nosferatu (réservé à Renfield)",
            "`{prefix}{command} players`": "Affiche les joueurs de la partie de Nosferatu",
        }
    }
    color = 0xff0000
    command_text = "nosferatu"

    games = {}
    number_emojis = [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ,"🔟" ]
    reaction_messages = []

    def __init__(self, client):
        super().__init__(client)

    #Lancer la partie
    async def command(self, message, args, kwargs):
        if not message.channel.id in self.games:
            embed = discord.Embed(title = "Démarrage de la partie de Nosferatu",
                                description = "Tapez !nosferatu join pour rejoindre la partie",
                                color = self.color)

            await message.channel.send(embed = embed)

            self.games[message.channel.id] = {
                "players": {
                    message.author.id: Renfield()
                }, #Dict pour rapidement accéder aux infos
                "order": [], #L'ordre de jeu (liste des id des joueurs, n'inclut pas Renfield)
                "turn": -1, #Le tour en cours (incrémente modulo le nombre de joueurs). -1 = pas commencé
                "clock": [ "dawn" ], #Nuits et Aurore
                "library": [], #Morsures, Incantations, Nuits et Journaux
                "stack": [], #Ce qui est passé à Renfield
                "rituals": [ "mirror", "transfusion", "transfusion", "distortion", "water" ]
            }

            for i in range(16):
                self.games[message.channel.id]["library"].append("bite")

            for i in range(15):
                self.games[message.channel.id]["library"].append("spell")

            for i in range(18):
                self.games[message.channel.id]["library"].append("journal")
        else:
            await message.channel.send("Il y a déjà une partie en cours")

    #Rejoindre la partie
    async def com_join(self, message, args, kwargs):
        if message.channel.id in self.games:
            if message.author.id in self.games[message.channel.id]["players"]:
                await message.channel.send("Tu es déjà dans la partie")
            elif len(self.games[message.channel.id]["players"]) < 8:
                await message.channel.send("<@" + str(message.author.id) + "> rejoint la partie")

                self.games[message.channel.id]["players"][message.author.id] = Hunter()
            else:
                await message.channel.send("Il y a déjà le nombre maximum de joueurs (8)")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Liste des joueurs
    async def com_players(self, message, args, kwargs):
        if message.channel.id in self.games:
            embed = discord.Embed(
                title = "Liste des joueurs",
                color = self.color,
                description = "```" + ', '.join([self.client.get_user(x).name + (" (Renfield)" if (y.role == "Renfield") else "") for x, y in self.games[message.channel.id]["players"].items()]) + "```"
            )
            await message.channel.send(embed = embed)
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Changer de Renfield
    async def com_nominate(self, message, args, kwargs):
        if message.channel.id in self.games:
            if message.author.id in self.games[message.channel.id]["players"]:
                if self.games[message.channel.id]["players"][message.author.id].role == "Renfield":
                    await message.channel.send(self.client.get_user(message.author.id).name + " va nominer un nouveau Renfield")
                    players = [x for x in self.games[message.channel.id]["players"]]

                    async def set_renfield(obj, reactions):
                        #Change Renfield
                        index = self.number_emojis.index(reactions[message.author.id][0])
                        await message.channel.send(self.client.get_user(players[index]).name + " est maitenant Renfield")

                        self.games[message.channel.id]["players"][message.author.id] = Hunter()
                        self.games[message.channel.id]["players"][players[index]] = Renfield()

                        self.reaction_messages.remove(obj)
                        print(self.reaction_messages)

                    async def cond(reactions):
                        return len(reactions[message.author.id]) == 1

                    await self.send_choice(message.channel,
                        "Choisis le joueur que tu veux mettre Renfield",
                        "",
                        self.color,
                        [self.client.get_user(x).name for x in self.games[message.channel.id]["players"]],
                        lambda r, u: u.id == message.author.id,
                        cond,
                        set_renfield)
                else:
                    await message.channel.send("Tu n'es pas Renfield")
            else:
                await message.channel.send("Tu n'es pas dans la partie")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    #Début de partie + logique des parties (boucle)
    async def com_start(self, message, args, kwargs):
        if message.channel.id in self.games:
            game = self.games[message.channel.id]
            if game["players"][message.author.id].role == "Renfield":
                if len(game["players"]) >= 5:
                    await message.channel.send("Début de partie")

                    #Ajouter les nuits à l'horloge et à la librairie et les mélange
                    for i in range(10):
                        if i < len(game["players"]):
                            game["clock"].append("night")
                        else:
                            game["library"].append("night")

                    random.shuffle(game["library"])
                    random.shuffle(game["clock"])

                    async def set_player(reactions):
                        #Met à jour les rôles et les envoies
                        index = self.number_emojis.index(reactions[message.author.id][0].emoji)
                        game["players"][index] = Vampire()

                        await message.author.send(self.client.get_user(players[index]).name + " est maitenant le Vampire")
                        await self.client.get_user(players[index]).send(embed = discord.Embed(
                            title = "Début de partie",
                            color = 0xff0000,
                            description = "Tu es le Vampire. Ton but est de faire tuer un Chasseur par le Pieu Ancestral, ou bien de réussir à placer " + ("4" if (len(game["players"]) == 5) else "5") + " Morsures."
                        ))

                        for player in game["players"].values():
                            if player.role == "Hunter":
                                await self.client.get_user(players[index]).send(embed = discord.Embed(
                                    title = "Début de partie",
                                    color = 0x00ff00,
                                    description = "Tu es un Chasseur. Ton but est de tuer le Vampire avec le Pieu Ancestral, ou bien de réussir à jouer les 5 Rituels."
                                ))

                        #Détermine au hasard l'ordre et le premier joueur et commence la boucle de la partie
                        game["order"] = [x for x in game["players"]]
                        game["order"].remove(message.author.id)
                        random.shuffle(game["order"])
                        game["turn"] = 0

                        #Envoies les infos

                        #Envoi le jeu

                    #Envoies le message de choix du vampire à Renfield
                    await self.send_choice(message.author,
                        "Choix du Vampire",
                        "",
                        0xff0000,
                        [self.client.get_user(players[x]).name for x in game["players"]],
                        lambda reactions: len(reactions) == 1,
                        set_player)

                else:
                    await message.channel.send("Il faut au minimum 5 joueurs pour commencer la partie")
            else:
                await message.channel.send("Tu n'es pas Renfield")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def on_reaction_add(self, reaction, user):
        print("Detected add reaction")
        if not user.bot:
            for message in self.reaction_messages:
                if message.check(reaction, user) and reaction.emoji in message.number_emojis and message.message.id == reaction.message.id:
                    await message.add_reaction(reaction, user)

    async def on_reaction_remove(self, reaction, user):
        print("Detected remove reaction")
        if not user.bot:
            for message in self.reaction_messages:
                if message.check(reaction, user) and reaction.emoji in message.number_emojis and message.message.id == reaction.message.id:
                    await message.remove_reaction(reaction, user)

    #Envoies un choix avec validation
    async def send_choice(self, _channel, _title, _description, _color, _choices, _check, _cond, _effect):
        embed = discord.Embed(
            title = _title,
            description = _description,
            color = _color
        )

        i = 0
        for choice in _choices:
            embed.description += self.number_emojis[i] + "`" + choice + "`\n"
            i += 1

        reaction_message = ReactionMessage(_check, _cond, _effect)
        print(reaction_message.number_emojis)
        self.reaction_messages.append(reaction_message)

        reaction_message.message = await _channel.send(embed = embed)
        reaction_message.number_emojis = reaction_message.number_emojis[:len(_choices)]
        reaction_message.number_emojis.append("✅")
        print(reaction_message.number_emojis)

        for i in range(10):
            if i < len(_choices):
                await reaction_message.message.add_reaction(self.number_emojis[i])
