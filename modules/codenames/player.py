import discord

import modules.codenames.globals as globals
from modules.codenames.reaction_message import ReactionMessage

class Player():
    team = "none"

    def __init__(self, user):
        self.user = user
        self.message = None

    async def send_tile_choice(self, game):
        choices = ["A", "B", "C", "D", "E", "1", "2", "3", "4", "5", "Pass"]

        async def send_tile_info(reactions):
            if reactions[self.user.id][0] == 10:
                game.turn = "blue" if game.turn == "red" else "red"
                game.hint = ""
                await game.send_info()
            else:
                card = reactions[self.user.id][0] + 5 * (reactions[self.user.id][1] - 5)

                game.revealed[card] = game.colors[card]
                if game.colors[card] == game.turn:
                    await self.check_if_win(game)
                elif game.colors[card] == "black":
                    await game.end_game(False)
                else:
                    game.turn = "blue" if game.turn == "red" else "red"
                    game.hint = ""
                    await game.send_info()


        async def cond(reactions):
            if self.user.id in reactions:
                if reactions[self.user.id][0] == 10:
                    return True

                if len(reactions[self.user.id]) >= 2:
                    if reactions[self.user.id][0] in range(5) and reactions[self.user.id][1] in range(5, 10):
                        card = reactions[self.user.id][0] + 5 * (reactions[self.user.id][1] - 5)
                        return game.revealed[card] == "white"
                    else:
                        return False
                else:
                    return False
            else:
                return False

        async def update_tile(reactions):

            embed = message.message.embeds[0]
            embed.description = "Carte choisie : "

            if self.user.id in reactions:
                if reactions[self.user.id][0] != 10:
                    embed.description += choices[reactions[self.user.id][0]]

                    if len(reactions[self.user.id]) >= 2:
                        embed.description += choices[reactions[self.user.id][1]]
                        if reactions[self.user.id][0] in range(5) and reactions[self.user.id][1] in range(5, 10):
                            index = reactions[self.user.id][0] + 5 * (reactions[self.user.id][1] - 5)
                            embed.description += " (" + globals.color_emojis[game.colors[index]] + " " + game.board[index] + ")"
                        else:
                            embed.description += " (🚫 Coordonnées invalides)"
                    else:
                        embed.description += "?"
                else:
                    embed.description += "Aucune"
            else:
                embed.description += "??"

            await message.message.edit(embed = embed)

        message = ReactionMessage(cond,
            send_tile_info,
            update = update_tile
        )

        await message.send(self.user,
            "Choisis la carte à révéler",
            "Carte choisie : ??",
            0x880088,
            choices,
            emojis = ["🇦", "🇧", "🇨", "🇩", "🇪", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "🚫"],
            silent = True
        )
