"""Panel classes (mesages with views)"""

import discord
import math

from modules.petrigon import constants
from modules.petrigon.views import FightView, PanelView, JoinView, PowerActivationView, PowerView


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
        return None

    @property
    def view(self):
        if self.closed:
            return None
        
        if not self._view: 
            self._view = self.view_class(self.game, self)
        else:
            self._view.update()
        
        return self._view

    async def send(self, channel):
        self.channel = channel
        self.message = await channel.send(content=self.content, view=self.view, embed=self.embed)
        return self
    
    async def reply(self, interaction, ephemeral=False):
        self.channel = interaction.channel
        self.message = await interaction.response.send_message(content=self.content, view=self.view, embed=self.embed, ephemeral=ephemeral)
        return self
    
    async def update(self, interaction=None, save=True):
        if interaction:
            await interaction.response.defer()
        
        await self.message.edit(content=self.content, view=self.view, embed=self.embed)
        if save: self.game.save()
    
    async def close(self, force_keep_message=None):
        if self.closed: return

        self.closed = True
        if not self._view: return
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
        embed.title = f"Partie de Petrigon | Joueurs ({len(self.game.players)}) :"
        embed.description = '\n'.join([f"- {x}" for x in self.game.players.values()])
        return embed
    

class PowerPanel(Panel):
    view_class = PowerView
    keep_message = False

    @property
    def embed(self):
        embed = discord.Embed(color=self.game.mainclass.color)
        embed.title = f"Choix des pouvoirs"
        embed.description = '\n'.join([
            f"{constants.TILE_COLORS[i+2]} {self.game.players[id]}: {'✅' if len(self.game.players[id].powers) else '❌'}" for i, id in enumerate(self.game.order)
        ])
        return embed


class FightPanel(Panel):
    view_class = FightView
    
    @property
    def embed(self):
        embed = discord.Embed(color=constants.PLAYER_COLORS[self.game.turn])
        embed.title = f"Petrigon | Manche {self.game.round} | Tour de {self.game.current_player}"
        embed.description = f"### Plateau{' | Dernier choix: ' + self.game.last_input if self.game.last_input else ''}\n{self.game.map}"

        for announcement in self.game.announcements:
            embed.add_field(
                name=announcement.name,
                value=announcement.value,
                inline=False
            )

        embed.add_field(
            name=f"Joueurs | Score de Domination: {self.game.domination_score}",
            value='\n'.join(self.game.players[id].info() for id in self.game.order)
        )

        return embed


class PowerActivationPanel(Panel):
    view_class = PowerActivationView
    keep_message = False

    def __init__(self, game, powers):
        super().__init__(game)
        self.powers = powers

    async def reply(self, interaction):
        if len(self.powers) == 1: return await self.resolve_power(next(iter(self.powers)), interaction)
        return await super().reply(interaction, ephemeral=True)

    @property
    def content(self):
        return "Vous avez plusieurs pouvoirs activables"
    
    async def resolve_power(self, power, interaction):
        if self.powers[power].use():
            await self.close()
            await self.game.panel.update(interaction)
        else:
            await interaction.response.send_message("Vous ne pouvez pas utiliser votre pouvoir.", ephemeral=True)