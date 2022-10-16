"""Views."""

import discord
import random

from modules.game.views import GameView, PlayView
from modules.mascarade.components import GeneralSelect, ConfirmButton

import modules.mascarade.roles as roles
import modules.mascarade.globals as global_values
import modules.mascarade.player as player_class


classes = {c.__name__.lower(): c for c in roles.Role.__subclasses__()}

# pylint: disable=unused-argument
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
            await self.game.pick_roles()
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

        if len(self.game.players) > 12:
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
        embed.title = "Partie de Mascarade | Joueurs (" + str(len(self.game.players)) + ") :"
        embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.game.players.values()])

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class RoleView(PlayView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.valid_roles = {k: x(self.game) for k, x in classes.items() if x.restriction(self.game) or global_values.debug}
        options = []
        for key, role in self.valid_roles.items():
            options.append(discord.SelectOption(
                label=role.name,
                value=key,
                emoji=role.icon,
                description=role.description
            ))

        self.add_item(GeneralSelect(
            "rôle",
            min_values=1,
            max_values=len(self.valid_roles),
            options=options
        ))

        condition = self.enough_roles()
        self.add_item(ConfirmButton(condition["bool"], condition["reason"]))

    def enough_roles(self):
        if global_values.debug:
            return {
                "bool": True,
                "reason": "Confirmer les rôles"
            }

        if self.game.role_count < len(self.game.players):
            return {
                "bool": False,
                "reason": "Pas assez de rôles"
            }

        if "judge" not in self.game.roles:
            return {
                "bool": False,
                "reason": "Le Juge doit être en jeu"
            }

        return {
            "bool": True,
            "reason": "Confirmer les rôles"
        }

    async def update_selection(self, select, interaction):
        self.game.roles = {k: self.valid_roles[k] for k in select.values}
        for option in select.options:
            option.default = option.value in select.values

        condition = self.enough_roles()
        self.children[1].update(condition["bool"], condition["reason"])

        await interaction.response.edit_message(view=self)

    async def confirm(self, button, interaction):
        await interaction.response.defer()

        await self.game.start_game()
        await self.delete()


class ConfirmView(PlayView):
    def __init__(self, game, to_confirm, next, next_args=None, *args, **kwargs):
        self.temporary = kwargs.pop("temporary") if "temporary" in kwargs else False

        super().__init__(game, *args, **kwargs)
        self.unconfirmed = [*to_confirm]  # Liste d'id de joueurs qui doivent confirmer
        self.next = next  # Fonction async appelée une fois que tout le monde a confirmé
        self.next_args = next_args or []

    async def interaction_check(self, interaction):
        return interaction.user.id in self.unconfirmed

    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.blurple)
    async def confirm(self, button, interaction):
        await self.check_if_all_confirmed(interaction)
        await self.respond(interaction)

    async def respond(self, interaction):
        await interaction.response.send_message(
            content="Vous avez confirmé",
            ephemeral=True
        )

    async def check_if_all_confirmed(self, interaction):
        if interaction.user.id in self.unconfirmed:
            self.unconfirmed.remove(interaction.user.id)
            if len(self.unconfirmed) == 0:
                await self.next(*self.next_args)

                if self.temporary:
                    await self.delete()
                else:
                    self.stop()


class TurnView(PlayView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        look_button = discord.ui.Button(label="Regarder", style=discord.ButtonStyle.gray, disabled=self.game.current_player.must_exchange)
        look_button.callback = self.look_at_role
        self.add_item(look_button)

        exchange_button = discord.ui.Button(label="Echanger", style=discord.ButtonStyle.gray)
        exchange_button.callback = self.exchange
        self.add_item(exchange_button)

        claim_button = discord.ui.Button(label="Annoncer", style=discord.ButtonStyle.gray, disabled=self.game.current_player.must_exchange)
        claim_button.callback = self.claim
        self.add_item(claim_button)

    async def interaction_check(self, interaction):
        return interaction.user.id == self.game.order[self.game.turn]

    def end(self):
        for player in self.game.players.values():
            player.revealed = False
            player.last_vote = None
            player.last_vote_emoji = "✉"

        for holder in self.game.center:
            holder.revealed = False

        self.stop()

    async def look_at_role(self, interaction):
        self.end()
        await self.game.current_player.send_role_info(interaction)
        await self.game.next_turn({
            "name": "👁 Consultation",
            "value": f"{self.game.current_player} a regardé son rôle"
        })

    async def exchange(self, interaction):
        self.end()
        self.game.phase = "exchange"
        await self.game.current_player.start_exchange(interaction)

    async def claim(self, interaction):
        self.end()
        self.game.phase = "contest"
        await self.game.current_player.claim_role(interaction)


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

    async def interaction_check(self, interaction):
        return interaction.user.id == self.player.user.id

    async def update_selection(self, select, interaction):
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
        include_center = kwargs.pop("include_center") if "include_center" in kwargs else False

        self.valid_players = [x for x in game.players.values() if condition(x)]
        choices = {}
        for player in self.valid_players:
            choices[player.user.id] = {
                "value": player,
                "label": str(player.user),
                "emoji": player.index_emoji
            }

        if include_center:
            for i, holder in enumerate(game.center):
                choices[-i] = {
                    "value": holder,
                    "label": holder.name,
                    "emoji": holder.index_emoji
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


class ExchangeView(PlayView):
    def __init__(self, player, first, second, next, *args, **kwargs):
        super().__init__(player.game, *args, **kwargs)
        self.player = player
        self.first = first
        self.second = second
        self.next = next

    async def interaction_check(self, interaction):
        return interaction.user.id == self.player.user.id

    async def end(self):
        await self.next()
        self.stop()

    @discord.ui.button(label="Echanger", style=discord.ButtonStyle.green)
    async def exchange(self, button, interaction):
        self.first.role, self.second.role = self.second.role, self.first.role
        await interaction.response.send_message(
            content="Vous avez échangé de rôles",
            ephemeral=True
        )
        await self.end()

    @discord.ui.button(label="Ne pas échanger", style=discord.ButtonStyle.red)
    async def dont_exchange(self, button, interaction):
        await interaction.response.send_message(
            content="Vous n'avez **pas** échangé de rôles",
            ephemeral=True
        )
        await self.end()

    @discord.ui.button(label="Au hasard", style=discord.ButtonStyle.blurple)
    async def random_exchange(self, button, interaction):
        await interaction.response.send_message(
            content="Vous avez échangé au hasard. Oups!",
            ephemeral=True
        )

        if random.random() < 0.5:
            self.first.role, self.second.role = self.second.role, self.first.role

        await self.end()


class ContestView(PlayView):
    def __init__(self, player, role, *args, **kwargs):
        super().__init__(player.game, *args, **kwargs)
        self.player = player
        self.role = role

    async def interaction_check(self, interaction):
        return await super().interaction_check(interaction) and interaction.user.id != self.player.user.id

    async def cast_vote(self, contesting, interaction):
        self.game.players[interaction.user.id].last_vote = contesting

        await interaction.response.send_message(
            content=f"Vous avez décider de {'contester' if contesting else 'ne pas contester'}",
            ephemeral=True
        )
        await self.message.edit(embed=self.game.get_info_embed())

        done = await self.game.check_vote_end(self.role)
        if done:
            self.stop()

    @discord.ui.button(label="Contester", style=discord.ButtonStyle.blurple)
    async def contest(self, button, interaction):
        await self.cast_vote(True, interaction)

    @discord.ui.button(label="Ne pas contester", style=discord.ButtonStyle.blurple)
    async def dont_contest(self, button, interaction):
        await self.cast_vote(False, interaction)
