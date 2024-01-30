"""Panel classes (mesages with views)"""

import discord
import datetime
import modules.botc.phases as phases

from modules.botc.views import PanelView, JoinView, NominationView, VoteView, ControlView, VoteControlView
from modules.botc.types import Phases, VoteState, Vote


class Panel:
    view_class = PanelView
    keep_message = True

    def __init__(self, game):
        self.game = game
        self.channel = None
        self.message = None
        self.closed = False
        
        self._view = None

    @property
    def content(self):
        return None
    
    @property
    def embed(self):
        return discord.Embed()

    @property
    def view(self):
        if not self._view: 
            if not self.closed: self._view = self.view_class(self.game, self)
        else:
            self._view.update()
        
        return self._view

    async def send(self, channel):
        self.channel = channel
        self.message = await channel.send(content=self.content, view=self.view, embed=self.embed)
        return self
    
    async def update(self, interaction=None, save=True):
        if interaction:
            await interaction.response.defer()
        
        await self.message.edit(content=self.content, view=self.view, embed=self.embed)
        if save: self.game.save()
    
    async def close(self, force_keep_message=None):
        if self.closed: return

        self.closed = True
        if (force_keep_message if force_keep_message != None else self.keep_message):
            await self._view.clear()
        else:
            await self._view.delete()

    def serialize(self):
        return {
            "channel": self.channel.id if self.channel else None,
            "message": self.message.id if self.message else None,
            "closed": self.closed
        }
    
    async def parse(self, object, client):
        self.channel = await client.fetch_channel(object["channel"]) if object["channel"] else None
        self.message = await self.channel.fetch_message(object["message"]) if object["message"] else None
        self.closed = object["closed"]

        if self.message:
            self.view.message = self.message
            await self.update(save=False)
        
        return self


class JoinPanel(Panel):
    view_class = JoinView
    keep_message = False
    
    @property
    def embed(self):
        embed = discord.Embed(color=self.game.mainclass.color)
        embed.title = f"Partie de BotC | Conteur: {self.game.storyteller.display_name} | Joueurs ({len(self.game.players)}/{self.game.phases[Phases.start].max_players}) :"
        embed.description = '\n'.join([x.user.mention for x in self.game.players.values()])
        return embed

    async def update_max_players(self, amount, interaction):
        self.game.phases[Phases.start].max_players = amount
        await self.update(interaction)
    

class TimedPanel(Panel):
    duration = datetime.timedelta(hours=24)

    def __init__(self, game):
        super().__init__(game)
        self.end_time = discord.utils.utcnow() + self.duration

    def serialize(self):
        object = super().serialize()
        object["end_time"] = self.end_time
        return object
    
    async def parse(self, object, client):
        self.end_time = object["end_time"]
        return await super().parse(object, client)


class NominationPanel(TimedPanel):
    view_class = NominationView
    keep_message = False

    @property
    def content(self):
        return self.game.role.mention
    
    @property
    def embed(self):
        embed = discord.Embed(
            color=self.game.mainclass.color,
            title="🔔 Les nominations sont ouvertes!",
            description=f"""
                Utilisez le menu de sélection pour nominer un autre joueur. Vous ne pouvez **nominer et être nominé qu'une fois par jour**, et seulement si vous êtes vivant (sauf pour exiler un Voyageur). 
                **Fin des nominations:** {discord.utils.format_dt(self.end_time, style='R')}
            """
        )
        return embed
    
    async def update(self, interaction=None, save=True):
        for panel in self.game.phases[Phases.nominations].vote_panels.values():
            await panel.update(save=False)
        await super().update(interaction, save=save)


