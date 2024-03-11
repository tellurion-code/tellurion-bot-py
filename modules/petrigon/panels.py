"""Panel classes (mesages with views)"""

import discord

from modules.petrigon import constants
from modules.petrigon.types import MapImage
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
        embed.description = '\n'.join([f"- {x.player_name(show_name=True)}" for x in self.game.players.values()])
        return embed
    

class PowerPanel(Panel):
    view_class = PowerView
    keep_message = False

    @property
    def embed(self):
        embed = discord.Embed(color=self.game.mainclass.color)
        embed.title = f"Choix des pouvoirs"
        embed.description = '\n'.join([
            f"{constants.TILE_EMOJIS[i+2]} {self.game.players[id].player_name()}: {'✅' if len(self.game.players[id].powers) else '❌'}" for i, id in enumerate(self.game.order)
        ])
        return embed


class FightPanel(Panel):
    view_class = FightView
    keep_message = False

    def __init__(self, game):
        super().__init__(game)
        self.map_images = []
        self.last_map = None
        self.image_url = None
    
    @property
    def embed(self):
        embed = discord.Embed(color=constants.PLAYER_COLORS[self.game.turn])
        embed.title = f"Petrigon | Manche {self.game.round} | Tour de {self.game.current_player.player_name()}"
        embed.description = f"### Plateau{' | Dernier choix: ' + self.game.last_input if self.game.last_input else ''}\n{self.game.map}"
        # embed.set_image(url=self.image_url)

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

    async def send(self, channel):
        map_image = self.update_map_image()
        # self.image_url = await self.get_url(map_image)
        return await super().send(channel)
    
    async def update(self, interaction=None, save=True):
        map_image = self.update_map_image()
        # self.image_url = await self.get_url(map_image)
        return await super().update(interaction, save)
    
    def update_map_image(self):
        if self.last_map != self.game.map:
            image = self.game.map.render()
            self.map_images.append(MapImage(image))
            self.last_map = self.game.map

        return self.map_images[-1]

    async def get_url(self, map_image):
        if map_image.url: return map_image.url

        filename = f"{constants.ASSET_FOLDER}board.png"
        map_image.image.save(filename)
        map_image.url = await self.send_and_get_url(filename)
        return map_image.url

    async def send_and_get_url(self, filename):
        url = None

        # Send the image to a private channel, get the url, then delete it
        config = self.game.mainclass.client.modules["errors"]["initialized_class"].config
        for chanid in config.dev_chan:
            message = await self.game.mainclass.client.get_channel(chanid).send(file=discord.File(filename))
            url = message.attachments[0].url
            await message.delete()
            break
        
        return url
    
    async def end(self, winner, reason, interaction):
        await self.update(interaction)

        embed = discord.Embed(title=f"Petrigon | Victoire de {winner.player_name() if winner else 'personne'} par {reason} (Manche {self.game.round})", color=self.game.mainclass.color)
        embed.description = '\n'.join(self.game.players[id].base_info(show_name=True) for id in self.game.order)

        await self.channel.send(embed=embed, file=discord.File(self.get_game_gif()))
        del self.map_images

    def get_game_gif(self):
        filename = f"{constants.ASSET_FOLDER}game.gif"
        images = [x.image for x in self.map_images]
        images[0].save(filename, save_all=True, append_images=(*images[1:], images[-1], images[-1],), duration=667, loop=0)
        return filename


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
    
    async def resolve_power(self, power_key, interaction):
        power = self.powers[power_key]
        context = power.use(self.game.current_context)

        if context:
            power.send_announcement()
            power.data = power.data_from_context(context)

            await self.close()
            await self.game.panel.update(interaction)
        else:
            await interaction.response.send_message("Vous ne pouvez pas utiliser votre pouvoir.", ephemeral=True)