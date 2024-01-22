"""Component classes"""

import discord

class PlayerSelect(discord.ui.Select):
    def __init__(self, game, *args, **kwargs):
        self.game = game

        options = []
        for id, player in self.game.players.items():
            options.append(discord.SelectOption(
                label=str(player),
                value=str(id),
                # emoji=player.emoji
            ))

        super().__init__(*args, options=options, **kwargs)
