import discord


class RoleButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = "Voir son rôle"
        self.style = discord.ButtonStyle.blurple

    async def callback(self, interaction):
        await self.view.game.players[interaction.user.id].send_role_info(interaction)


class TeamSelect(discord.ui.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = "Choississez votre équipe"

    async def callback(self, interaction):
        await self.view.update_selection(self, interaction)


class ConfirmButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = "Nombre de membres invalide"
        self.style = discord.ButtonStyle.gray
        self.disabled = True

    async def callback(self, interaction):
        await self.view.confirm_team(self, interaction)


class VoteButton(discord.ui.Button):
    def __init__(self, vote, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vote = vote

    async def callback(self, interaction):
        await self.view.cast_vote(self, interaction, self.vote)


class QuestButton(discord.ui.Button):
    def __init__(self, choice, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice = choice

    async def callback(self, interaction):
        await self.view.cast_choice(self, interaction, self.choice)


class TeamSelect(discord.ui.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = "Choississez votre équipe"

    async def callback(self, interaction):
        await self.view.update_selection(self, interaction)


class AssassinSelect(discord.ui.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = "Choississez qui assassiner"

    async def callback(self, interaction):
        await self.view.update_selection(self, interaction)

class KillButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = "Pas de cible choisie"
        self.style = discord.ButtonStyle.gray
        self.disabled = True

    async def callback(self, interaction):
        await self.view.kill(self, interaction)
