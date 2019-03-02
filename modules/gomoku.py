# dummy module
import asyncio
import os
import pickle
import random
from subprocess import call

import discord
from PIL import Image, ImageDraw, ImageFont

moduleFiles = "gomoku"


class MainClass:
    def save_object(self, object, object_name):
        with open("storage/%s/" % moduleFiles + object_name + "tmp", "wb") as pickleFile:
            pickler = pickle.Pickler(pickleFile)
            pickler.dump(object)
        call(['mv', "storage/%s/" % moduleFiles + object_name + "tmp", "storage/%s/" % moduleFiles + object_name])

    def load_object(self, object_name):
        if self.save_exists(object_name):
            with open("storage/%s/" % moduleFiles + object_name, "rb") as pickleFile:
                unpickler = pickle.Unpickler(pickleFile)
                return unpickler.load()

    def save_exists(self, object_name):
        return os.path.isfile("storage/%s/" % moduleFiles + object_name)

    def __init__(self, client, modules, owners, prefix):
        if not os.path.isdir("storage/%s" % moduleFiles):
            call(['mkdir', 'storage/%s' % moduleFiles])
        self.save = None
        # format : { 'currently_playing':[id,id,id],
        # 'player_game':{id:gameid} 'games':{gameid:{'White':id,'Black':id, 'hist':['h8','h9']}}}
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message', 'on_ready']  # events list
        self.command = ""  # command prefix (can be empty to catch every single messages)

        self.name = "Gomoku"
        self.description = "Module du jeu Gomoku"
        self.interactive = True
        self.color = 0xffff00
        self.help = """\
 </prefix>gomoku challenge <@mention>
 => Défie le joueur mentionné pour une partie de Gomoku
 
 </prefix>gomoku spectate <@mention>
 => Permet d'observer la partie d'un joueur en jeu
 
 </prefix>gomoku spectate stop
 => Permet d'arrêter d'observer une partie
 
 </prefix>gomoku leave
 => Quitte la partie en cours
 
 <coordonnées>
 => Joue aux coordonnées spécifiées si c'est votre tour et que les coordonnées sont valides
 
"""

    async def on_ready(self):
        if self.save is None:
            if self.save_exists('save'):
                self.save = self.load_object('save')
            else:
                self.save = {'currently_playing': [], 'player_game': {}, 'games': {}}
            self.save_object(self.save, 'save')
        for game_id in self.save['games'].keys():
            self.save['games'][game_id]['lock'] = False

    async def send_reactions(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def on_message(self, message):
        if self.save is None:
            await self.on_ready()
        else:
            if message.content.startswith('%sgomoku' % self.prefix):
                args = message.content.split()
                if len(args) > 1 and args[1] == 'challenge' and not len(message.mentions) == 0:
                    try:
                        if message.mentions[0].id not in self.save['currently_playing']:
                            if message.author.id not in self.save['currently_playing']:
                                self.save['currently_playing'] += [message.author.id, message.mentions[0].id]
                                game_id = 0
                                while game_id in self.save.keys():
                                    game_id += 1
                                black = random.choice([message.author, message.mentions[0]])
                                white = [message.author, message.mentions[0]][
                                    [message.author, message.mentions[0]].index(black) - 1]
                                self.save['games'].update({game_id: {'lock': False, 'specs': [], 'Black': black.id,
                                                                     'White': white.id, 'hist': []}})
                                self.save['player_game'].update(
                                    {message.author.id: game_id, message.mentions[0].id: game_id})

                                async def send_messages(condition, message_str, image_file):
                                    for user in condition:
                                        await user.send(message_str, file=image_file)

                                asyncio.ensure_future(
                                    send_messages(
                                        [
                                            self.client.get_user(id_) for id_ in
                                            [self.save['games'][game_id][color] for color in ['Black', 'White']] +
                                            self.save['games'][game_id]['specs']
                                        ],
                                        "C'est à %s de commencer" % black.mention,
                                        self.gen_img_from_hist(self.save['games'][game_id]['hist'])
                                    ), loop=self.client.loop)
                            else:
                                await message.channel.send(
                                    message.author.mention + ", vous êtes déjà dans une partie, finissez celle là pour "
                                                             "commencer. ^^")
                        else:
                            await message.channel.send(
                                message.author.mention + ", le joueur mentionné est déjà en train de jouer...")
                    except KeyError:
                        pass
                elif len(args) > 1 and args[1] == 'spectate' and (len(message.mentions) != 0 or "stop" in args):
                    if "stop" in args:
                        # Transform [["a","b"],["c","d"]] into ['a', 'b', 'c', 'd']
                        if message.author.id in [
                            inner for outer in [game['specs'] for game in self.save['games'].values()]
                            for inner in outer
                        ]:
                            for game_id in self.save['games'].keys():
                                if message.author.id in self.save['games'][game_id]['specs']:
                                    self.save['games'][game_id]['specs'].remove(message.author.id)
                                    await message.channel.send("Vous n'observez plus la partie n°%s" % game_id)
                        else:
                            await message.channel.send("Vous n'observez aucune partie.")
                    else:
                        try:
                            if message.mentions[0].id in self.save['currently_playing']:
                                game_id = self.save['player_game'][message.mentions[0].id]
                                if message.author.id not in self.save['games'][game_id]['specs']:
                                    self.save['games'][game_id]['specs'].append(message.author.id)
                                    await message.author.send("Vous observez maintenant une partie.",
                                                              file=self.gen_img_from_hist(
                                                                  self.save['games'][game_id]['hist'])
                                                              )
                                else:
                                    await message.channel.send(
                                        message.author.mention + ", vous êtes déjà en train d'observer cette partie...")
                            else:
                                await message.channel.send(
                                    message.author.mention + ", le joueur mentionné n'est pas dans une partie...")
                        except KeyError:
                            pass
                elif len(args) == 2 and args[1] == 'leave':
                    if message.author.id in self.save['currently_playing']:
                        game_id = self.save['player_game'][message.author.id]
                        for player_id in [self.save['games'][game_id][color] for color in ['White', 'Black']]:
                            self.save['currently_playing'].remove(player_id)
                            try:
                                del self.save['player_game'][player_id]
                            except KeyError:
                                pass
                            await self.client.get_user(player_id).send("La partie de Gomoku a été annulée.")
                        del self.save['games'][game_id]
                    else:
                        await message.channel.send(
                            "%s, vous n'êtes pas dans une partie de Gomoku" % message.author.mention)
                else:
                    await self.modules['help'][1].send_help(message.channel, self)
            elif message.author.id in self.save['currently_playing']:
                try:
                    game_id = self.save['player_game'][message.author.id]
                    test = None
                    test2 = None
                    if self.save['games'][game_id]['Black'] == message.author.id:
                        test = len(self.save['games'][game_id]['hist']) % 2 == 0
                    if self.save['games'][game_id]['White'] == message.author.id:
                        test2 = len(self.save['games'][game_id]['hist']) % 2 != 0
                    if test or test2:
                        test = self.get_valid_coords(message.content, self.save['games'][game_id]['hist'])
                        if test and not self.save['games'][game_id]['lock']:
                            self.save['games'][game_id]['lock'] = True
                            validate_message = await message.author.send(
                                file=self.gen_img_from_hist(self.save['games'][game_id]['hist'] + [test], test=True))
                            asyncio.ensure_future(self.send_reactions(validate_message, ['✅', '❌']),
                                                  loop=self.client.loop)

                            def check(reaction_, user):
                                return reaction_.message.id == validate_message.id and user.id == message.author.id and str(
                                    reaction_.emoji) in ['✅', '❌']

                            reaction, _ = await self.client.wait_for('reaction_add', check=check)
                            if str(reaction.emoji) == '✅':
                                await validate_message.delete()
                                self.save['games'][game_id]['hist'].append(test)
                                self.save['games'][game_id]['lock'] = False
                                res = self.gen_grid_from_hist(self.save['games'][game_id]['hist'], fin=True)
                                if any(res):
                                    message_text = "%s a gagné, bravo à cette personne !" % self.client.get_user(
                                        self.save['games'][game_id][['Black', 'White'][res.index(True)]]).mention
                                else:
                                    message_text = "C'est au tour de %s !" % (self.client.get_user(
                                        self.save['games'][game_id]['White'] if self.save['games'][game_id][
                                                                                    'Black'] == message.author.id else
                                        self.save['games'][game_id]['Black']).mention)
                                image_file = self.gen_img_from_hist(self.save['games'][game_id]['hist'])

                                async def send_messages(condition, message_text, file_name):
                                    for user in condition:
                                        await user.send(message_text, file=file_name)

                                asyncio.ensure_future(
                                    send_messages(
                                        [
                                            self.client.get_user(id_) for id_ in
                                            [self.save['games'][game_id][color] for color in ['Black', 'White']] +
                                            self.save['games'][game_id]['specs']
                                        ], message_text, image_file
                                    ),
                                    loop=self.client.loop)
                                if any(res):
                                    for player_id in [self.save['games'][game_id][color] for color in
                                                      ['White', 'Black']]:
                                        self.save['currently_playing'].remove(player_id)
                                        del self.save['player_game'][player_id]
                                    del self.save['games'][game_id]
                            if str(reaction.emoji) == '❌':
                                self.save['games'][game_id]['lock'] = False
                                await validate_message.delete()
                            self.save_object(self.save, 'save')
                except KeyError:
                    raise

    def is_win(self, grid, coordinates=None):
        def is_win_check(row, check):
            if row[check] is not None:
                for i in range(len(row)):
                    if row[i] == row[check]:
                        if i <= check < i + 5:
                            if row[i:i + 5].count(row[check]) >= 5:
                                return True
            return False

        def check_coordinates(index_line, index_case, grid_):
            hor = grid_[index_line]
            ver = [grid_[i][index_case] for i in range(len(grid_))]
            diagonal_1 = [
                [
                    index_line - min(index_line, index_case) + i, index_case - min(index_line, index_case) + i
                ] for i in
                range(15 - max(index_line - min(index_line, index_case), index_case - min(index_line, index_case)))
            ]
            diagonal_2 = [
                [
                    index_line - min(index_line, 14 - index_case) + i, index_case + min(index_line, 14 - index_case) - i
                ]
                for i in
                range(min(
                    15 - (index_line - min(index_line, 14 - index_case)),
                    15 - (14 - (index_case + min(index_line, 14 - index_case)))
                ))
            ]
            return is_win_check(hor, index_case) or \
                   is_win_check(ver, index_line) or \
                   is_win_check([grid_[coordinates[0]][coordinates[1]] for coordinates in diagonal_1],
                                diagonal_1.index([index_line, index_case])) or \
                   is_win_check([grid_[coordinates[0]][coordinates[1]] for coordinates in diagonal_2],
                                diagonal_2.index([index_line, index_case]))

        if coordinates is None:
            for index_line in range(len(grid)):
                for index_case in range(len(grid[index_line])):
                    if check_coordinates(index_line, index_case, grid):
                        return check_coordinates(index_line, index_case, grid)
        else:
            index_case, index_line = coordinates
            return check_coordinates(index_line, index_case, grid)
        return False

    def gen_img_from_hist(self, hist, test=False):
        return self.gen_img(self.gen_grid_from_hist(hist), test=test)

    def gen_grid_from_hist(self, hist, fin=False):
        grid = [[None for _ in range(15)] for _ in range(15)]
        i = 0
        final_turn = None
        for turn in hist:
            if i % 2 == 0:
                grid[turn[1]][turn[0]] = 'Black'
            else:
                grid[turn[1]][turn[0]] = 'White'
            final_turn = turn
            i += 1
        grid_copy = [row.copy() for row in grid]
        i = 0
        for turn in hist:
            if self.is_win(grid_copy, coordinates=turn):
                grid[turn[1]][turn[0]] += 'W'
            final_turn = turn
            i += 1
        if final_turn:
            grid[final_turn[1]][final_turn[0]] += 'L'
        if not fin:
            return grid
        if fin:
            black_win = any([any([True if 'BlackW' == case else False for case in row]) for row in grid])
            white_win = any([any([True if 'WhiteW' == case else False for case in row]) for row in grid])
            return black_win, white_win

    def get_valid_coords(self, coordinate_input, hist):
        try:
            coordinate = coordinate_input.upper()
            coordinates_list = []
            if coordinate[0] in "ABCDEFGHIJKLMNO":
                coordinates_list.append("ABCDEFGHIJKLMNO".index(coordinate[0]))
            else:
                return False
            if 0 < int(coordinate[1:]) < 16:
                coordinates_list.append(int(coordinate[1:]) - 1)
            else:
                return False
            if coordinates_list not in hist:
                return coordinates_list
            else:
                return False
        except:
            return False

    def gen_img(self, grid, test=False, m=1):
        if test:
            img = Image.new('RGBA', (640 * m, 640 * m), color=(255, 200, 200, 255))
        else:
            img = Image.new('RGBA', (640 * m, 640 * m), color=(200, 200, 200, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("assets/Hack-Bold.ttf", size=12 * m)
        for i in range(16):
            draw.line((i * 40 * m, 20 * m) + (i * 40 * m, 620 * m), fill=(128, 128, 128, 255), width=m - 1)
        for i in range(16):
            draw.line((20 * m, i * 40 * m) + (620 * m, i * 40 * m), fill=(128, 128, 128, 255), width=m - 1)
        draw.ellipse([((7 + 1) * 40 * m - 6 * m, (7 + 1) * 40 * m - 6 * m),
                      ((7 + 1) * 40 * m + 6 * m, (7 + 1) * 40 * m + 6 * m)], fill=(128, 128, 128, 255))
        for i in range(1, 16):
            draw.text((4 * m, m * 40 * i - 6 * m), str(i), font=font, fill=(255, 0, 0, 255))
        letters = "ABCDEFGHIJKLMNO"
        for i in range(1, 16):
            draw.text((m * 40 * i - 4 * m, 4 * m), letters[i - 1], font=font, fill=(255, 0, 0, 255))
        for index_line in range(len(grid)):
            for index_case in range(len(grid[index_line])):
                # print([((index_case +1)*40 -15 ,(index_line +1) * 40 - 15),((index_case +1)*40 + 15 ,(index_line +1) *
                #  40 + 15)])
                if grid[index_line][index_case] is not None:
                    if 'L' in grid[index_line][index_case][5:]:
                        draw.ellipse([((index_case + 1) * 40 * m - 17 * m, (index_line + 1) * 40 * m - 17 * m),
                                      ((index_case + 1) * 40 * m + 17 * m, (index_line + 1) * 40 * m + 17 * m)],
                                     fill=(54, 122, 57, 255))
                    if grid[index_line][index_case].startswith('White'):
                        draw.ellipse([((index_case + 1) * 40 * m - 13 * m, (index_line + 1) * 40 * m - 13 * m),
                                      ((index_case + 1) * 40 * m + 13 * m, (index_line + 1) * 40 * m + 13 * m)],
                                     fill=(12, 96, 153, 255))
                    if grid[index_line][index_case].startswith('Black'):
                        draw.ellipse([((index_case + 1) * 40 * m - 13 * m, (index_line + 1) * 40 * m - 13 * m),
                                      ((index_case + 1) * 40 * m + 13 * m, (index_line + 1) * 40 * m + 13 * m)],
                                     fill=(10, 10, 10, 255))
                    if 'W' in grid[index_line][index_case][5:]:
                        draw.ellipse([((index_case + 1) * 40 * m - 4 * m, (index_line + 1) * 40 * m - 4 * m),
                                      ((index_case + 1) * 40 * m + 4 * m, (index_line + 1) * 40 * m + 4 * m)],
                                     fill=(194, 45, 48, 255))
                else:
                    if [index_line, index_case] == [7, 7]:
                        draw.text(((index_case + 1) * 40 * m + 5 * m, (index_line + 1) * 40 * m + 5 * m),
                                  letters[index_case] + str(index_line + 1), font=font, fill=(128, 128, 128, 255))
                    else:
                        draw.text(((index_case + 1) * 40 * m + 1 * m, (index_line + 1) * 40 * m - 1 * m),
                                  letters[index_case] + str(index_line + 1), font=font, fill=(128, 128, 128, 255))
        file_name = "/tmp/%s.bmp" % random.randint(1, 10000000)
        img.save(file_name)
        return discord.File(file_name)
