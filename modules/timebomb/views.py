"""Views."""

import discord

from modules.game.views import GameView, PlayView
from modules.timebomb.components import GeneralSelect

import modules.timebomb.globals as global_values
import modules.timebomb.player as player_class


class JoinView(GameView):
    @discord.ui.button(label="Rejoindre ou quitter", style=discord.ButtonStyle.blurple)
    async def join_or_leave(self, button, interaction):
        if interaction.user.id not in self.game.players:
            self.game.players[interaction.user.id] = player_class.Player(self.game, interaction.user)
        else:
            del self.game.players[interaction.user.id]

        await self.update_join_message(interaction)

    @discord.ui.button(label="Pas assez de joueurs", disabled=True, style=discord.ButtonStyle.gray)
    async def start(self, button, interaction):
        await interaction.response.defer()

        if interaction.user.id in self.game.players:
            await self.game.start_game()
            await self.delete()

    def enough_players(self):
        if global_values.debug:
            return {
                "bool": True,
                "reason": "Démarrer"
            }

        if len(self.game.players) < 4:
            return {
                "bool": False,
                "reason": "Pas assez de joueurs"
            }

        if len(self.game.players) > 8:
            return {
                "bool": False,
                "reason": "Trop de joueurs"
            }

        return {
            "bool": True,
            "reason": "Démarrer"
        }

    async def update_join_message(self, interaction):
        condition = self.enough_players()

        self.children[1].style = discord.ButtonStyle.green if condition["bool"] else discord.ButtonStyle.gray
        self.children[1].label = condition["reason"]
        self.children[1].disabled = not condition["bool"]

        embed = self.message.embeds[0]
        embed.title = "Partie de Timebomb | Joueurs (" + str(len(self.game.players)) + ") :"
        embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.game.players.values()])

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

class GeneralSelectView(PlayView):
    def __init__(self, game, choices, name, next, *args, **kwargs):
        self.player = kwargs.pop("player") if "player" in kwargs else None
        min_values = kwargs.pop("min_values") if "min_values" in kwargs else 1
        max_values = kwargs.pop("max_values") if "max_values" in kwargs else 1

        super().__init__(game, *args, **kwargs)

        self.player = self.player or self.game.current_player
        self.next = next  # Fonction async appelée une fois le choix fait

        self.choices = {str(key): value for key, value in choices.items()}
        options = []
        for key, choice in self.choices.items():
            options.append(discord.SelectOption(
                label=choice["label"],
                value=key,
                emoji=choice["emoji"]
            ))

        self.add_item(GeneralSelect(
            name,
            min_values=min_values,
            max_values=max_values,
            options=options
        ))

        # self.add_item(ConfirmButton("Nombre de joueurs invalide"))

    async def update_selection(self, select, interaction):
        if interaction.user.id != self.player.user.id:
            await interaction.response.defer()
            return
        
        self.selection = [self.choices[x]["value"] for x in select.values]
        # for option in select.options:
        #     option.default = option.value in select.values
        #
        # self.children[1].update(True, "Confirmer")
        # await interaction.response.edit_message(view=self)
        await self.next(self.selection, interaction)
        self.stop()


class PlayerSelectView(GeneralSelectView):
    def __init__(self, game, next, *args, **kwargs):
        condition = kwargs.pop("condition") if "condition" in kwargs else lambda e: True

        self.valid_players = [x for x in game.players.values() if condition(x)]
        choices = {}
        for player in self.valid_players:
            choices[player.user.id] = {
                "value": player,
                "label": str(player.user),
                "emoji": player.index_emoji
            }
            
        super().__init__(game, choices, "joueur", next, *args, **kwargs)
        

class RoleSelectView(GeneralSelectView):
    def __init__(self, game, next, *args, **kwargs):
        condition = kwargs.pop("condition") if "condition" in kwargs else lambda e: True
        self.valid_roles = {k: x for k, x in game.roles.items() if condition(x)}
        choices = {}
        for key, role in self.valid_roles.items():
            choices[key] = {
                "value": role,
                "label": role.name,
                "emoji": role.icon
            }

        super().__init__(game, choices, "rôle", next, *args, **kwargs)


class WireCuttingView(PlayView):
    def __init__(self, player, next, *args, **kwargs):
        super().__init__(player.game, *args, **kwargs)
        self.next = next

        for i, wire in enumerate(player.wires):
            wire_button = discord.ui.Button(emoji=str(wire), custom_id=str(i), style=discord.ButtonStyle.gray)
            wire_button.callback = self.choose_wire

            self.add_item(wire_button)

    async def choose_wire(self, interaction):
        index = int(interaction.data["custom_id"])
        await self.next(index, interaction)
