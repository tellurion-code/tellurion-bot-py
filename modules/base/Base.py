"""Base class for module, never use directly !!!"""
import asyncio
import os
from typing import List

import discord

from config import Config
from storage import Objects


class BaseClass:
    """Base class for all modules, Override it to make submodules"""
    name = ""
    help = {
        "description": "",
        "commands": {

        }
    }

    def __init__(self, client):
        """Initialize module class

        Initialize module class, always call it to set self.client when you override it.

        :param client: client instance
        :type client: LBI"""
        self.client = client
        self.objects = Objects(path=os.path.join("data", self.name.lower()))
        self.config = Config(parent=self.client.config, name="mod-" + self.name.lower())
        self.config.init({"help_active": True, "color": 0x000000, "auth_everyone": False, "authorized_roles": [],
                          "authorized_users": [], "command_text": self.name.lower(), "configured": False})

    async def send_help(self, channel):
        embed = discord.Embed(
            title="[{nom}] - Aide".format(nom=self.name),
            description="*" + self.help["description"].format(prefix=self.client.config['prefix']) + "*",
            color=self.config.color
        )
        for command, description in self.help["commands"].items():
            embed.add_field(name=command.format(prefix=self.client.config['prefix'], command=self.config.command_text),
                            value="-> " + description.format(prefix=self.client.config['prefix'],
                                                             command=self.config.command_text),
                            inline=False)
        await channel.send(embed=embed)

    def auth(self, user: discord.User, role_list: List[int] = None, user_list: List[int] = None,
             guild: int = None):
        """
        Return True if user is an owner of the bot or in authorized_users or he have a role in authorized_roles.

        :param user: User to check
        :param user_list: List of authorized users, if not specified use self.authorized_users
        :param role_list: list of authorized roles, if not specified use self.authorized_roles
        :param guild: Specific guild to search role
        :type user_list: List[Int]
        :type role_list: List[Int]
        :type guild: Int
        :type user: discord.User
        """
        if self.config.auth_everyone:
            return True
        if user_list is None:
            user_list = self.config.authorized_users + self.client.config.admin_users
        if user.id in user_list:
            return True
        if role_list is None:
            role_list = self.config.authorized_roles + self.client.config.admin_roles
        if guild is None:
            guilds = self.client.guilds
        else:
            guilds = [guild]
        for guild in guilds:
            if guild.get_member(user.id):
                for role_id in role_list:
                    if role_id in [r.id for r in guild.get_member(user.id).roles]:
                        return True
        return False

    async def parse_command(self, message):
        """Parse a command_text from received message and execute function
        Parse message like `{prefix}{command_text} subcommand` and call class method `com_{subcommand}`.

        :param message: message to parse
        :type message: discord.Message"""
        command = self.client.config["prefix"] + (self.config.command_text if self.config.command_text else "") + " "
        if message.content.startswith(command):
            content = message.content.split(" ", 1)[1]
            sub_command, args, kwargs = self._parse_command_content(content)
            sub_command = "com_" + sub_command
            if self.auth(message.author):
                if sub_command in dir(self):
                    await self.__getattribute__(sub_command)(message, args, kwargs)
                else:
                    await self.command(message, args, kwargs)
            else:
                await self.unauthorized(message)

    @staticmethod
    def _parse_command_content(content):
        """Parse string

        Parse string like `subcommand argument "argument with spaces" -o -shortwaytopassoncharacteroption --longoption
        -o "option with argument"`. You can override this function to change parsing.

        :param content: content to parse
        :type content: str

        :return: parsed arguments: [subcommand, [arg1, arg2, ...], [(option1, arg1), (option2, arg2), ...]]
        :rtype: tuple[str, list, list]"""
        if not len(content.split()):
            return "", [], []
        # Sub_command
        sub_command = content.split()[0]
        args_ = [sub_command]
        kwargs = []
        if len(content.split()) > 1:
            # Remove subcommand
            content = content.lstrip(sub_command)
            # Take the other part of command_text
            content = content.lstrip().replace("\"", "\"\"")
            # Splitting around quotes
            quotes = [element.split("\" ") for element in content.split(" \"")]
            # Split all sub chains but raw chains and flat the resulting list
            args = [item.split() if item[0] != "\"" else [item, ] for sublist in quotes for item in sublist]
            # Second plating
            args = [item for sublist in args for item in sublist]
            # args_ are arguments, kwargs are options with arguments
            i = 0
            while i < len(args):
                if args[i].startswith("\""):
                    args_.append(args[i][1:-1])
                elif args[i].startswith("--"):
                    if i + 1 >= len(args):
                        kwargs.append((args[i].lstrip("-"), None))
                        break
                    if args[i + 1][0] != "-":
                        kwargs.append((args[i].lstrip("-"), args[i + 1].strip("\"")))
                        i += 1
                    else:
                        kwargs.append((args[i].lstrip("-"), None))
                elif args[i].startswith("-"):
                    if len(args[i]) == 2:
                        if i + 1 >= len(args):
                            break
                        if args[i + 1][0] != "-":
                            kwargs.append((args[i].lstrip("-"), args[i + 1].strip("\"")))
                            i += 1
                        else:
                            kwargs.append((args[i].lstrip("-"), None))
                    else:
                        kwargs.extend([(arg, None) for arg in args[i][1:]])
                else:
                    args_.append(args[i])
                i += 1
        return sub_command, args_, kwargs

    async def on_message(self, message: discord.Message):
        """Override this function to deactivate command_text parsing"""
        if message.author.bot:
            return
        await self.parse_command(message)

    async def command(self, message, args, kwargs):
        """Override this function to handle all messages starting with `{prefix}{command_text}`

        Function which is executed for all command_text doesn't match with a `com_{subcommand}` function"""
        pass

    async def com_help(self, message, args, kwargs):
        await self.send_help(message.channel)

    async def unauthorized(self, message):
        await message.channel.send("Vous n'êtes pas autorisé à effectuer cette commande")

    def dispatch(self, event, *args, **kwargs):
        # Method to call
        method = 'on_' + event
        try:
            # Try to get coro, if not exists pass without raise an error
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            # Run event
            asyncio.ensure_future(self.client._run_event(coro, method, *args, **kwargs), loop=self.client.loop)

    async def on_error(self, event_method, *args, **kwargs):
        pass
