"""Game class."""

import discord
from dataclasses import dataclass

from modules.botc.phases import StartPhase, NominationsPhase, NightPhase, DayPhase
from modules.botc.panels import ControlPanel
from modules.botc.player import Player

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

        self.control_thread = None
        self.control_panel = None

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

    async def on_creation(self, message):
        await self.change_phase("start")
        await self.current_phase.on_command(message, [None], {})
        self.save()

    async def start_game(self):
        await self.change_phase("night")
        self.save()

    async def change_phase(self, phase):
        if self.phase == phase: return
        if self.phase: await self.current_phase.on_exit()
        self.phase = phase
        await self.current_phase.on_enter()

    async def on_command(self, message, args, kwargs):
        return await self.current_phase.on_command(message, args, kwargs)

    async def end(self):
        await self.current_phase.on_exit()
        if self.control_panel: await self.control_panel.close()
        if self.control_thread: await self.control_thread.archive()
        self.delete_save()
    
    def serialize(self):
        return {
            "storyteller": self.storyteller.id,
            "channel": self.channel.id,
            "players": {i: x.serialize() for i,x in self.players.items()},
            "phase": self.phase,
            "phases": {i: x.serialize() for i,x in self.phases.items()},
            "gamerules": {i: x.state for i,x in self.gamerules.items()},
            "control_thread": self.control_thread.id if self.control_thread else None,
            "control_panel": self.control_panel.serialize() if self.control_panel else None
        }

    async def parse(self, object, client):
        self.storyteller = await client.fetch_user(object["storyteller"])
        self.channel = await client.fetch_channel(object["channel"])
        self.players = {int(i): await Player(self).parse(x, client) for i,x in object["players"].items()}
        self.phase = object["phase"]
        
        self.control_thread = await client.fetch_channel(object["control_thread"]) if object["control_thread"] else None
        self.control_panel = await ControlPanel(self).parse(object["control_panel"], client) if object["control_panel"] else None
        
        for key, phase in self.phases.items(): 
            await phase.parse(object["phases"][key], client)
        
        for key, gamerule in self.gamerules.items(): 
            gamerule.state = object["gamerules"][key]
        
        return self
    
    def save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
        else:
            object = {}

        object[str(self.channel.id)] = self.serialize()
        self.mainclass.objects.save_object("games", object)

    def delete_save(self):
        if self.mainclass.objects.save_exists("games"):
            object = self.mainclass.objects.load_object("games")
            if str(self.channel.id) in object:
                object.pop(str(self.channel.id))

            self.mainclass.objects.save_object("games", object)
        else:
            print("no save")
