import discord


def get_quantity_qualifier(min_value, max_value, name):
    if min_value == 1:
        if max_value == 1: return f"un {name}"
        return f"un ou plusieurs {name}s"
    return f"plusieurs {name}s"


class GeneralSelect(discord.ui.Select):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = f"Choisissez {get_quantity_qualifier(self.min_values, self.max_values, name)}"

    async def callback(self, interaction):
        await self.view.update_selection(self, interaction)


class ConfirmButton(discord.ui.Button):
    def __init__(self, enabled, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(enabled, label)

    def update(self, enabled, label):
        self.label = label
        self.style = discord.ButtonStyle.green if enabled else discord.ButtonStyle.gray
        self.disabled = not enabled

    async def callback(self, interaction):
        await self.view.confirm(self, interaction)


class RolesButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = "Voir les rôles"
        self.style = discord.ButtonStyle.gray

    async def callback(self, interaction):
        await interaction.response.send_message(
            content=', '.join(str(x) for x in self.view.game.roles.values()),
            ephemeral=True
        )
