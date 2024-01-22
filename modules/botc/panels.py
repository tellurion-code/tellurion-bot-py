"""Panel classes (mesages with views)"""

import discord
import datetime

from modules.botc.views import PanelView, JoinView, NominationView, VoteView, ControlView, VoteControlView
from modules.botc.constants import VOTE_AGAINST, VOTE_FOR

class Panel:
    view_class = PanelView
    keep_message = True

    def __init__(self, game):
        self.game = game
        self.message = None
        self.channel = None
        self.view = None

        self.closed = False

    def get_content(self):
        return None
    
    def get_embed(self):
        return discord.Embed()

    def get_view(self):
        if not self.view: 
            self.view = self.view_class(self.game, self)
        else:
            self.view.update()
        
        return self.view

    async def send(self, channel):
        self.channel = channel
        self.message = await channel.send(content=self.get_content(), view=self.get_view(), embed=self.get_embed())
        return self
    
    async def update(self, interaction=None):
        if interaction:
            await interaction.response.edit_message(content=self.get_content(), view=self.get_view(), embed=self.get_embed())
        else:
            await self.message.edit(content=self.get_content(), view=self.get_view(), embed=self.get_embed())
    
    async def close(self, force_keep_message=None):
        if self.closed: return

        self.closed = True
        if (force_keep_message if force_keep_message != None else self.keep_message):
            await self.view.clear()
        else:
            await self.view.delete()


class JoinPanel(Panel):
    view_class = JoinView
    keep_message = False
    
    def get_embed(self):
        embed = discord.Embed(color=self.game.mainclass.color)
        embed.title = f"Partie de BOTC | Conteur: {self.game.storyteller.display_name} | Joueurs ({str(len(self.game.players))}) :"
        embed.description = '\n'.join([x.user.mention for x in self.game.players.values()])
        return embed


class NominationPanel(Panel):
    duration = datetime.timedelta(hours=24)
    view_class = NominationView
    keep_message = False

    def __init__(self, game):
        super().__init__(game)
        self.end_time = discord.utils.utcnow() + self.duration
    
    def get_embed(self):
        embed = discord.Embed(
            color=self.game.mainclass.color,
            title="🔔 Les nominations sont ouvertes!",
            description=f"""
                Utilisez le menu de sélection pour nominer un autre joueur. Vous ne pouvez **nominer et être nominé qu'une fois par jour**, et seulement si vous êtes vivant (sauf pour exiler un Voyageur). 
                **Fin des nominations:** {discord.utils.format_dt(self.end_time, style='R')}
            """
        )
        return embed


class VotePanel(Panel):
    duration = datetime.timedelta(hours=24)
    view_class = VoteView

    def __init__(self, game, nominator, nominee):
        super().__init__(game)
        self.nominator = nominator
        self.nominee = nominee

        self.accusation = "En atente..."
        self.defense = "En atente..."
        self.votes = {id: "❔" for id in self.game.players}

        self.end_time = discord.utils.utcnow() + self.duration

        nominator.has_nominated = True
        nominee.was_nominated = True

    def get_content(self):
        return f"{self.nominator.user.mention}{self.nominee.user.mention}"
    
    def get_embed(self):
        verb = "a appelé à l'exil de" if self.nominee.traveller else "a nominé"
        vote_total = (f"{'?' if self.game.gamerules['hidden_vote'].state else sum(1 for x in self.votes.values() if x == VOTE_FOR)}"
                      f"/{self.game.required_votes_for_exile if self.nominee.traveller else self.game.required_votes}")

        embed = discord.Embed(
            color=self.game.mainclass.color,
            title=f"⚖️ {self.nominator} {verb} {self.nominee}",
            description=f"""
                Utilisez les boutons pour ajouter une accusation, une défense, et pour voter.
                **Total des votes:** {vote_total}
                **Fin du vote:** {discord.utils.format_dt(self.end_time, style='R')}
            """
        )

        embed.add_field(
            name=f"👉 Accusation",
            value=self.accusation
        )

        embed.add_field(
            name=f"✋ Défense",
            value=self.defense
        )

        for id, vote in self.votes.items():
            value = vote
            if self.game.gamerules["hidden_vote"].state: value = "🙈"

            embed.add_field(
                name=f"{self.game.players[id]}",
                value=value,
                inline=False
            )
    
        return embed

    async def send(self, channel):
        self.control_panel = await VoteControlPanel(self.game, self).send(self.game.control_thread)
        return await super().send(channel)
    
    async def update(self, interaction=None):
        await self.control_panel.update()
        return await super().update(interaction)
    
    async def update_accusation(self, accusation, interaction):
        self.accusation = accusation
        await self.update(interaction)

    async def update_defense(self, defense, interaction):
        self.defense = defense
        await self.update(interaction)
    
    async def update_vote(self, id, vote, interaction):
        player = self.game.players[id]
        if not player.alive and not player.dead_vote and not self.nominee.traveller and self.game.gamerules["dead_vote_required"].state:
            await interaction.response.send_message("Vous n'avez plus de jeton de vote.", ephemeral=True)
            return

        self.votes[id] = vote
        await self.update(interaction)


