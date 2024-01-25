import random
import discord

from modules.base import BaseClassPython

from modules.botc.game import Game
from modules.botc.phases import Phases
from modules.botc.player import Player


class MainClass(BaseClassPython):
    name = "botc"
    help = {
        "description": "Gère les parties par texte de BOTC",
        "commands": {
            "{prefix}{command} create": "Crée une partie avec l'auteur du message en tant que Conteur.",
            "{prefix}{command} day": "(Conteur) Commence la journée.",
            "{prefix}{command} open [nom]": "(Conteur) Commence la journée et ouvre les nominations dans un fil avec le nom donné. Si aucun n'est donné, réutilise le dernier fil de nomination s'il existe.",
            "{prefix}{command} close": "(Conteur) Ferme les nominations.",
            "{prefix}{command} night": "(Conteur) Ferme les votes et démarre la nuit.",
            "{prefix}{command} thread <nom>": "(Conteur) Crée un thread avec le nom donné pour tous les joueurs.",
            "{prefix}{command} stthreads [message]": "(Conteur) Crée un thread privé avec chaque joueur, et envoie le message donné dans chaque.",
            "{prefix}{command} order [mentions]": "(Conteur) Place les joueurs mentionnés en haut de l'ordre, puis l'affiche.",
            "{prefix}{command} add/remove <mentions>": "(Conteur) Ajoute/Enlève les joueurs mentionnés à/de la partie.",
            "{prefix}{command} replace <mention> <mention>": "(Conteur) Remplace un joueur par un autre utilisateur.",
            "{prefix}{command} whisper <mentions>": "Crée un thread privé avec les joueurs mentionnés."
        }
    }
    command_text = "botc"
    help_active = True
    color = 0x9932cc

    def __init__(self, client):
        super().__init__(client)
        # self.config.init({"help_active": True,
        #     "color": globals.color,
        #     "auth_everyone": True,
        #     "authorized_roles": [],
        #     "authorized_users": [],
        #     "command_text": "avalon",
        #     "configured": True
        # })
        self.config["color"] = self.color
        self.config["auth_everyone"] = True
        self.config["configured"] = True
        
        self.debug = False
        self.games = {}

        self.emojis = {
            "for": self.client.get_emoji("857736591535505438") or "✅",
            "against": self.client.get_emoji("857736495577563147") or "❌"
        }

    async def on_ready(self):
        if self.objects.save_exists("globals"):
            object = self.objects.load_object("globals")
            self.debug = object["debug"]

        if self.objects.save_exists("games"):
            games = self.objects.load_object("games")
            for channel, object in games.items():
                print(f"Reloading game in {channel}")
                self.games[int(channel)] = await Game(self).parse(object, self.client)

    async def command(self, message, args, kwargs):
        if message.channel.id in self.games:
            game = self.games[message.channel.id]
            save_and_delete = await game.on_command(message, args, kwargs)
            if save_and_delete:
                game.save()
                await message.delete()

    async def com_create(self, message, args, kwargs):
        if message.channel.id not in self.games:
            self.games[message.channel.id] = Game(self, message=message)
            await self.games[message.channel.id].on_creation(message)

    async def com_end(self, message, args, kwargs):
        if message.channel.id in self.games and self.games[message.channel.id].storyteller == message.author:
            await self.games[message.channel.id].end()
            del self.games[message.channel.id]
            await message.channel.send("Merci d'avoir joué à Blood on the Clocktower!")
            # TODO: Add recap

    async def com_thread(self, message, args, kwargs):
        if len(args) < 2: return await message.delete()

        if message.channel.id in self.games and self.games[message.channel.id].storyteller == message.author:
            thread = await message.channel.create_thread(name=' '.join(args[1:]), type=discord.ChannelType.public_thread)
            await thread.send(self.games[message.channel.id].role.mention)
        
        await message.delete()

    async def com_whisper(self, message, args, kwargs):
        if len(args) < 2: return await message.delete()
        if message.channel.id not in self.games: return await message.delete()

        game = self.games[message.channel.id]
        if game.phase not in (Phases.day, Phases.nominations): return await message.delete()

        if message.author.id in game.players or message.author == game.storyteller:
            targets = set((game.players[message.author.id],))
            for arg in args[1:]:
                for id in discord.utils.raw_mentions(arg):
                    if id != game.storyteller.id and id not in game.players: continue
                targets.add(game.players[id])

            if len(targets) == 1: return await message.delete()

            thread = await message.channel.create_thread(name=", ".join(x.display_name for x in targets), type=discord.ChannelType.private_thread, auto_archive_duration=24*60)
            await thread.add_user(game.storyteller)
            for player in targets:
                await thread.add_user(player.user)
                # player.whispers += 1

            if message.author == game.storyteller: await message.delete()
            
            # embed = discord.Embed(title="Nouvelle discussion privée")
            # embed.add_field(
            #     name="Discussions utilisées",
            #     value='\n'.join(f"{game.players[x].display_name}: {game.players[x].whispers}" for x in targets)
            # )
            # await thread.send(embed)
        else:
            await message.delete()

    async def com_stthreads(self, message, args, kwargs):
        if message.channel.id in self.games:
            game = self.games[message.channel.id]
            if message.author != game.storyteller: return await message.delete()

            msg = ' '.join(args[1:]) if len(args) > 1 else None
            for player in game.players.values():
                thread = await message.channel.create_thread(name=f"[Conteur] {player}", type=discord.ChannelType.private_thread)
                await thread.add_user(game.storyteller)
                await thread.add_user(player.user)
                if msg: await thread.send(msg)
            
        await message.delete()

    async def com_order(self, message, args, kwargs):
        if message.channel.id in self.games:
            game = self.games[message.channel.id]
            if message.author != game.storyteller: return
            if len(game.order) == 0: return

            args.reverse()
            for mention in args:
                player = game.player_from_mention(mention)
                if not player: continue
                game.order.remove(player.user.id)
                game.order.insert(0, player.user.id)
            
            await game.send_order(message.channel)
            await game.control_panel.update()

    async def com_add(self, message, args, kwargs):
        if message.channel.id in self.games:
            game = self.games[message.channel.id]
            if message.author != game.storyteller: return
            if len(game.order) == 0: return

            for mention in args:
                ids = discord.utils.raw_mentions(mention)
                if len(ids) == 0: continue
                id = ids[0]
                game.players[id] = Player(game, game.channel.guild.get_member(id))
                game.order.append(id)
            
            await game.send_order(message.channel)
            await game.control_panel.update()

    async def com_remove(self, message, args, kwargs):
        if message.channel.id in self.games:
            game = self.games[message.channel.id]
            if message.author != game.storyteller: return
            if len(game.order) == 0: return

            for mention in args:
                player = game.player_from_mention(mention)
                if not player: continue
                game.order.remove(player.user.id)
                del game.players[player.user.id]
            
            await game.send_order(message.channel)
            await game.control_panel.update()

    async def com_replace(self, message, args, kwargs):
        if len(args) != 3:
            return await message.channel.send("Nombre d'arguments invalide")

        if message.channel.id in self.games:
            game = self.games[message.channel.id]
            if message.author != game.storyteller: return
            if len(game.order) == 0: return

            player = game.player_from_mention(args[1])
            if not player:
                return await message.channel.send(f"`{args[1]}` n'est pas une mention valide ou un joueur dans le jeu")

            ids = discord.utils.raw_mentions(args[2])
            if len(ids) == 0:
                return await message.channel.send(f"`{args[2]}` n'est pas une mention valide")
            
            id = ids[0]
            user = game.channel.guild.get_member(id)
            if id in game.players:
                return await message.channel.send(f"`{user.display_name}` est déjà dans en jeu")

            index = game.order.index(player.user.id)
            del game.players[player.user.id]
            game.players[id] = Player(game, user)
            game.order[index] = id
            
            await game.send_order(message.channel)
            await game.control_panel.update()

    # Active le debug: enlève le nombre minimal de joueurs
    async def com_debug(self, message, args, kwargs):
        if message.author.id == 240947137750237185:
            self.debug = not self.debug
            await message.channel.send("Debug: " + str(self.debug))

            if self.objects.save_exists("globals"):
                save = self.objects.load_object("globals")
            else:
                save = {}

            save["debug"] = self.debug
            self.objects.save_object("globals", save)


# Module créé par Le Codex#9836 (ou le_codex)
