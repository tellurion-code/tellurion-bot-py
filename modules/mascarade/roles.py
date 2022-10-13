import discord
import random
import modules.mascarade.globals as global_values

from modules.mascarade.utils import display_money


class Role:
    icon = "❌"
    name = "Invalide"
    description = "Ce rôle ne devrait pas être visible"
    number = 1
    action_name = ""

    def __init__(self, game):
        self.game = game
        self.player = None  # Dernier joueur à avoir utilisé la capacité

    @classmethod
    def restriction(cls, game):
        # Détermine si ce rôle peut être utilisé ou non
        return True

    async def use_power(self, player):
        self.player = player
        await self.power()

    async def power(self):
        # Fonction utilisée pour le pouvoir de ce rôle
        self.game.stack.append("⚠ Pouvoir pas encore implémenté")
        await self.end_turn()

    async def end_turn(self, extra=""):
        await self.game.next_turn({
            "name": f"{self.icon} {self.action_name}",
            "value": extra + '\n'.join(self.game.stack)
        })

    def __str__(self):
        return f"{self.icon} {self.name}"


class Judge(Role):
    icon = "⚖"
    name = "Juge"
    description = f"Gagnez les {display_money(1)} du Tribunal"
    action_name = "Taxes"

    async def power(self):
        self.player.gain_coins(self.game.tribunal, " du Tribunal")
        self.game.tribunal = 0
        await self.end_turn()


class Empress(Role):
    icon = "👑"
    name = "Impératrice"
    description = f"Gagnez {display_money(3)}"
    action_name = "Taxes"

    async def power(self):
        self.player.gain_coins(3)
        await self.end_turn()


class Patron(Role):
    icon = "💎"
    name = "Mécène"
    description = f"Gagnez {display_money(3)} puis vos deux voisins gagnent {display_money(1)}"
    action_name = "Mécénat"

    async def power(self):
        self.player.gain_coins(3)

        previous, next = self.game.get_neighbours(self.player)
        previous.gain_coins(1)
        next.gain_coins(1)

        await self.end_turn()

