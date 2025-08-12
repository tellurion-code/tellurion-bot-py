"""View classes."""

import discord

import modules.petrigon.bot as bot
from modules.game.views import GameView, PlayView
from modules.petrigon.hex import Hex
from modules.petrigon.power import ALL_POWERS, Power


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
        self.children[3].label = message
        self.children[3].disabled = not can_start
        self.children[3].style = discord.ButtonStyle.green if can_start else discord.ButtonStyle.gray

    @discord.ui.button(label="Rejoindre ou quitter", style=discord.ButtonStyle.blurple)
    async def join_or_leave(self, button, interaction):
        if len(self.game.players) >= 6:
            return await interaction.response.send_message("Le nombre maximum de joueurs est atteint", ephemeral=True)

        if interaction.user.id not in self.game.players:
            self.game.add_player(interaction.user)
        else:
            del self.game.players[interaction.user.id]

        await self.panel.update(interaction)

    @discord.ui.button(label="+", emoji="🤖", style=discord.ButtonStyle.blurple)
    async def add_bot(self, button, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut changer les paramètres", ephemeral=True)
        
        if len(self.game.players) >= 6:
            return await interaction.response.send_message("Le nombre maximum de joueurs est atteint", ephemeral=True)
        
        self.game.add_bot(depth=2)
        return await self.panel.update(interaction)
    
    @discord.ui.button(label="-", emoji="🤖", style=discord.ButtonStyle.red)
    async def remove_bot(self, button, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut changer les paramètres", ephemeral=True)

        id = min(self.game.players.keys(), default=0)
        if id == 0:
            return await interaction.response.send_message("Aucun bot n'est dans cette partie", ephemeral=True)
        
        del self.game.players[id]
        return await self.panel.update(interaction)
    
    @discord.ui.button(label="Pas assez de joueurs", disabled=True, style=discord.ButtonStyle.gray)
    async def start(self, button, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut la démarrer", ephemeral=True)

        await self.game.prepare_game()

    @discord.ui.button(label="Pouvoirs activés", emoji="🦸", style=discord.ButtonStyle.green, row=1)
    async def toggle_powers(self, button, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut changer les paramètres", ephemeral=True)

        self.game.powers_enabled = not self.game.powers_enabled
        button.label = f"Pouvoirs {'activés' if self.game.powers_enabled else 'désactivés'}" 
        button.style = discord.ButtonStyle.green if self.game.powers_enabled else discord.ButtonStyle.gray
        return await self.panel.update(interaction)
    
    @discord.ui.button(label="Symétrie désactivée", emoji="🔄", style=discord.ButtonStyle.gray, row=1)
    async def toggle_symmetry(self, button, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut changer les paramètres", ephemeral=True)

        self.game.use_symmetry = not self.game.use_symmetry
        button.label = f"Symétrie {'activée' if self.game.use_symmetry else 'désactivée'}" 
        button.style = discord.ButtonStyle.green if self.game.use_symmetry else discord.ButtonStyle.gray
        return await self.panel.update(interaction)

    @discord.ui.button(label="Tournoi désactivé", emoji="🏆", style=discord.ButtonStyle.gray, row=1)
    async def toggle_tournament(self, button, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut changer les paramètres", ephemeral=True)

        self.game.tournament = not self.game.tournament
        button.label = f"Tournoi {'activé' if self.game.tournament else 'désactivé'}" 
        button.style = discord.ButtonStyle.green if self.game.tournament else discord.ButtonStyle.gray
        return await self.panel.update(interaction)


class PowerView(PanelView, PlayView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs)

        self.power_classes = {x.__name__: x for x in (*ALL_POWERS, Power)}
        options = [discord.SelectOption(
            label=subclass.name,
            description=subclass.description,
            emoji=subclass.icon,
            value=key
        ) for key, subclass in self.power_classes.items()]
        
        self.select = discord.ui.Select(options=options, placeholder="Choisissez un pouvoir", max_values=2)
        self.select.callback = self.callback
        self.add_item(self.select)

        self.button = discord.ui.Button(label="Choix restants à faire", disabled=True, style=discord.ButtonStyle.gray, row=1)
        self.button.callback = self.start
        self.add_item(self.button)

        if (any([isinstance(x, bot.GameBot) for x in game.players.values()])):
            self.bot_powers_button = discord.ui.Button(label="Modifier les pouvoirs des bots", style=discord.ButtonStyle.gray, row=2)
            self.bot_powers_button.callback = self.set_bot_powers
            self.add_item(self.bot_powers_button)

        self.update()

    def check_for_selection(self):
        if sum(1 for x in self.game.players.values() if len(x.powers) == 0) > 0:
            return False, "Choix restants à faire"
        
        return True, "Démarrer"

    def update(self):
        super().update()
        can_start, message = self.check_for_selection()
        self.button.label = message
        self.button.disabled = not can_start
        self.button.style = discord.ButtonStyle.green if can_start else discord.ButtonStyle.gray

    async def callback(self, interaction):
        self.game.players[interaction.user.id].set_powers(self.power_classes[x] for x in self.select.values)
        await self.panel.update(interaction)

    async def start(self, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut la démarrer", ephemeral=True)

        await self.game.finish_power_selection(interaction)

    async def set_bot_powers(self, interaction):
        if interaction.user.id != self.game.admin:
            return await interaction.response.send_message("Seul le créateur de la partie peut choisir du pouvoir des bots", ephemeral=True)

        await interaction.response.send_message("Choisissez les pouvoirs des bots", view=BotPowerSelectView(self.game), ephemeral=True)

class BotPowerSelectView(PlayView):
    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)

        self.power_classes = {x.__name__: x for x in (*ALL_POWERS, Power)}
        self.update()

    def update(self):
        self.clear_items()
        for id in self.game.order:
            if isinstance(self.game.players[id], bot.GameBot):
                options = [discord.SelectOption(
                    label=subclass.name,
                    description=subclass.description,
                    emoji=subclass.icon,
                    value=key,
                    default=key in self.game.players[id].powers.keys()
                ) for key, subclass in self.power_classes.items()]
                self.select = discord.ui.Select(options=options, max_values=2, placeholder=f"Pouvoir de {self.game.players[id].name}")
                self.select.callback = lambda interaction: self.update_bot_power(interaction, id)
                self.add_item(self.select)

    async def update_bot_power(self, interaction, id):
        self.game.players[id].set_powers([self.power_classes[x] for x in self.select.values])
        self.update()
        await interaction.response.edit_message(view=self)

class FightView(PanelView, PlayView):
    update_on_init = True

    def update(self):
        self.children[7].disabled = not any(power.data.active for power in self.game.current_player.powers.values())

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
        
        success = await self.game.handle_direction(direction, interaction)

        if not success:
            await interaction.response.send_message("Ce mouvement ne cause aucun changement du plateau.", ephemeral=True)

    @discord.ui.button(emoji="💀", style=discord.ButtonStyle.red)
    async def forfeit(self, button, interaction):
        await self.game.players[interaction.user.id].forfeit(interaction)

    @discord.ui.button(emoji="🦸", style=discord.ButtonStyle.green, row=1)
    async def use_ability(self, button, interaction):
        if interaction.user != self.game.current_player.user:
            return await interaction.response.defer()
        
        await self.game.current_player.use_power(interaction)


class PowerActivationView(PanelView):
    def __init__(self, game, panel, *args, **kwargs):
        super().__init__(game, panel, *args, **kwargs) 
        options = []
        for key, power in self.panel.powers.items():
            options.append(discord.SelectOption(emoji=power.icon, label=power.name, description=power.description, value=key))

        self.select = discord.ui.Select(placeholder="Choisissez le pouvoir à activer", options=options)
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction):
        await self.panel.resolve_power(self.select.values[0], interaction)