class ControlPanel(Panel):
    view_class = ControlView
    
    def get_embed(self):
        embed = discord.Embed(
            color=self.game.mainclass.color,
            title="⚙️ Panneau de contrôle"
        )
        embed.add_field(name="Joueurs", value='\n'.join(f'- {player}' for player in self.game.players.values()))
        return embed
    
    async def update(self, interaction=None, global_update=True):
        if global_update and self.game.current_panel: await self.game.current_panel.update()
        return await super().update(interaction)


class VoteControlPanel(Panel):
    view_class = VoteControlView

    def __init__(self, game, vote_panel):
        super().__init__(game)
        self.vote_panel = vote_panel
        self.player_ids = None

    def get_content(self):
        return f"{self.game.storyteller.mention} **{self.vote_panel.nominator}** 👉 **{self.vote_panel.nominee}**"

    def get_embed(self):
        embed = discord.Embed(
            color=self.game.mainclass.color,
            title=f"⚙️⚖️ Contrôle du vote"
        )
        embed.add_field(name="Accusation", value=self.vote_panel.accusation)
        embed.add_field(name="Défense", value=self.vote_panel.defense)
        embed.add_field(name="Votes", value='\n'.join(f"__{self.game.players[id]}:__ {vote}" for id, vote in self.vote_panel.votes.items()), inline=False)
        embed.add_field(name="Total", value=f"{sum(1 for x in self.vote_panel.votes.values() if x == VOTE_FOR)}/{self.game.required_votes_for_exile if self.vote_panel.nominee.traveller else self.game.required_votes}")

        if self.player_ids:
            id = self.player_ids[-1]
            embed.add_field(name="Vote à déterminer", value=f"{self.game.players[id]}: {self.vote_panel.votes[id]}", inline=False)

        return embed
    
    async def start_count(self, interaction):
        await self.vote_panel.close()
        self.player_ids = list(self.game.players.keys())
        await self.next_player(interaction)

    async def count_as_for(self, interaction):
        id = self.player_ids.pop()
        self.vote_panel.votes[id] = VOTE_FOR
        await self.next_player(interaction)

    async def count_as_against(self, interaction):
        id = self.player_ids.pop()
        self.vote_panel.votes[id] = VOTE_AGAINST
        await self.next_player(interaction)

    async def next_player(self, interaction):
        if len(self.player_ids) == 0: 
            await self.vote_panel.update()
            await self.update(interaction)
            await self.close(force_keep_message=self.game.gamerules["hidden_vote"].state)
            return

        next_vote = self.vote_panel.votes[self.player_ids[-1]]
        if next_vote == VOTE_FOR: return await self.count_as_for(interaction)
        if next_vote == VOTE_AGAINST: return await self.count_as_against(interaction)
        await self.update(interaction)
