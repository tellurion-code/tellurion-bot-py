import discord
import traceback

from modules.avalon.player import Player
from modules.avalon.components import TeamSelect, ConfirmButton, VoteButton, QuestButton, AssassinSelect

import modules.avalon.globals as global_values


class GameView(discord.ui.View):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.timeout = None

    async def clear(self):
        self.clear_items()
        await self.message.edit(view=self)
        self.stop()

    async def freeze(self):
        self.disable_all_items()
        await self.message.edit(view=self)
        self.stop()

    async def delete(self):
        await self.message.delete()
        self.stop()

    async def on_check_failure(self, interaction):
        await interaction.response.defer()

    async def on_error(self, error, item, interaction):
        embed = discord.Embed(
            title="[Erreur] Aïe :/",
            description="```python\n{0}```".format(traceback.format_exc())
        )

        # Send message to dev channels
        await self.game.mainclass.client.get_channel(456142390726623243).send(embed=embed.set_footer(text="Ce message ne s'autodétruira pas.",))


class JoinView(GameView):
    @discord.ui.button(label="Rejoindre ou quiter", style=discord.ButtonStyle.blurple)
    async def join_or_leave(self, button, interaction):
        if interaction.user.id not in self.game.players:
            self.game.players[interaction.user.id] = Player(self, interaction.user)
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

        if len(self.game.players) < 5:
            return {
                "bool": False,
                "reason": "Pas assez de joueurs"
            }

        if len(self.game.players) > 10:
            return {
                "bool": False,
                "reason": "Trop de joueurs"
            }

        if len(self.game.roles) and len(self.game.players) != len(self.game.roles):
            return {
                "bool": False,
                "reason": f"Nombre de joueurs différent du nombre de rôles ({str(len(self.game.roles))})"
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
        embed.title = "Partie d'Avalon | Joueurs (" + str(len(self.game.players)) + ") :"
        embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.game.players.values()])

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class PlayView(GameView):
    async def interaction_check(self, interaction):
        return interaction.user.id in self.game.players

class TeamView(PlayView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        valid_candidates = [self.game.players[x] for x in self.game.order]
        options = []
        for i, player in enumerate(valid_candidates):
            options.append(discord.SelectOption(
                label=str(player.user),
                value=str(player.user.id),
                emoji=player.index_emoji
            ))

        self.add_item(TeamSelect(
            min_values=self.game.quests[self.game.round],
            max_values=self.game.quests[self.game.round],
            options=options
        ))

        self.add_item(ConfirmButton())

    async def update_selection(self, select, interaction):
        if interaction.user.id != self.game.order[self.game.turn]:
            await interaction.response.defer()
            return

        self.game.team = [int(x) for x in select.values]
        for option in select.options:
            option.default = option.value in select.values

        confirm_button = self.children[1]
        if len(self.game.team) == self.game.quests[self.game.round]:
            confirm_button.disabled = False
            confirm_button.label = "Confirmer l'équipe"
            confirm_button.style = discord.ButtonStyle.green
        else:
            confirm_button.disabled = True
            confirm_button.label = "Nombre de membres invalide"
            confirm_button.style = discord.ButtonStyle.gray

        await interaction.response.edit_message(
            embed=self.game.get_info_embed(),
            view=self
        )

    async def confirm_team(self, button, interaction):
        await interaction.response.defer()

        if len(self.game.team) == self.game.quests[self.game.round] and interaction.user.id == self.game.order[self.game.turn]:
            await self.game.send_players_vote_choice()


class VoteView(PlayView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [x for x in global_values.vote_choices["names"].keys()]
        for choice in choices:
            self.add_item(VoteButton(
                choice,
                label=global_values.vote_choices["names"][choice],
                style=global_values.vote_choices["styles"][choice]
            ))

    async def cast_vote(self, button, interaction, vote):
        self.game.players[interaction.user.id].last_vote = vote

        await interaction.response.send_message(
            content=f"Vous avez voté {global_values.vote_choices['emojis'][vote]} {global_values.vote_choices['names'][vote]}",
            ephemeral=True
        )
        await self.message.edit(embed=self.game.get_info_embed())
        await self.game.check_vote_end()

class QuestView(PlayView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = []
        for id in self.game.team:
            for choice in self.game.players[id].quest_choices:
                if choice not in choices:
                    choices.append(choice)

        for choice in choices:
            self.add_item(QuestButton(
                choice,
                label=global_values.quest_choices["names"][choice],
                emoji=global_values.quest_choices["emojis"][choice],
                style=global_values.quest_choices["styles"][choice]
            ))

    async def cast_choice(self, button, interaction, choice):
        if interaction.user.id not in self.game.team:
            await interaction.response.defer()
            return

        self.game.players[interaction.user.id].last_choice = choice

        await interaction.response.send_message(
            content=f"Vous avez choisi {global_values.quest_choices['emojis'][choice]} {global_values.quest_choices['names'][choice]}",
            ephemeral=True
        )
        await self.game.check_quest_end()


class AssassinView(PlayView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        valid_candidates = [x for x in self.game.players.values() if x.allegiance != "evil"]
        options = []
        for i, player in enumerate(valid_candidates):
            options.append(discord.SelectOption(
                label=str(player.user),
                value=str(player.user.id),
                emoji=player.index_emoji
            ))

        self.add_item(AssassinSelect(
            min_values=1,
            max_values=1,
            options=options
        ))

    async def interaction_check(self, interaction):
        return self.game.players[interaction.user.id].role == "assassin"

    async def kill(self, select, interaction):
        killed = self.game.players[int(select.values[0])]

        if killed.role == "merlin":
            await self.game.end_game(False, "assassinat de Merlin (`" + str(killed.user) + "`)")
        elif killed.role == "elias":
            await self.game.end_game(global_values.visual_roles[killed.role], "usurpation (`" + str(killed.user) + "`)")
        else:
            await self.game.end_game(True, "3 Quêtes réussies (Assassinat de `" + str(killed.user) + "` qui était " + global_values.visual_roles[killed.role] + ")")

        await interaction.response.defer()
        await self.delete()
