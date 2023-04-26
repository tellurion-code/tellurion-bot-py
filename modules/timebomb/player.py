"""Player class."""

# from modules.timebomb.utils import ...

import modules.timebomb.globals as global_values
import modules.timebomb.views as views


class Player:
    def __init__(self, game, user):
        self.game = game
        self.user = user
        self.role = None
        self.index_emoji = ""
        self.wires = []

        self.target = None

    @property
    def must_exchange(self):
        return (self.revealed is not None) or (self.game.round < 5 and not global_values.debug)

    def __str__(self):
        return f"{self.index_emoji} `{self.user}`"

    async def send_role_info(self, interaction):
        await interaction.response.send_message(
            content=f"Votre rôle est {self.role}",
            ephemeral=True
        )

    async def cut_wire(self, selection, interaction):
        await interaction.response.defer()
        self.target = selection[0]
        await self.game.send_info(
            info={
                "name": "✂️ Coupe",
                "value": f"{self} va choisir quel fil couper chez {self.target}"
            },
            view=views.WireCuttingView(
                self.target,
                self.end_turn
            )
        )

    async def end_turn(self, index, interaction):
        await interaction.response.defer()

        game_over = await self.target.wires[index].cut(self)
        if not game_over:
            wire = self.target.wires.pop(index)
            self.game.aside.append(wire)

            self.game.turn = self.target.user.id
            await self.game.next_turn({
                "name": f"✂️ Coupe",
                "value": self.game.stack_string
            })
