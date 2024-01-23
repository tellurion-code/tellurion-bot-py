"""Phase classes."""

import discord

from modules.botc.panels import Panel, JoinPanel, NominationPanel, VotePanel, ControlPanel


class Phase:
    def __init__(self, game):
        self.game = game

    async def on_enter(self):
        pass

    async def on_command(self, message, args, kwargs):
        return False

    async def on_interaction(self, event, interaction, *args):
        await interaction.response.defer()

    async def on_exit(self):
        pass

    def serialize(self):
        return {}

    async def parse(self, object, client):
        return self


class PanelPhase(Phase):
    panel_class = Panel

    def __init__(self, game):
        super().__init__(game)
        self.panel = None

    async def send(self, channel):
        self.panel = await self.panel_class(self.game).send(channel)

    async def update(self, save=True):
        if self.panel: await self.panel.update(save=save)

    async def close(self):
        await self.panel.close()
        self.panel = None

    async def on_exit(self):
        if self.panel: await self.panel.close()
        self.panel = None

    def serialize(self):
        object = super().serialize()
        object["panel"] = self.panel.serialize() if self.panel else None
        return object
    
    async def parse(self, object, client):
        self.panel = await self.panel_class(self.game).parse(object["panel"], client) if object["panel"] else None
        return await super().parse(object, client)


class StartPhase(PanelPhase):
    panel_class = JoinPanel

    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == None:
            await self.send(message.channel)
            return False
        
        return await super().on_command(message, args, kwargs)

    async def on_exit(self):
        self.game.control_thread = await self.panel.channel.create_thread(name="Salle de contrôle", type=discord.ChannelType.private_thread)
        await self.game.control_thread.add_user(self.game.storyteller)
        self.game.control_panel = await ControlPanel(self.game).send(self.game.control_thread)
        await super().on_exit()


class NightPhase(Phase):
    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == "day":
            await self.game.change_phase("day")
            return True

        if args[0] == "open":
            if not self.game.phases["nominations"].nomination_thread and len(args) < 2: return False
            await self.game.change_phase("day")
            return await self.game.current_phase.on_command(message, args, kwargs)
        
        return await super().on_command(message, args, kwargs)

    async def on_enter(self):
        await self.game.channel.send(embed=discord.Embed(color=0xffffff, title="🌙 La nuit tombe sur le village..."))
        for player in self.game.players.values():
            player.has_nominated = False
            player.was_nominated = False


class DayPhase(Phase):
    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == "open":
            if not self.game.phases["nominations"].nomination_thread and len(args) < 2: return False
            await self.game.change_phase("nominations")
            return await self.game.current_phase.on_command(message, [None, *args[1:]], kwargs)
        
        if args[0] == "night":
            await self.game.change_phase("night")
            return True
        
        return await super().on_command(message, args, kwargs)
        
    async def on_enter(self):
        await self.game.channel.send(embed=discord.Embed(color=0xffffff, title="☀️ Le jour se lève!"))


class NominationsPhase(PanelPhase):
    panel_class = NominationPanel

    def __init__(self, game):
        super().__init__(game)
        self.vote_panels = {}
        self.nomination_thread = None

    async def on_command(self, message, args, kwargs):
        if message.author != self.game.storyteller: return

        if args[0] == None:
            if len(args) > 1:
                name = ' '.join(args[1:])
                self.nomination_thread = await message.channel.create_thread(name=name, auto_archive_duration=24*60, type=discord.ChannelType.public_thread)
                await self.nomination_thread.add_user(self.game.storyteller)
                for player in self.game.players.values(): await self.nomination_thread.add_user(player.user)
                # await self.nomination_thread.edit(locked=True)

            await self.send(self.nomination_thread)
            return True
        
        if args[0] == "close":
            await self.panel.channel.send(embed=discord.Embed(color=0xffffff, title="Les nouvelles nominations sont maintenant fermées!"))
            await self.close()
            return True
        
        if args[0] == "night":
            await self.game.change_phase("night")
            return True
        
        return await super().on_command(message, args, kwargs)
        
    async def on_interaction(self, event, interaction, *args):
        if event == "start_vote":
            vote_panel = await VotePanel(self.game, self.game.players[interaction.user.id], args[0]).send(self.nomination_thread)
            self.vote_panels[vote_panel.message.id] = vote_panel
            self.game.save()
            await interaction.response.defer()
            return

        await super().on_interaction(event, interaction, *args)

    async def close_vote(self, id):
        if id not in self.vote_panels: return

        await self.vote_panels[id].close()
        del self.vote_panels[id]
        
    async def on_exit(self):
        await super().on_exit()
        for panel in self.vote_panels: await panel.close()
        await self.nomination_thread.archive()
        self.vote_panels = {}

    def serialize(self):
        object = super().serialize()
        object["vote_panels"] = {i: x.serialize() for i, x in self.vote_panels.items()}
        object["nomination_thread"] = self.nomination_thread.id if self.nomination_thread else None
        return object
    
    async def parse(self, object, client):
        self.vote_panels = {int(i): await VotePanel(self.game).parse(x, client) for i, x in object["vote_panels"].items()}
        self.nomination_thread = await client.fetch_channel(object["nomination_thread"]) if object["nomination_thread"] else None
        return await super().parse(object, client)
