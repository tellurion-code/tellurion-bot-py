import discord

from modules.base import BaseClassPython
from modules.hidden.game import Game
from modules.reaction_message.reaction_message import ReactionMessage

class MainClass(BaseClassPython):
    name = "Rôles cachés"
    help = {
        "description": "Distribue des rôles cachés",
        "commands": {
            "`{prefix}{command} create`": "Crée une partie s'il n'y en a pas déjà une dans le salon",
            "`{prefix}{command} reset`": "Reinitialise la partie",
            "`{prefix}{command} roles set/add/remove`": "Change les rôles, ou affiche les rôles en jeu si aucune sous-commande n'est donnée",
            "`{prefix}{command} rules`": "Affiche les règles et les explications des rôles"
        }
    }
    help_active = True
    command_text = "hidden"
    color = 0x123456
    games = {}

    def __init__(self, client):
        super().__init__(client)
        self.config["name"] = self.name
        self.config["command_text"] = self.command_text
        self.config["color"] = self.color
        self.config["help_active"] = self.help_active
        self.config["configured"] = True
        self.config["auth_everyone"] = True

    async def command(self, message, args, kwargs):
        if args[0] == "join't":
            await message.channel.send(message.author.mention + " n'a pas rejoint la partie")

    async def com_create(self, message, args, kwargs):
        if message.channel.id in self.games:
            await message.channel.send("Il y a déjà une partie en cours dans ce channel")
        else:
            self.games[message.channel.id] = Game(self, message=message)
            await self.games[message.channel.id].on_creation()

    # Réitinitialise et supprime la partie
    async def com_reset(self, message, args, kwargs):
        if message.channel.id in self.games:
            async def confirm(reactions):
                if reactions[message.author.id][0] == 0:
                    await message.channel.send("La partie a été réinitialisée")

                    if self.games[message.channel.id].game_creation_message:
                        await self.games[message.channel.id].game_creation_message.delete()

                    del self.games[message.channel.id]

            async def cond(reactions):
                if message.author.id in reactions:
                    return len(reactions[message.author.id]) == 1
                else:
                    return False

            await ReactionMessage(
                cond,
                confirm
            ).send(
                message.channel,
                "Êtes vous sûr.e de vouloir réinitialiser la partie?",
                "",
                self.color,
                ["Oui", "Non"],
                emojis=["✅", "❎"],
                validation_emoji="⭕"
            )
        else:
            await message.channel.send("Il n'y a pas de partie en cours")

    async def com_roles(self, message, args, kwargs):
        if message.channel.id not in self.games:
            await message.channel.send("Il n'y a pas de partie en cours")
            return

        game = self.games[message.channel.id]
        if len(args) == 1:
            if len(game.roles):
                await message.channel.send(embed=discord.Embed(
                    title="Liste des rôles (" + str(len(game.roles)) + ") :",
                    description=', '.join([game.roles]),
                    color=self.color))
            else:
                await message.channel.send(embed=discord.Embed(
                    title="Liste des rôles :",
                    description="Aucun rôle n'a été défini.",
                    color=self.color
                ))
            return

        if message.author.id not in game.players:
            await message.channel.send("Vous n'êtes pas dans la partie")
            return

        args.pop(0)
        subcommand = args.pop(0)

        if subcommand == "reset":
            game.roles = []
            await message.channel.send("Les rôles ont été réinitialisés")
        else:
            roles = args

            for i, role in enumerate(roles):
                roles[i] = role.lower()

            if subcommand == "set":
                game.roles = [x for x in roles]
            elif subcommand == "add":
                game.roles.extend([x for x in roles])
            elif subcommand == "remove":
                for x in roles:
                    for role in game.roles:
                        if role == x:
                            game.roles.remove(role)
            else:
                await message.channel.send("Sous-commande invalide")

            await message.channel.send(embed=discord.Embed(
                title="Liste des rôles (" + str(len(game.roles)) + ") :",
                description=', '.join(game.roles),
                color=self.color))
            await game.view.update_join_message()
