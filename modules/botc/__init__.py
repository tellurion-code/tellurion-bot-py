import random
import discord

from modules.base import BaseClassPython

from modules.botc.game import Game
from modules.botc.phases import Phases


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
        if len(args) < 2: return

        if message.channel.id in self.games and self.games[message.channel.id].storyteller == message.author:
            thread = await message.channel.create_thread(name=' '.join(args[1:]), type=discord.ChannelType.public_thread)
            await thread.send(self.games[message.channel.id].role.mention)
            await message.delete()

    async def com_whisper(self, message, args, kwargs):
        if len(args) < 2: return await message.delete()
        if message.channel.id not in self.games: return await message.delete()

        game = self.games[message.channel.id]
        if game.phase == Phases.night: return await message.delete()

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
        if message.channel.id in self.games and self.games[message.channel.id].storyteller == message.author:
            game = self.games[message.channel.id]
            msg = ' '.join(args[1:]) if len(args) > 1 else None
            for player in game.players.values():
                thread = await message.channel.create_thread(name=f"[Conteur] {player}", type=discord.ChannelType.private_thread)
                await thread.add_user(game.storyteller)
                await thread.add_user(player.user)
                if msg: await thread.send(msg)
            
        await message.delete()

    async def com_order(self, message, args, kwargs):
        if message.channel.id in self.games and self.games[message.channel.id].storyteller == message.author:
            game = self.games[message.channel.id]
            
            for mention in args.reverse():
                player = game.player_from_mention(mention)
                if not player: continue
                game.order.remove(player.user.id)
                game.order.insert(0, player.user.id)
            
            await message.channel.send(f"Ordre actuel: {','.join(str(game.players[id]) for id in game.order)}")

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