class Princess(Role):
    icon = "💍"
    name = "Princesse"
    description = f"Gagnez {display_money(2)} puis forcez un joueur à montrer son rôle sans le voir"
    action_name = "Divulgation"

    @classmethod
    def restriction(cls, game):
        return len(game.players.keys()) >= 6

    async def power(self):
        self.player.gain_coins(2)
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va choisir un joueur à divulguer"
            },
            view=views.PlayerSelectView(
                self.game,
                self.divulgate,
                player=self.player,
                condition=lambda e: e.user.id != self.player.user.id
            )
        )

    async def divulgate(self, selection, interaction):
        await interaction.response.defer()
        self.game.stack.append(f"Le rôle de `{selection[0].user}` a été révélé aux autres joueurs")

        view = views.ConfirmView(
            self.game,
            (x.user.id for x in self.game.players if x.user.id != selection[0].user.id),
            self.end
        )

        async def new_confirm(self, button, interaction):
            await self.check_if_all_confirmed(interaction)
            await interaction.response.send_message(
                content=f"Le rôle de `{selection[0]}` est `{selection[0].role}`",
                ephemeral=True
            )

        view.confirm = new_confirm
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` a divulgué le rôle de `{selection[0].user}`. Confirmez pour voir le rôle"
            },
            view=view
        )

    async def end(self):
        await self.end_turn()


class King(Role):
    icon = "⚜"
    name = "Roi"
    description = f"Gagnez {display_money(2)}"
    action_name = "Taxes"

    async def power(self):
        self.player.gain_coins(2)
        await self.end_turn()


class Thief(Role):
    icon = "🧤"
    name = "Voleur"
    description = f"Prenez {display_money(1)} à vos deux voisins"
    action_name = "Vol"

    async def power(self):
        previous, next = self.game.get_neighbours(interaction, self.player)
        self.player.steal_coins(1, previous)
        self.player.steal_coins(1, next)
        await self.next_turn()


class Crook(Role):
    icon = "🤞"
    name = "Escroc"
    description = f"Prenez {display_money(1)} au joueur qui en a le plus"
    action_name = "Vol"

    async def power(self):
        most_coins = max(player.coins for player in self.game.players.values())
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va choisir un joueur à voler"
            },
            view=views.PlayerSelectView(
                self.game,
                self.steal,
                player=self.player,
                condition=lambda e: e.coins == most_coins
            )
        )

    async def steal(self, selection, interaction):
        await interaction.response.defer()
        self.player.steal_coins(2, selection[0])
        await self.end_turn()


class Beggar(Role):
    icon = "🪔"
    name = "Mendiant"
    description = f"Prenez dans le sens horaire {display_money(1)} à chaque joueur avec plus de {display_money(1)} que vous"
    action_name = "Mendicité"

    async def power(self):
        origin = self.game.order.index(self.player.user.id)
        index = (origin + 1) % len(self.order)
        while index != origin:
            other = self.game.players[self.game.order[index]]
            if other.coins > player.coins:
                self.player.steal_coins(1, other)
            else:
                self.game.stack.append(f"`{other.user}` avait moins de pièces que `{self.player.user}`")

            index = (index + 1) % len(self.order)

        await self.end_turn()


class Fool(Role):
    icon = "🎉"
    name = "Fou"
    description = f"Gagnez {display_money(1)}, puis échangez (ou pas) deux cartes autres que la vôtre"
    action_name = "Echange"

    async def power(self):
        self.player.gain_coins(1)
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va choisir deux joueurs avec lesquels échanger"
            },
            view=views.PlayerSelectView(
                self.game,
                self.do_exchange,
                min_values=2,
                max_values=2,
                player=self.player,
                condition=lambda e: e.user.id != self.player.user.id
            )
        )

    async def do_exchange(self, selection, interaction):
        await interaction.response.defer()

        self.game.stack.append(f"`{self.player.user}` a échangé (ou pas) les cartes de `{selection[0].user}` et `{selection[1].user}`")
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va échanger (ou pas) les cartes de `{selection[0].user}` et `{selection[1].user}`"
            },
            view=views.ExchangeView(self.player, selection[0], selection[1], self.end)
        )

    async def end(self):
        await self.end_turn()


class Witch(Role):
    icon = "⚗️"
    name = "Sorcière"
    description = "Echangez votre fortune avec un autre joueur"
    action_name = "Echange"

    async def power(self):
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va choisir un joueur avec qui échanger sa fortume"
            },
            view=views.PlayerSelectView(
                self.game,
                self.exchange_coins,
                player=self.player,
                condition=lambda e: e.user.id != self.player.user.id
            )
        )

    async def exchange_coins(self, selection, interaction):
        selection[0].coins, self.player.coins = self.player.coins, selection[0].coins
        self.game.stack.append(f"`{self.player.user}` a échangé sa fortune avec `{selection[0].user}`")
        await self.end_turn()


class Peasant(Role):
    icon = "🌾"
    name = "Paysan"
    description = f"Gagnez {display_money(1)}. Si le deuxième Paysan conteste, gagnez chacun {display_money(2)}"
    action_name = "Récolte"
    number = 2
    first_peasant_trigger = False

    @classmethod
    def restriction(cls, game):
        return len(game.players.keys()) >= 8

    async def power(self):
        if sum([1 for x in self.game.contestors if self.game.players[x].role.name == self.name]) == 2:
            self.player.gain_coins(2, " grâce au second Paysan")

            self.first_peasant_trigger = not self.first_peasant_trigger
            if not self.first_peasant_trigger:
                await self.end_turn()
        else:
            self.player.gain_coins(1)
            await self.end_turn()


class Cheat(Role):
    icon = "🃏"
    name = "Tricheur"
    description = f"Si vous avez {display_money(10)} ou plus, vous gagnez la partie"
    action_name = "Triche"

    async def power(self):
        if self.player.coins >= 10:
            await self.game.end_game(str(self.player.user))
        else:
            self.game.stack.append(f"`{self.player.user}` n'avait pas assez de :coin:")
            await self.end_turn()


class Spy(Role):
    icon = "🎭"
    name = "Espionne"
    description = "Regardez votre rôle et celui d'un autre joueur, puis échangez les (ou pas)"
    action_name = "Echange"

    async def power(self):
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va choisir un joueur avec qui échanger"
            },
            view=views.PlayerSelectView(
                self.game,
                self.reveal_and_exchange,
                player=self.player,
                condition=lambda e: e.user.id != self.player.user.id
            )
        )

    async def reveal_and_exchange(self, selection, interaction):
        await interaction.response.send_message(
            content=f"Votre rôle est {self.player.role} et celui de votre cible est {selection[0].role}",
            ephemeral=True
        )

        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va échanger (ou pas) avec `{selection[0].user}`"
            },
            view=views.ExchangeView(self.player, self.player, selection[0], self.end)
        )

    async def end(self):
        await self.end_turn()


class Widow(Role):
    icon = "⚰"
    name = "Veuve"
    description = f"Gagnez des {display_money(1)} jusqu'à en avoir 10 ({display_money(10)})"
    action_name = "Héritage"

    async def power(self):
        if self.player.coins < 10:
            diff = 10 - self.player.coins
            self.player.gain_coins(diff)
        else:
            stack.append(f"{self.player.user} avait déjà {display_money(10)} ou plus")

        await self.end_turn()


class Guru(Role):
    icon = "📿"
    name = "Gourou"
    description = f"Forcez un joueur à annoncer et révéler son rôle. S'il a tort, prenez lui {display_money(4)}"
    action_name = "Inquisition"
    target = None

    @classmethod
    def restriction(cls, game):
        return len(game.players.keys()) >= 8

    async def power(self):
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va choisir qui va devoir annoncer son rôle"
            },
            view=views.PlayerSelectView(
                self.game,
                self.ask_for_role,
                player=self.player,
                condition=lambda e: e.user.id != self.player.user.id
            )
        )

    async def ask_for_role(self, selection, interaction):
        self.target = selection[0]
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` a demandé à `{self.target.user}` d'annoncer son rôle"
            },
            view=views.RoleSelectView(
                self.game,
                self.check_if_correct,
                player=self.target
            )
        )

    async def check_if_correct(self, selection, interaction):
        correct = selection[0].role.name == self.target.role.name
        self.target.revealed = True
        stack.append(f"`{self.target.user}` a annoncé {selection[0]} et avait {'raison' if correct else 'tort'}")
        if not correct:
            self.player.steal_coins(4, self.target)

        await self.end_turn()

