import sys
import random
import discord
import asyncio

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

    def __init__(self, client):
        super().__init__(client)

    async def command(self, message, args, kwargs):
        if not message.channel.id in self.games:
            embed = discord.Embed(title = "Démarrage de la partie de Nosferatu",
                                description = "Tapez !nosferatu join pour rejoindre la partie",
                                color = self.color)

            await message.channel.send(embed = embed)

            self.games[message.channel.id] = {
                "players": {
                    message.author.id: {
                        "role": "Renfield"
                    }
                },
                "turn": -1
            }
        else:
            await message.channel.send("Il y a déjà une partie en cours")
    #     self._can_delete.add(message.id)

    async def com_start(self, message, args, kwargs):
        if message.channel.id in self.games:
            if len(self.games[message.channel.id]["players"]) >= 5:
                await message.channel.send("Début de partie")
            else:
                await message.channel.send("Il faut au minimum 5 joueurs pour commencer la partie")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_join(self, message, args, kwargs):
        if message.channel.id in self.games:
            if message.author.id in self.games[message.channel.id]["players"]:
                await message.channel.send("Tu es déjà dans la partie")
            elif len(self.games[message.channel.id]["players"]) < 8:
                await message.channel.send("<@" + str(message.author.id) + "> rejoint la partie")

                self.games[message.channel.id]["players"][message.author.id] = {
                    "role": ""
                }
            else:
                await message.channel.send("Il y a déjà le nombre maximum de joueurs (8)")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_players(self, message, args, kwargs):
        if message.channel.id in self.games:
            embed = discord.Embed(
                title = "Liste des joueurs",
                color = self.color,
                description = "```" + ', '.join([self.client.get_user(x).name + (" (Renfield)" if (y["role"] == "Renfield") else "") for x, y in self.games[message.channel.id]["players"].items()]) + "```"
            )
            await message.channel.send(embed = embed)
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_nominate(self, message, args, kwargs):
        if message.channel.id in self.games:
            if self.games[message.channel.id]["players"][message.author.id]["role"] == "Renfield":
                await message.channel.send(self.client.get_user(message.author.id).name + " va nominer un nouveau Renfield")

                embed = discord.Embed(
                    title = "Choisis le joueur que tu veux mettre Renfield",
                    color = self.color,
                    description = ""
                )

                i = 0
                players = []
                for id in self.games[message.channel.id]["players"]:
                    embed.description += self.number_emojis[i] + "`" + self.client.get_user(id).name + "`\n"
                    players.append(id)
                    i += 1

                res = await message.author.send(embed = embed)

                for i in range(len(self.games[message.channel.id]["players"])):
                    await res.add_reaction(self.number_emojis[i])

                reaction, user = await self.client.wait_for("reaction_add", check = lambda r, u: r.count == 2)

                index = self.number_emojis.index(reaction.emoji)
                await message.channel.send(self.client.get_user(players[index]).name + " est maitenant Renfield")

                self.games[message.channel.id]["players"][message.author.id]["role"] = ""
                self.games[message.channel.id]["players"][players[index]]["role"] = "Renfield"
            else:
                await message.channel.send("Tu n'es pas Renfield")
        else:
            await message.channel.send("Il n'y a pas de partie en cours")
