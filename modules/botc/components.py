"""Component classes."""

import discord


class PlayerSelect(discord.ui.Select):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.update()

    def update(self):
        self.options = []
        for id in self.game.order:
            player = self.game.players[id]
            self.options.append(discord.SelectOption(
                label=str(player),
                value=str(id),
                # emoji=player.emoji
            ))
