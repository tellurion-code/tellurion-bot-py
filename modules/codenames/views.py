import discord

from modules.codenames.player import Player
import modules.codenames.globals as global_values


class GameView(discord.ui.View):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game

    async def freeze(self):
        self.disable_all_items()
        await self.message.edit(view=self)
        self.stop()

    async def delete(self):
        await self.message.delete()
        self.stop()

    async def on_check_failure(self, interaction):
        await interaction.response.defer()


class JoinView(GameView):
    @discord.ui.button(label="Rejoindre ou quiter", style=discord.ButtonStyle.blurple)
    async def join_or_leave(self, button, interaction):
        if interaction.user.id not in self.game.players:
            self.game.players[interaction.user.id] = Player(interaction.user)
        else:
            del self.game.players[interaction.user.id]

        await self.update_join_message(interaction)

    @discord.ui.button(label="Pas assez de joueurs", disabled=True, style=discord.ButtonStyle.gray)
    async def start(self, button, interaction):
        await interaction.response.defer()

        if interaction.user.id in self.game.players:
            await self.game.choose_teams()
            await self.delete()

    async def update_join_message(self, interaction):
        self.children[1].style = discord.ButtonStyle.green if (len(self.game.players) >= 4 or global_values.debug) else discord.ButtonStyle.gray
        self.children[1].label = "Démarrer" if (len(self.game.players) >= 4 or global_values.debug) else "Pas assez de joueurs"
        self.children[1].disabled = False if (len(self.game.players) >= 4 or global_values.debug) else True

        embed = self.message.embeds[0]
        embed.title = "Partie de Codenames | Joueurs (" + str(len(self.game.players)) + ") :"
        embed.description = '\n'.join(["`" + str(x.user) + "`" for x in self.game.players.values()])

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class TeamView(GameView):
    async def interaction_check(self, interaction):
        return interaction.user.id in self.game.players

    @discord.ui.button(label="Rejoindre l'équipe bleue", style=discord.ButtonStyle.blurple)
    async def join_blue_team(self, button, interaction):
        self.game.players[interaction.user.id].team = 0
        await self.update_team_message(interaction)

    @discord.ui.button(label="Rejoindre l'équipe rouge", style=discord.ButtonStyle.red)
    async def join_red_team(self, button, interaction):
        self.game.players[interaction.user.id].team = 1
        await self.update_team_message(interaction)

    @discord.ui.button(label="Joueurs sans équipe restants", style=discord.ButtonStyle.gray, disabled=True, row=1)
    async def confirm_teams(self, button, interaction):
        await interaction.response.defer()

        if self.balanced_teams() and not self.missing_players():
            await self.game.choose_spymasters()
            await self.delete()

    def balanced_teams(self):
        return abs(sum([2 * x.team - 1 for x in self.game.players.values()])) <= 1

    def missing_players(self):
        return sum([1 for x in self.game.players.values() if x.team == -1])

    async def update_team_message(self, interaction):
        style = discord.ButtonStyle.gray
        label = "Continuer"
        disabled = True

        if self.missing_players():
            label = "Joueurs sans équipe restants"
        elif not self.balanced_teams():
            label = "Equipes déséquilibrées"
        else:
            style = discord.ButtonStyle.green
            disabled = False

        self.children[2].style = style
        self.children[2].label = label
        self.children[2].disabled = disabled

        embed = self.message.embeds[0]
        for i in range(2):
            members = ["`" + str(x.user) + "`" for x in self.game.players.values() if x.team == i]

            embed.set_field_at(
                i,
                name=embed.fields[i].name,
                value='\n'.join(members) if len(members) else "Personne"
            )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class SpymasterView(GameView):
    async def interaction_check(self, interaction):
        return interaction.user.id in self.game.players

    @discord.ui.button(label="Devenir Spymaster bleu", style=discord.ButtonStyle.blurple)
    async def become_blue_spymaster(self, button, interaction):
        await self.become_spymaster(interaction, 0)

    @discord.ui.button(label="Devenir Spymaster rouge", style=discord.ButtonStyle.red)
    async def become_red_spymaster(self, button, interaction):
        await self.become_spymaster(interaction, 1)

    async def become_spymaster(self, interaction, index):
        if self.game.players[interaction.user.id].team == index:
            self.game.spy_masters[index] = interaction.user.id
            await self.update_spymaster_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Spymasters manquants", style=discord.ButtonStyle.gray, disabled=True, row=1)
    async def confirm_spymasters(self, button, interaction):
        await interaction.response.defer()
        if not self.missing_spymasters():
            self.game.turn = 0
            await self.game.send_game_messages()
            await self.delete()

    def missing_spymasters(self):
        return len([0 for x in self.game.spy_masters if x == 0])

    async def update_spymaster_message(self, interaction):
        style = discord.ButtonStyle.gray
        label = "Continuer"
        disabled = True

        if self.missing_spymasters():
            label = "Spymaster manquant"
        else:
            style = discord.ButtonStyle.green
            disabled = False

        self.children[2].style = style
        self.children[2].label = label
        self.children[2].disabled = disabled

        embed = self.message.embeds[0]
        for i in range(2):
            embed.set_field_at(
                i,
                name=embed.fields[i].name,
                value="`" + str(self.game.players[self.game.spy_masters[i]].user) + "`" if self.game.spy_masters[i] else "Personne"
            )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class BoardView(GameView):
    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)

        for y in range(5):
            for x in range(5):
                word = self.game.board[5 * y + x]
                self.add_item(WordButton(word, row=y))

    async def interaction_check(self, interaction):
        return interaction.user.id == self.game.spy_masters[self.game.turn]

    async def reveal_word(self, button, interaction):
        button.word.revealed = button.disabled = True
        button.update_style(True)

        if button.word.color != self.game.turn:
            self.game.turn = 1 - self.game.turn

        if button.word.color == 3:
            await self.game.end_game()
        else:
            await self.game.check_if_win()

        await self.game.send_info(interaction)

    def reveal_all_words(self):
        for button in self.children:
            button.update_style(True)


class ControlsView(GameView):
    async def interaction_check(self, interaction):
        return interaction.user.id in self.game.spy_masters

    @discord.ui.button(label="Voir les vraies couleurs", style=discord.ButtonStyle.gray)
    async def send_spymaster_info(self, button, interaction):
        view = discord.ui.View()
        for y in range(5):
            for x in range(5):
                word = self.game.board[5 * y + x]
                view.add_item(WordButton(word, row=y, spymaster=True))

        await interaction.response.send_message(content="Vraies couleurs des cartes", view=view, ephemeral=True)
        view.stop()

    @discord.ui.button(label="Passer le tour", style=discord.ButtonStyle.gray)
    async def pass_turn(self, button, interaction):
        if interaction.user.id == self.game.spy_masters[self.game.turn]:
            self.game.turn = 1 - self.game.turn
            await self.game.send_info(interaction)
        else:
            await interaction.response.defer()


class WordButton(discord.ui.Button):
    def __init__(self, word, **kwargs):
        spymaster = kwargs.pop("spymaster") if "spymaster" in kwargs else False
        revealed = word.revealed or spymaster

        super().__init__(**kwargs)

        self.word = word
        self.update_style(revealed)

    def update_style(self, revealed):
        self.label = word.word
        self.style = discord.ButtonStyle.gray if not revealed else global_values.button_styles[word.color]
        self.disabled = revealed

    async def callback(self, interaction):
        await self.view.reveal_word(self, interaction)
