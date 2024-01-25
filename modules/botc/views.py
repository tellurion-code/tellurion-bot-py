"""Views."""

import discord
import modules.botc.phases as phases

from modules.game.views import GameView, PlayView
from modules.botc.player import Player
from modules.botc.components import PlayerSelect


class PanelView(GameView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.panel = panel

    def update(self):
        pass


class JoinView(PanelView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs)

        self.input_modal = discord.ui.Modal(discord.ui.InputText(label="Nombre de joueurs", max_length=2), title="Combien de joueurs au maximum?")
        self.input_modal.callback = self.update_max_players
    
    # def update(self):
    #     super().update()
    #     can_start, message = self.check_for_enough_players()
    #     self.children[1].label = message
    #     self.children[1].disabled = not can_start
    #     self.children[1].style = discord.ButtonStyle.green if can_start else discord.ButtonStyle.gray

    @discord.ui.button(label="Rejoindre ou quitter", style=discord.ButtonStyle.blurple)
    async def join_or_leave(self, button, interaction):
        if len(self.game.players) >= self.game.phases[phases.Phases.start].max_players:
            return await interaction.response.send_message("Le nombre maximum de joueurs est atteint.", ephemeral=True)

        if interaction.user.id not in self.game.players:
            if interaction.user != self.game.storyteller or self.game.mainclass.debug:
                self.game.players[interaction.user.id] = Player(self.game, interaction.user)
        else:
            del self.game.players[interaction.user.id]

        await self.panel.update(interaction)
    
    # @discord.ui.button(label="Pas assez de joueurs", disabled=True, style=discord.ButtonStyle.gray)
    # async def start(self, button, interaction):
    #     if interaction.user != self.game.storyteller:
    #         return await interaction.response.defer()

    #     await self.game.start_game()

    @discord.ui.button(label="Changer le nombre max de joueurs", style=discord.ButtonStyle.gray)
    async def send_input_modal(self, button, interaction):
        if interaction.user != self.game.storyteller:
            return await interaction.response.defer()

        await interaction.response.send_modal(self.input_modal)

    async def update_max_players(self, interaction):
        value = self.input_modal.children[0].value
        try:
            amount = int(value)
        except ValueError:
            return await interaction.response.send_message(f"{value} n'est pas un nombre.", ephemeral=True)
        
        if not self.game.mainclass.debug and amount < 5 or amount > 15:
            return await interaction.response.send_message(f"{amount} n'est pas un nombre valide de joueurs (entre 5 et 15).", ephemeral=True)
        
        await self.panel.update_max_players(amount, interaction)


class NominationView(PlayView, PanelView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs)
        self.timeout = None

        self.player_select = PlayerSelect(
            self.game,
            placeholder="Nominer un joueur...",
            min_values=1,
            max_values=1
        )
        self.player_select.callback = self.nominate
        self.add_item(self.player_select)

    def update(self):
        super().update()
        self.player_select.update()

    async def interaction_check(self, interaction):
        return await super().interaction_check(interaction) and discord.utils.utcnow() < self.panel.end_time
    
    async def on_check_failure(self, interaction):
        if discord.utils.utcnow() > self.panel.end_time:
            return await interaction.response.send_message("Les nominations sont terminées.", ephemeral=True)
        
        await super().on_check_failure(interaction)

    async def nominate(self, interaction):
        player = self.game.players[interaction.user.id]
        if player.has_nominated and self.game.gamerules["only_nominate_once"].state:
            return await interaction.response.send_message("Vous avez déjà nominé aujourd'hui.", ephemeral=True)
        
        target = self.game.players[int(self.player_select.values[0])]
        if target.was_nominated and self.game.gamerules["only_be_nominated_once"].state: 
            return await interaction.response.send_message("Ce joueur a déjà été nominé aujourd'hui.", ephemeral=True)
        
        if not player.alive and not target.traveller: 
            return await interaction.response.send_message("Vous ne pouvez pas nominer, vous êtes mort.", ephemeral=True)
            
        await self.game.current_phase.on_interaction("start_vote", interaction, target)


class VoteView(PlayView, PanelView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs)
        self.timeout = None

        self.accusation_modal = discord.ui.Modal(discord.ui.InputText(label=f"Votre accusation", max_length=200), title="Accusation")
        self.accusation_modal.callback = self.update_accusation

        self.defense_modal = discord.ui.Modal(discord.ui.InputText(label=f"Votre défense", max_length=200), title="Défense")
        self.defense_modal.callback = self.update_defense
        
        self.vote_modal = discord.ui.Modal(discord.ui.InputText(label=f"Votre vote", max_length=100), title="Vote")
        self.vote_modal.callback = self.update_vote

    async def interaction_check(self, interaction):
        return await super().interaction_check(interaction) and discord.utils.utcnow() < self.panel.end_time
    
    async def on_check_failure(self, interaction):
        if discord.utils.utcnow() > self.panel.end_time:
            return await interaction.response.send_message("Le vote est terminé.", ephemeral=True)
        
        await super().on_check_failure(interaction)

    @discord.ui.button(label="Accusation", style=discord.ButtonStyle.gray)
    async def write_accusation(self, button, interaction):
        if interaction.user != self.panel.nominator.user:
            await interaction.response.defer()
            return
        
        await interaction.response.send_modal(self.accusation_modal)

    @discord.ui.button(label="Défense", style=discord.ButtonStyle.gray)
    async def write_defense(self, button, interaction):
        if interaction.user != self.panel.nominee.user:
            await interaction.response.defer()
            return
        
        await interaction.response.send_modal(self.defense_modal)

    @discord.ui.button(label="Vote", style=discord.ButtonStyle.blurple)
    async def write_vote(self, button, interaction):
        await interaction.response.send_modal(self.vote_modal)

    async def update_accusation(self, interaction):
        await self.panel.update_accusation(self.accusation_modal.children[0].value, interaction)
    
    async def update_defense(self, interaction):
        await self.panel.update_defense(self.defense_modal.children[0].value, interaction)

    async def update_vote(self, interaction):
        await self.panel.update_vote(interaction.user.id, self.vote_modal.children[0].value, interaction)

    @discord.ui.button(label="Pour", style=discord.ButtonStyle.green)
    async def vote_for(self, button, interaction):
        await self.panel.update_vote(interaction.user.id, self.game.mainclass.emojis["for"], interaction)

    @discord.ui.button(label="Contre", style=discord.ButtonStyle.red)
    async def vote_against(self, button, interaction):
        await self.panel.update_vote(interaction.user.id, self.game.mainclass.emojis["against"], interaction)


class ControlView(PanelView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs)

        self.player_select = PlayerSelect(
            self.game,
            placeholder="Choisissez un (des) joueur(s) à affecter",
            max_values=len(self.game.players)
        )
        self.player_select.callback = self.player_callback
        self.add_item(self.player_select)

        options = self.get_gamerules_options()
        self.gamerules_select = discord.ui.Select(
            placeholder="Règles actives",
            options=options,
            max_values=len(self.game.gamerules)
        )
        self.gamerules_select.callback = self.gamerules_callback
        self.add_item(self.gamerules_select)

    def update(self):
        super().update()
        self.player_select.update()

    async def interaction_check(self, interaction):
        return interaction.user == self.game.storyteller

    def get_gamerules_options(self):
        options = []
        for id, gamerule in self.game.gamerules.items():
            options.append(discord.SelectOption(
                label=gamerule.name,
                value=id,
                default=gamerule.state
            ))
        
        return options
        
    async def player_callback(self, interaction):
        await interaction.response.defer()

    async def gamerules_callback(self, interaction):
        for id in self.game.gamerules:
            self.game.gamerules[id].state = id in self.gamerules_select.values

        self.gamerules_select.options = self.get_gamerules_options()
        await self.panel.update(interaction, global_update=False)

    @discord.ui.button(label="Mort", emoji="💀", style=discord.ButtonStyle.red)
    async def kill_players(self, button, interaction):
        for value in self.player_select.values:
            self.game.players[int(value)].alive = False

        await self.panel.update(interaction)

    @discord.ui.button(label="Vivant", style=discord.ButtonStyle.green)
    async def raise_players(self, button, interaction):
        for value in self.player_select.values:
            self.game.players[int(value)].alive = True
            self.game.players[int(value)].dead_vote = True

        await self.panel.update(interaction)

    @discord.ui.button(label="Sans jeton", emoji="🚫", style=discord.ButtonStyle.gray)
    async def remove_dead_vote(self, button, interaction):
        for value in self.player_select.values:
            player = self.game.players[int(value)]
            if not player.alive: player.dead_vote = False

        await self.panel.update(interaction)

    @discord.ui.button(label="Voyageur", emoji="🎒", style=discord.ButtonStyle.blurple)
    async def make_traveller(self, button, interaction):
        for value in self.player_select.values:
            self.game.players[int(value)].traveller = True

        await self.panel.update(interaction)

    @discord.ui.button(label="Résident", style=discord.ButtonStyle.blurple)
    async def make_resident(self, button, interaction):
        for value in self.player_select.values:
            self.game.players[int(value)].traveller = False

        await self.panel.update(interaction)


class VoteControlView(PanelView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs)

    @discord.ui.button(label="Compter comme Pour", style=discord.ButtonStyle.green)
    async def count_as_for(self, interaction):
        await self.panel.count_as_for(interaction)
    
    @discord.ui.button(label="Compter comme Contre", style=discord.ButtonStyle.red)
    async def count_as_against(self, interaction):
        await self.panel.count_as_against(interaction)
