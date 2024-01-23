"""Panel classes (mesages with views)"""

import discord
import datetime
import modules.botc.phases as phases

from modules.botc.views import PanelView, JoinView, NominationView, VoteView, ControlView, VoteControlView

class Panel:
    view_class = PanelView
    keep_message = True

    def __init__(self, game):
        self.game = game
        self.channel = None
        self.message = None
        self.view = None
        self.closed = False

    def get_content(self):
        return None
    
    def get_embed(self):
        return discord.Embed()

    def get_view(self):
        if not self.view: 
            if not self.closed: self.view = self.view_class(self.game, self)
        else:
            self.view.update()
        
        return self.view

    async def send(self, channel):
        self.channel = channel
        self.message = await channel.send(content=self.get_content(), view=self.get_view(), embed=self.get_embed())
        return self
    
    async def update(self, interaction=None, save=True):
        if interaction:
            await interaction.response.edit_message(content=self.get_content(), view=self.get_view(), embed=self.get_embed())
        else:
            await self.message.edit(content=self.get_content(), view=self.get_view(), embed=self.get_embed())

        if save: self.game.save()
    
    async def close(self, force_keep_message=None):
        if self.closed: return

        self.closed = True
        if (force_keep_message if force_keep_message != None else self.keep_message):
            await self.view.clear()
        else:
            await self.view.delete()

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
            self.get_view().message = self.message
            await self.update(save=False)
        
        return self


class JoinPanel(Panel):
    view_class = JoinView
    keep_message = False
    
    def get_embed(self):
        embed = discord.Embed(color=self.game.mainclass.color)
        embed.title = f"Partie de BOTC | Conteur: {self.game.storyteller.display_name} | Joueurs ({str(len(self.game.players))}) :"
        embed.description = '\n'.join([x.user.mention for x in self.game.players.values()])
        return embed
    

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


class VotePanel(TimedPanel):
    view_class = VoteView

    def __init__(self, game, nominator=None, nominee=None):
        super().__init__(game)
        self.nominator = nominator
        self.nominee = nominee

        self.accusation = "En attente..."
        self.defense = "En attente..."
        self.votes = {}
        self.control_panel = None

    def get_content(self):
        return f"{self.nominator.user.mention}{self.nominee.user.mention}"
    
    def get_embed(self):
        verb = "a appelé à l'exil de" if self.nominee.traveller else "a nominé"
        vote_total = (f"{'?' if self.game.gamerules['hidden_vote'].state else sum(1 for x in self.votes.values() if x == self.game.mainclass.emojis['for'])}"
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
            name="👉 Accusation",
            value=self.accusation
        )

        embed.add_field(
            name="✋ Défense",
            value=self.defense
        )

        for id, vote in self.votes.items():
            player = self.game.players[id]

            value = vote
            if self.game.gamerules["hidden_vote"].state: value = "🙈"

            icon = ""
            if self.nominator == player: icon = "👉"
            if self.nominee == player: icon = "✋"

            embed.add_field(
                name=f"{icon} {player}",
                value=value,
                inline=False
            )
    
        return embed

    async def send(self, channel):
        self.control_panel = await VoteControlPanel(self.game, self).send(self.game.control_thread)
        if not self.nominee.traveller: self.nominator.has_nominated = True
        self.nominee.was_nominated = True
        self.votes = {i: "❔" if self.can_player_vote(x) else self.game.mainclass.emojis["against"] for i,x in self.game.players.items()}
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
    
    async def update_vote(self, id, vote, interaction):
        player = self.game.players[id]
        if not self.can_player_vote(player) and self.game.gamerules["dead_vote_required"].state:
            return await interaction.response.send_message("Vous n'avez plus de jeton de vote.", ephemeral=True)

        self.votes[id] = vote
        await self.update(interaction)

    def serialize(self):
        object = super().serialize()
        object["nominator"] = self.nominator.user.id
        object["nominee"] = self.nominator.user.id
        object["accusation"] = self.accusation
        object["defense"] = self.defense
        object["votes"] = self.votes
        object["control_panel"] = self.control_panel.serialize() if self.control_panel else None
        return object
    
    async def parse(self, object, client):
        self.nominator = self.game.players[object["nominator"]]
        self.nominee = self.game.players[object["nominee"]]
        self.accusation = object["accusation"]
        self.defense = object["defense"]
        self.votes = {int(i): x for i,x in object["votes"].items()}
        self.control_panel = await VoteControlPanel(self.game, self).parse(object["control_panel"], client) if object["control_panel"] else None
        return await super().parse(object, client)


class ControlPanel(Panel):
    view_class = ControlView
    
    def get_embed(self):
        embed = discord.Embed(
            color=self.game.mainclass.color,
            title="⚙️ Panneau de contrôle"
        )
        embed.add_field(name="Joueurs", value='\n'.join(f'- {player}' for player in self.game.players.values()))
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
        embed.add_field(name="Total", value=f"{sum(1 for x in self.vote_panel.votes.values() if x == self.game.mainclass.emojis['for'])}/{self.game.required_votes_for_exile if self.vote_panel.nominee.traveller else self.game.required_votes}")

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
        self.vote_panel.votes[id] = self.game.mainclass.emojis["for"]
        await self.next_player(interaction)

    async def count_as_against(self, interaction):
        id = self.player_ids.pop()
        self.vote_panel.votes[id] = self.game.mainclass.emojis["against"]
        await self.next_player(interaction)

    async def next_player(self, interaction):
        if len(self.player_ids) == 0: 
            await self.vote_panel.update(save=False)
            await self.game.phases["nominations"].close_vote(self.vote_panel.message.id)
            await self.update(interaction)
            await self.close(force_keep_message=self.game.gamerules["hidden_vote"].state)
            return

        next_vote = self.vote_panel.votes[self.player_ids[-1]]
        if next_vote == self.game.mainclass.emojis["for"]: return await self.count_as_for(interaction)
        if next_vote == self.game.mainclass.emojis["against"]: return await self.count_as_against(interaction)
        await self.update(interaction)

    def serialize(self):
        object = super().serialize()
        object["player_ids"] = self.player_ids
        return object

    async def parse(self, object, client):
        self.player_ids = [int(x) for x in object["player_ids"]] if object["player_ids"] else None
        return await super().parse(object, client)
