"""Phase classes."""

import discord

from modules.botc.panels import Panel, JoinPanel, NominationPanel, VotePanel


class Phase:
    def __init__(self, game):
        self.game = game

    async def on_enter(self):
        pass

    async def on_command(self, message, args, kwargs):
        pass

    async def on_interaction(self, event, interaction, *args):
        await interaction.response.defer()

    async def on_exit(self):
        pass


class PanelPhase(Phase):
    panel_class = Panel

    async def send(self, channel):
        self.channel = channel
        await self.game.change_panel(await self.panel_class(self.game).send(channel))

    async def on_exit(self):
        if self.game.current_panel: await self.game.current_panel.close()
        self.game.current_panel = None


class StartPhase(PanelPhase):
    panel_class = JoinPanel

    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == "create":
            await self.send(message.channel)
            return


class NightPhase(Phase):
    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == "day":
            await self.game.change_phase("day")
            await message.delete()
            return

        if args[0] == "open":
            if len(args) < 2: return
            await self.game.change_phase("day")
            await self.game.current_phase.on_command(message, args, kwargs)
            return

    async def on_enter(self):
        await self.game.channel.send(embed=discord.Embed(color=0xffffff, title="🌙 La nuit tombe sur le village..."))
        for player in self.game.players.values():
            player.has_nominated = False
            player.was_nominated = False


class DayPhase(Phase):
    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == "open":
            if len(args) < 2: return
            await self.game.change_phase("nominations")
            await self.game.current_phase.on_command(message, args, kwargs)
            return
        
        if args[0] == "night":
            await self.game.change_phase("night")
            await message.delete()
            return
        
    async def on_enter(self):
        await self.game.channel.send(embed=discord.Embed(color=0xffffff, title="☀️ Le jour se lève!"))


class NominationsPhase(PanelPhase):
    panel_class = NominationPanel

    def __init__(self, game):
        super().__init__(game)
        self.vote_panels = []
        self.nomination_thread = None

    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == "open":
            self.nomination_thread = await message.channel.create_thread(name=' '.join(args[1:]), auto_archive_duration=24*60, type=discord.ChannelType.public_thread)
            await self.nomination_thread.add_user(self.game.storyteller)
            for player in self.game.players.values(): await self.nomination_thread.add_user(player.user)
            # await self.nomination_thread.edit(locked=True)

            await self.send(self.nomination_thread)
            await message.delete()
            return
        
        if args[0] == "close":
            await self.game.current_panel.channel.send(embed=discord.Embed(color=0xffffff, title="Les nouvelles nominations sont maintenant fermées!"))
            await self.game.current_panel.close()
            await message.delete()
            return
        
        if args[0] == "night":
            await self.game.change_phase("night")
            await message.delete()
            return
        
    async def on_interaction(self, event, interaction, *args):
        if event == "start_vote":
            vote_panel = await VotePanel(self.game, self.game.players[interaction.user.id], args[0]).send(self.channel)
            self.vote_panels.append(vote_panel)
            await interaction.response.defer()
            return

        await super().on_interaction(event, interaction, *args)
        
    async def on_exit(self):
        await super().on_exit()
        for panel in self.vote_panels: await panel.close()
        await self.nomination_thread.archive()
        self.vote_panels = []