class VotePanel(TimedPanel):
    view_class = VoteView

    def __init__(self, game, nominator=None, nominee=None):
        super().__init__(game)
        self.nominator = nominator
        self.nominee = nominee

        self.accusation = "En attente..."
        self.defense = "En attente..."
        self.order = []
        self.active_order = []
        self.votes = {}
        self.control_panel = None

    @property
    def content(self):
        return f"{self.game.role.mention} {self.nominator.user.mention}{self.nominee.user.mention}"
    
    @property
    def vote_total(self):
        return sum(x.value for i,x in self.votes.items() if i not in self.active_order)
    
    @property
    def required_votes(self):
        return self.game.required_votes_for_exile if self.nominee.traveller else self.game.required_votes
    
    @property
    def embed(self):
        verb = "a appelé à l'exil de" if self.nominee.traveller else "a nominé"

        embed = discord.Embed(
            color=self.game.mainclass.color,
            title=f"⚖️ {self.nominator} {verb} {self.nominee}",
            description=f"""
                Utilisez les boutons pour ajouter une accusation, une défense, et pour voter.
                **Total des votes:** {'?' if self.game.gamerules['hidden_vote'].state else self.vote_total}/{self.required_votes}
                **Fin du vote:** {discord.utils.format_dt(self.end_time, style='R')}
            """
        )

        embed.add_field(
            name="👉 Accusation",
            value=self.accusation
        )

        embed.add_field(
            name="✋ Défense",
            value=self.defense
        )

        for id in self.order:
            value = self.votes[id].display
            if self.game.gamerules["hidden_vote"].state: value = "🙈"

            icon = ""
            player = self.game.players[id]
            if self.nominator == player: icon += "👉"
            if self.nominee == player: icon += "✋"
            if not self.game.gamerules["hidden_vote"].state:
                if self.votes[id].with_thief: icon += self.game.mainclass.emojis["thief"]
                if self.votes[id].with_bureaucrat: icon += self.game.mainclass.emojis["bureaucrat"]

            embed.add_field(
                name=f"{'➡️ ' if not self.game.gamerules['hidden_vote'].state and len(self.active_order) and self.active_order[0] == id else ''}{player} {icon}",
                value=value,
                inline=False
            )
    
        return embed

    async def send(self, channel):
        if not self.nominee.traveller: self.nominator.has_nominated = True
        self.nominee.was_nominated = True

        self.order = self.game.order_from(self.nominee.user.id)
        self.active_order = [*self.order]
        self.votes = {
            i: Vote(VoteState.no_vote, "❔") if self.can_player_vote(x) else Vote(VoteState.vote_against, self.game.mainclass.emojis["against"]) 
            for i,x in self.game.players.items()
        }
        
        self.control_panel = await VoteControlPanel(self.game, self).send(self.game.control_thread)
        return await super().send(channel)
    
    async def update(self, interaction=None, save=True):
        await self.control_panel.update(save=False)
        await super().update(interaction, save=save)

    def can_player_vote(self, player):
        return player.can_vote or self.nominee.traveller
    
    async def update_accusation(self, accusation, interaction):
        self.accusation = accusation
        await self.update(interaction)

    async def update_defense(self, defense, interaction):
        self.defense = defense
        await self.update(interaction)
    
    async def update_vote(self, id, display, state, interaction):
        player = self.game.players[id]
        if not self.can_player_vote(player) and self.game.gamerules["dead_vote_required"].state:
            return await interaction.response.send_message("Vous n'avez plus de jeton de vote.", ephemeral=True)
        
        if id not in self.active_order:
            return await interaction.response.send_message("Vous avez déjà voté.", ephemeral=True)

        self.votes[id].display = display
        self.votes[id].state = state
        if id == self.active_order[0] and state in (VoteState.vote_for, VoteState.vote_against): 
            return await self.next_player(interaction)
        
        await self.update(interaction)

    async def next_player(self, interaction):
        id = self.active_order.pop(0)
        vote = self.votes[id]
        if vote.state == VoteState.vote_for:
            if not self.nominee.traveller:
                vote.with_thief = self.game.players[id].thief_affected
                vote.with_bureaucrat = self.game.players[id].bureaucrat_affected
            vote.display += f" ({self.vote_total}/{self.required_votes})"

        if len(self.active_order) == 0:
            return await self.end(interaction)

        next_vote = self.votes[self.active_order[0]]
        if next_vote.state in (VoteState.vote_for, VoteState.vote_against): return await self.next_player(interaction)
        await self.update(interaction)

    async def end(self, interaction=None, no_delete=False):
        await self.control_panel.close()
        if no_delete:
            await self.close()
        else:
            await self.game.phases[Phases.nominations].close_vote(self.message.id)
        await self.update(interaction)

    def serialize(self):
        object = super().serialize()
        object["nominator"] = self.nominator.user.id
        object["nominee"] = self.nominee.user.id
        object["accusation"] = self.accusation
        object["defense"] = self.defense
        object["order"] = self.order
        object["active_order"] = self.active_order
        object["votes"] = {i: x.to_dict() for i,x in self.votes.items()}
        object["control_panel"] = self.control_panel.serialize() if self.control_panel else None
        return object
    
    async def parse(self, object, client):
        self.nominator = self.game.players[object["nominator"]]
        self.nominee = self.game.players[object["nominee"]]
        self.accusation = object["accusation"]
        self.defense = object["defense"]
        self.order = [int(x) for x in object["order"]]
        self.active_order = [int(x) for x in object["active_order"]]
        self.votes = {int(i): Vote.from_dict(x) for i,x in object["votes"].items()}
        self.control_panel = await VoteControlPanel(self.game, self).parse(object["control_panel"], client) if object["control_panel"] else None
        return await super().parse(object, client)