class Puppeteer(Role):
    icon = "♟"
    name = "Marionnettiste"
    description = f"Prenez {display_money(1)} à deux autre joueurs qui échangent de place, rôle, et fortune"
    action_name = "Manipulation"

    @classmethod
    def restriction(cls, game):
        return len(game.players.keys()) >= 8

    async def power(self, player):
        await self.game.send_info(
            info={
                "name": f"{self.icon} {self.action_name}",
                "value": f"`{self.player.user}` va choisir deux joueurs à échanger"
            },
            view=views.PlayerSelectView(
                self.game,
                self.manipulate,
                min_values=2,
                max_values=2,
                player=self.player,
                condition=lambda e: e.user.id != self.player.user.id
            )
        )

    async def manipulate(self, selection, interaction):
        await interaction.response.defer()
        target, target2 = selection

        self.player.steal_coins(1, target)
        self.player.steal_coins(1, target2)

        target.role, target2.role = target2.role, target.role
        target.coins, target2.coins = target2.coins, target.coins

        index = self.game.order.index(target.user.id)
        index2 = self.game.order.index(target2.user.id)
        self.game.order.remove(target.user.id)
        self.game.order.insert(index2, target.user.id)
        self.game.order.remove(target2.user.id)
        self.game.order.insert(index, target2.user.id)

        await self.end_turn()


class Gambler(Role):
    icon = "🎲"
    name = "Joueur"
    description = f"Prenez 1-3 {display_money(1)} et désignez un joueur. S'il devine le nombre, il les gagne, sinon vous les gagnez"
    action_name = "Pari"
