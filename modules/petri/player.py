import discord
import random

from modules.reaction_message.reaction_message import ReactionMessage

import modules.petri.globals as global_values


class Player:
    name = "🚫 Sans-Pouvoir"
    description = "N'a pas de pouvoir spécial"
    index = -1
    power_active = False

    def __init__(self, user):
        self.user = user

    def spawn(self, game, map, x, y):
        map[y][x] = self.index

    def get_power(self, game, x, y, dx, dy):
        power = 0
        tdx, tdy = 0, 0
        while game.map[y + tdy][x + tdx] == self.index:
            power += 1
            tdx += dx
            tdy += dy
            if not game.inside(x + tdx, y + tdy):
                break

        return power

    def on_attack(self, diff):
        return 1

    def on_defense(self, diff):
        return 0

    def on_turn_end(self, game):
        pass

    def active_power(self, game):
        pass


class Defender(Player):
    name = "🛡️ Défenseur"
    description = "Ne perd pas d'unités lors d'une égalité en défense"

    def on_defense(self, diff):
        return (-1 if diff <= 0 else 0)


class Attacker(Player):
    name = "🗡️ Attaquant"
    description = "Capture l'unité au lieu de la détruire lors d'une égalité en attaque"

    def on_attack(self, diff):
        return (2 if diff >= 0 else 1)


class Architect(Player):
    name = "🧱 Architecte"
    description = "Les murs comptent comme des unités pour lui en défense"

    def get_power(self, game, x, y, dx, dy):
        power = 0
        tdx, tdy = 0, 0
        while game.map[y + tdy][x + tdx] == self.index or game.map[y + tdy][x + tdx] == -2 and self.index != game.turn:
            power += 1
            tdx += dx
            tdy += dy
            if not game.inside(x + tdx, y + tdy):
                break

        return power


class Swarm(Player):
    name = "🐝 Essaim"
    description = "Commence avec une unité en plus"

    def spawn(self, game, map, x, y):
        map[y][x] = self.index

        a = random.randrange(4)
        dx = [-1, 0, 1, 0][a]
        dy = [0, -1, 0, 1][a]

        if game.inside(x + dx, y + dy):
            map[y + dy][x + dx] = self.index
        else:
            map[y - dy][x - dx] = self.index


class Racer(Player):
    name = "🏎️ Coureur"
    description = "Peut prendre une fois dans la partie un second tour juste après le sien"
    power_active = True
    steal_turn = False

    def active_power(self, game):
        self.power_active = False
        self.steal_turn = True

        return {
            "name": "🏎️ Pouvoir du Coureur",
            "value": "Le prochain tour sera le vôtre"
        }

    def on_turn_end(self, game):
        if self.steal_turn:
            self.steal_turn = False
            game.turn = (self.index - 1)%len(game.players)

class Demolisher(Player):
    name = "🧨 Démolisseur"
    description = "Détruit tous les murs qu'il encercle à la fin de son tour (diagonales non nécessaires)"

    def on_turn_end(self, game):
        amount = 0

        def check_circling(x, y):
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if game.map[y + dy][x + dx] != self.index and dx != dy:
                        return False
            return True

        for y in range(game.ranges[1]):
            for x in range(game.ranges[0]):
                if game.map[y][x] == -2:
                    if check_circling(x, y):
                        game.map[y][x] == -1
                        amount += 1

# class Delayed(Player):
#     name = "⏳ Délayé"
#     description = "Arrive en jeu 3 tours après le début du jeu. Commence avec 12 unités"
#     x, y = 0, 0
#
#     def spawn(self, game, x, y):
#         self.x, self.y = max(1, min(x, game.ranges[0]-2)), max(1, min(y, game.ranges[1]-1))
#
#     def on_turn_end(self, game):
#         if game.round == 4:
#             for dx in range(-1, 3):
#                 for dy in range(-1, 2):
#                     game.map[self.x + dx][self.y + dy] = self.index