class ControlPanel(Panel):
    view_class = ControlView
    
    @property
    def embed(self):
        embed = discord.Embed(
            color=self.game.mainclass.color,
            title="⚙️ Panneau de contrôle"
        )

        player_info = []
        for id in self.game.order:
            player = self.game.players[id]
            info = f"- {player} "
            if player.thief_affected: info += self.game.mainclass.emojis["thief"] 
            if player.bureaucrat_affected: info += self.game.mainclass.emojis["bureaucrat"] 
            player_info.append(info)
        embed.add_field(name="Joueurs", value='\n'.join(player_info))
        
        return embed
    
    async def update(self, interaction=None, save=True, global_update=True):
        if global_update:
            for phase in self.game.phases.values():
                if isinstance(phase, phases.PanelPhase):
                    await phase.update(save=False)

        return await super().update(interaction, save=save)


class VoteControlPanel(Panel):
    view_class = VoteControlView

    def __init__(self, game, vote_panel):
        super().__init__(game)
        self.vote_panel = vote_panel

    @property
    def content(self):
        return f"**{self.vote_panel.nominator}** 👉 **{self.vote_panel.nominee}**"
    
    @property
    def clockhand_player_id(self):
        return self.vote_panel.active_order[0] if len(self.vote_panel.active_order) else None

    @property
    def embed(self):
        embed = discord.Embed(
            color=self.game.mainclass.color,
            title=f"⚙️⚖️ Contrôle du vote"
        )
        embed.add_field(name="Accusation", value=self.vote_panel.accusation)
        embed.add_field(name="Défense", value=self.vote_panel.defense)

        player_info = [
            ('➡️ ' if len(self.vote_panel.active_order) and self.clockhand_player_id == id else '')
            + f"__{self.game.players[id]}:__ {self.vote_panel.votes[id].display} "
            + (self.game.mainclass.emojis["thief"] if self.vote_panel.votes[id].with_thief or self.game.players[id].thief_affected else "")
            + (self.game.mainclass.emojis["bureaucrat"] if self.vote_panel.votes[id].with_bureaucrat  or self.game.players[id].bureaucrat_affected else "")
            for id in self.vote_panel.order
        ]
        embed.add_field(name="Votes", value='\n'.join(player_info), inline=False)
        embed.add_field(name="Total", value=f"{self.vote_panel.vote_total}/{self.vote_panel.required_votes}")

        if len(self.vote_panel.active_order):
            id = self.clockhand_player_id
            embed.add_field(name="Vote à déterminer", value=f"{self.game.players[id]}: {self.vote_panel.votes[id].display}", inline=False)

        return embed
    
    async def update_next_vote(self, display, value, interaction):
        if not self.clockhand_player_id:
            return await interaction.response.defer()
        
        await self.vote_panel.update_vote(self.clockhand_player_id, display, value, interaction)

    async def count_as_for(self, interaction):
        await self.update_next_vote(self.game.mainclass.emojis["for"], VoteState.vote_for, interaction)
    
    async def count_as_against(self, interaction):
        await self.update_next_vote(self.game.mainclass.emojis["against"], VoteState.vote_against, interaction)

    async def ping_missing(self, interaction):
        content = (', '.join(self.game.players[i].user.mention for i,x in self.vote_panel.votes.items() if x.state == VoteState.no_vote)
                + f", vous n'avez pas encore voté pour la nomination de {self.vote_panel.nominee}")
        await self.vote_panel.channel.send(content)
        await interaction.response.defer()
