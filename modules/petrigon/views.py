"""View classes."""

import discord

from modules.game.views import GameView, PlayView
from modules.petrigon.player import Player
from modules.petrigon.hex import Hex
from modules.petrigon.power import Power
from modules.petrigon.types import Announcement


class PanelView(GameView):
    update_on_init = False

    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.panel = panel
        if self.update_on_init: self.update()

    def update(self):
        pass


class JoinView(PanelView):
    def check_for_enough_players(self):
        if self.game.mainclass.debug:
            return True, "Démarrer"

        if len(self.game.players) < 2:
            return False, "Pas assez de joueurs"
        
        if len(self.game.players) > 6:
            return False, "Trop de joueurs"
        
        return True, "Démarrer"

    def update(self):
        super().update()
        can_start, message = self.check_for_enough_players()
        self.children[1].label = message
        self.children[1].disabled = not can_start
        self.children[1].style = discord.ButtonStyle.green if can_start else discord.ButtonStyle.gray

    @discord.ui.button(label="Rejoindre ou quitter", style=discord.ButtonStyle.blurple)
    async def join_or_leave(self, button, interaction):
        if len(self.game.players) > 6:
            return await interaction.response.send_message("Le nombre maximum de joueurs est atteint.", ephemeral=True)

        if interaction.user.id not in self.game.players:
            self.game.players[interaction.user.id] = Player(self.game, interaction.user)
        else:
            del self.game.players[interaction.user.id]

        await self.panel.update(interaction)
    
    @discord.ui.button(label="Pas assez de joueurs", disabled=True, style=discord.ButtonStyle.gray)
    async def start(self, button, interaction):
        if interaction.user.id not in self.game.players:
            return await interaction.response.defer()

        await self.game.start()

    @discord.ui.button(label="Pouvoirs désactivés", emoji="🦸", style=discord.ButtonStyle.gray)
    async def toggle_powers(self, button, interaction):
        if interaction.user.id in self.game.players:
            self.game.powers_enabled = not self.game.powers_enabled
            button.label = f"Pouvoirs {'activés' if self.game.powers_enabled else 'désactivés'}" 
            button.style = discord.ButtonStyle.green if self.game.powers_enabled else discord.ButtonStyle.gray
            return await self.panel.update(interaction)

        await interaction.response.defer()


class PowerView(PanelView, PlayView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs)

        self.power_classes = {x.__name__: x for x in (*Power.__subclasses__(), Power)}
        options = [discord.SelectOption(label=subclass.name, emoji=subclass.icon, value=key) for key, subclass in self.power_classes.items()]
        
        self.select = discord.ui.Select(options=options, placeholder="Choisissez un pouvoir")
        self.select.callback = self.callback
        self.add_item(self.select)
        

    def check_for_selection(self):
        if sum(1 for x in self.game.players.values() if not x.power) > 0:
            return False, "Choix restants à faire"
        
        return True, "Démarrer"

    def update(self):
        super().update()
        can_start, message = self.check_for_selection()
        self.children[0].label = message
        self.children[0].disabled = not can_start
        self.children[0].style = discord.ButtonStyle.green if can_start else discord.ButtonStyle.gray

    async def callback(self, interaction):
        self.game.players[interaction.user.id].set_power(self.power_classes[self.select.values[0]])
        await self.panel.update(interaction)

    @discord.ui.button(label="Choix restants à faire", disabled=True, style=discord.ButtonStyle.gray, row=1)
    async def start(self, button, interaction):
        await self.game.finish_power_selection(interaction)


class FightView(PanelView, PlayView):
    update_on_init = True

    def update(self):
        self.children[7].disabled = not (self.game.current_player.power and self.game.current_player.power.active)

    @discord.ui.button(emoji="↖️", style=discord.ButtonStyle.blurple)
    async def move_up_left(self, button, interaction):
        await self.try_to_move(interaction, button.emoji, Hex(0, -1))

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.blurple)
    async def move_left(self, button, interaction):
        await self.try_to_move(interaction, button.emoji, Hex(-1, 0))

    @discord.ui.button(emoji="↗️", style=discord.ButtonStyle.blurple)
    async def move_up_right(self, button, interaction):
        await self.try_to_move(interaction, button.emoji, Hex(1, -1))
    
    @discord.ui.button(emoji="↙️", style=discord.ButtonStyle.blurple, row=1)
    async def move_down_left(self, button, interaction):
        await self.try_to_move(interaction, button.emoji, Hex(-1, 1))
    
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple, row=1)
    async def move_right(self, button, interaction):
        await self.try_to_move(interaction, button.emoji, Hex(1, 0))
    
    @discord.ui.button(emoji="↘️", style=discord.ButtonStyle.blurple, row=1)
    async def move_down_right(self, button, interaction):
        await self.try_to_move(interaction, button.emoji, Hex(0, 1))

    async def try_to_move(self, interaction, emoji, direction):
        if interaction.user != self.game.current_player.user:
            return await interaction.response.defer()
        
        if self.game.current_player.move(direction):
            self.game.last_input = emoji
            await self.game.current_player.end_turn(interaction)
        else:
            await interaction.response.send_message("Ce mouvement ne cause aucun changement du plateau.", ephemeral=True)

    @discord.ui.button(emoji="💀", style=discord.ButtonStyle.red)
    async def forfeit(self, button, interaction):
        player = self.game.players[interaction.user.id]
        player.forfeit()
        
        if player == self.game.current_player:
            await self.game.next_turn(interaction)
        else:
            await self.game.check_for_game_end(interaction)

    @discord.ui.button(emoji="🦸", style=discord.ButtonStyle.green, row=1)
    async def use_ability(self, button, interaction):
        if interaction.user != self.game.current_player.user:
            return await interaction.response.defer()
        
        if self.game.current_player.use_power():
            await self.panel.update(interaction)
        else:
            await interaction.response.send_message("Vous ne pouvez pas utiliser votre pouvoir.", ephemeral=True)
