"""Component classes."""

import discord


class PlayerSelect(discord.ui.Select):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.update()

    def update(self, keep_values_as_defaults=True):
        self.options.clear()
        
        for id in self.game.order:
            player = self.game.players[id]
            self.options.append(discord.SelectOption(
                label=str(player),
                value=str(id),
                # emoji=player.emoji
            ))

        if keep_values_as_defaults:
            for option in self.options:
                option.default = option.value in self.values
        else:
            self.values.clear()
