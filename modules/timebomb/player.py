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
        self.wire_index = None

    def __str__(self):
        return f"{self.index_emoji} `{self.user}`"

    async def send_role_info(self, interaction):
        await interaction.response.send_message(
            content=f"Votre rôle est {self.role}",
            ephemeral=True
        )

    async def choose_wire_to_cut(self, selection, interaction):
        await interaction.response.defer()
        self.target = selection[0]
        await self.game.send_info(
            info={
                "name": "✂️ Coupe",
                "value": f"{self} va choisir quel fil couper chez {self.target}"
            },
            view=views.WireCuttingView(
                self.target,
                self.cut_wire
            )
        )

    async def cut_wire(self, index, interaction):
        self.wire_index = index
        await self.target.wires[index].cut(self, interaction)

    async def end_turn(self, interaction):
        await interaction.response.defer()

        wire = self.target.wires.pop(self.wire_index)
        self.game.aside.append(wire)

        await self.game.next_turn(self.target.user.id, {
            "name": f"✂️ Coupe",
            "value": self.game.stack_string
        })
