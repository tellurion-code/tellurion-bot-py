"""Player class."""

from modules.mascarade.utils import display_money

import modules.mascarade.globals as global_values
import modules.mascarade.views as views


class Player:
    def __init__(self, game, user):
        self.game = game
        self.user = user
        self.role = None
        self.index_emoji = ""
        self.last_vote = None
        self.coins = 6
        self.revealed = False
        self.target = None

    @property
    def must_exchange(self):
        return self.revealed or self.game.round < 4

    def __str__(self):
        return f"{self.index_emoji} `{self.user}`"

    async def send_role_info(self, interaction):
        await interaction.response.send_message(
            content=f"Votre rôle est {self.role}",
            ephemeral=True
        )

    def gain_coins(self, amount, extra=""):
        self.game.stack.append(f"{self} a gagné {display_money(amount)}{extra}")
        self.coins += amount

    def steal_coins(self, amount, player, extra=""):
        total = min(player.coins, amount)
        self.game.stack.append(f"{self} a volé {display_money(total)} à {player}{extra}")
        self.coins += total
        player.coins -= total

    async def start_exchange(self, interaction):
        await interaction.response.defer()
        await self.game.send_info(
            info={
                "name": "🔄 Echange",
                "value": f"{self} va choisir un joueur avec qui échanger"
            },
            view=views.PlayerSelectView(self.game, self.do_exchange, condition=lambda e: e.user.id != self.user.id)
        )

    async def do_exchange(self, selection, interaction):
        await interaction.response.defer()
        self.target = selection[0]
        await self.game.send_info(
            info={
                "name": "🔄 Echange",
                "value": f"{self} va échanger (ou pas) avec {self.target}"
            },
            view=views.ExchangeView(self, self, self.target, self.end_exchange)
        )

    async def end_exchange(self):
        await self.game.next_turn({
            "name": "🔄 Echange",
            "value": f"{self} a échangé (ou pas) avec {self.target}"
        })

    async def claim_role(self, interaction):
        await interaction.response.defer()
        await self.game.send_info(
            info={
                "name": "❗ Annonce",
                "value": f"{self} va annoncer un rôle"
            },
            view=views.RoleSelectView(self.game, self.start_contest)
        )

    async def start_contest(self, selection, interaction):
        await interaction.response.defer()
        role = selection[0]
        self.last_vote = False
        await self.game.send_info(
            info={
                "name": f"{role.icon} Annonce",
                "value": f"{self} a annoncé que son rôle est {role}"
            },
            view=views.ContestView(self, role)
        )
