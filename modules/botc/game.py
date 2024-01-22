"""Game class."""

import discord
from dataclasses import dataclass

from modules.botc.phases import StartPhase, NominationsPhase, NightPhase, DayPhase
from modules.botc.panels import ControlPanel

@dataclass
class Gamerule:
    name: str
    state: bool


class Game:
    def __init__(self, mainclass, message=None):
        self.mainclass = mainclass

        self.players = {}
        if message:
            self.storyteller = message.author
            self.channel = message.channel

        self.phases = {
            "start": StartPhase(self),
            "night": NightPhase(self),
            "day": DayPhase(self),
            "nominations": NominationsPhase(self),
        }
        self.phase = ""

        self.current_panel = None
        self.control_thread = None

        self.gamerules = {
            "only_nominate_once": Gamerule("Nominer une fois par jour", True),
            "only_be_nominated_once": Gamerule("Être nominé une fois par jour", True),
            "dead_vote_required": Gamerule("Jeton de vote de mort nécessaire", True),
            "hidden_vote": Gamerule("Votes cachés des joueurs", False)
        }

    @property
    def current_phase(self):
        return self.phases[self.phase]
    
    @property
    def required_votes(self):
        return round(sum(1 for x in self.players.values() if x.alive) / 2)
    
    @property
    def required_votes_for_exile(self):
        return round(len(self.players) / 2)

    async def reload(self, object, client):
        pass

    async def on_creation(self, message, args):
        await self.change_phase("start")
        await self.current_phase.on_command(message, args, {})

    async def start_game(self):
        self.control_thread = await self.current_panel.channel.create_thread(name="Salle de contrôle", type=discord.ChannelType.private_thread)
        await self.control_thread.add_user(self.storyteller)
        self.control_panel = await ControlPanel(self).send(self.control_thread)

        await self.change_phase("night")

    async def change_panel(self, panel):
        if self.current_panel: await self.current_panel.close()
        self.current_panel = panel

    async def change_phase(self, phase):
        if self.phase == phase: return
        if self.phase: await self.current_phase.on_exit()
        self.phase = phase
        await self.current_phase.on_enter()

    async def on_command(self, message, args, kwargs):
        await self.current_phase.on_command(message, args, kwargs)

    async def end(self):
        await self.current_phase.on_exit()
        if self.control_panel: await self.control_panel.close()
        if self.control_thread: await self.control_thread.archive()
        if self.current_panel: await self.current_panel.close()
