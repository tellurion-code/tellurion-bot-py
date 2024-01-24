"""Game class."""

import discord
import random

from dataclasses import dataclass

from modules.botc.phases import Phases, StartPhase, NominationsPhase, NightPhase, DayPhase
from modules.botc.panels import ControlPanel
from modules.botc.player import Player


@dataclass
class Gamerule:
    name: str
    state: bool


class Game:
    def __init__(self, mainclass, message=None):
        self.mainclass = mainclass

        self.order = []
        self.players = {}
        if message:
            self.id = max((x.id for x in self.mainclass.games.values()), default=0) + 1
            self.storyteller = message.author
            self.channel = message.channel

        self.phases = {
            Phases.start: StartPhase(self),
            Phases.night: NightPhase(self),
            Phases.day: DayPhase(self),
            Phases.nominations: NominationsPhase(self),
        }
        self.phase = None

        self.control_thread = None
        self.control_panel = None
        self.role = None

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

    def player_from_mention(self, mention):
        ids = discord.utils.raw_mentions(mention)
        if len(ids) == 0: return None
        if ids[0] not in self.players: return None
        return self.players[ids[0]]

    def order_from(self, id):
        if id not in self.players: return self.order
        index = (self.order.index(id) + len(self.order) - 1) % len(self.order)
        return self.order[index:] + self.order[:index]

    async def on_creation(self, message):
        self.role = await self.channel.guild.create_role(name=f"BotC {self.id}", color=self.mainclass.color, mentionable=True)

        await self.change_phase(Phases.start)
        await self.current_phase.on_command(message, [None], {})
        self.save()

    async def start_game(self):
        self.order = [id for id in self.players]
        random.shuffle(self.order)

        self.control_thread = await self.channel.create_thread(name="Salle de contrôle", type=discord.ChannelType.private_thread)
        await self.control_thread.add_user(self.storyteller)
        self.control_panel = await ControlPanel(self).send(self.control_thread)
        await self.control_panel.message.pin()

        await self.storyteller.add_roles(self.role)
        for player in self.players.values():
            await player.user.add_roles(self.role)

        await self.change_phase(Phases.night)
        self.save()

    async def change_phase(self, phase):
        if self.phase == phase: return
        if self.phase: await self.current_phase.on_exit()
        self.phase = phase
        await self.current_phase.on_enter()

    async def on_command(self, message, args, kwargs):
        return await self.current_phase.on_command(message, args, kwargs)

    async def end(self):
        await self.role.delete()
        await self.current_phase.on_exit()
        if self.control_panel: await self.control_panel.close()
        if self.control_thread: await self.control_thread.archive()
        self.delete_save()
    
    def serialize(self):
        return {
            "id": self.id,
            "storyteller": self.storyteller.id,
            "channel": self.channel.id,
            "order": self.order,
            "players": {i: x.serialize() for i,x in self.players.items()},
            "phase": self.phase.value,
            "phases": {i.value: x.serialize() for i,x in self.phases.items()},
            "gamerules": {i: x.state for i,x in self.gamerules.items()},
            "control_thread": self.control_thread.id if self.control_thread else None,
            "control_panel": self.control_panel.serialize() if self.control_panel else None,
            "role": self.role.id
        }

    async def parse(self, object, client):
        self.id = object["id"]
        self.channel = await client.fetch_channel(object["channel"])
        self.storyteller = await self.channel.guild.fetch_member(object["storyteller"])
        self.players = {int(i): await Player(self).parse(x, client) for i,x in object["players"].items()}
        self.order = [int(i) for i in object["order"]]
        self.phase = Phases(object["phase"])
        
        self.control_thread = await client.fetch_channel(object["control_thread"]) if object["control_thread"] else None
        self.control_panel = await ControlPanel(self).parse(object["control_panel"], client) if object["control_panel"] else None
        self.role = next((x for x in self.channel.guild.roles if x.id == object["role"]), None)
        
        for key, phase in self.phases.items(): 
            await phase.parse(object["phases"][key.value], client)
        
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
