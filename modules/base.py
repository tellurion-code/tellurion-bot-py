"""Base class for module, never use directly !!!"""
import os
import pickle


class BaseClass:
    """Base class for all modules, Override it to make submodules"""
    name = ""

    help = ""
    help_active = False

    color = 0x000000
    command_text = None

    def __init__(self, client):
        """Initialize module class

        Initialize module class, always call it to set self.client when you override it.

        :param client: client instance
        :type client: discord.Client"""
        self.client = client
        if not os.path.isdir(os.path.join("storage", self.name)):
            os.mkdir(os.path.join("storage", self.name))

    async def auth(self, user, role_list):
        if user.id in self.client.owners:
            return True
        for guild in self.client.guilds:
            if guild.get_member(user.id):
                for role_id in role_list:
                    if role_id in [r.id for r in guild.get_member(user.id).roles]:
                        return True

    async def parse_command(self, message):
        """Parse a command_text from received message and execute function
        %git update
        com_update(m..)
        Parse message like `{prefix}{command_text} subcommand` and call class method `com_{subcommand}`.

        :param message: message to parse
        :type message: discord.Message"""
        if message.content.startswith(self.client.config["prefix"] + (self.command_text if self.command_text else "")):

            content = message.content.lstrip(self.client.config["prefix"] + (self.command_text if self.command_text else ""))
            sub_command, args, kwargs = self._parse_command_content(content)
            sub_command = "com_" + sub_command
            if sub_command in dir(self):
                await self.__getattribute__(sub_command)(message, args, kwargs)
            else:
                await self.command(message, args, kwargs)

    @staticmethod
    def _parse_command_content(content):
        """Parse string

        Parse string like `subcommand argument "argument with spaces" -o -shortwaytopassoncharacteroption --longoption
        -o "option with argument"`. You can override this function to change parsing.

        :param content: content to parse
        :type content: str

        :return: parsed arguments: [subcommand, [arg1, arg2, ...], [(option1, arg1), (option2, arg2), ...]]
        :rtype: list[str, list, list]"""
        if not len(content.split()):
            return "", [], []
        # Sub_command
        sub_command = content.split()[0]
        args_ = []
        kwargs = []
        if len(content.split()) >= 2:
            # Take the other part of command_text
            content = content.split(" ", 1)[1].replace("\"", "\"\"")
            # Splitting around quotes
            quotes = [element.split("\" ") for element in content.split(" \"")]
            # Split all sub chains but brute chains and flat the resulting list
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

    async def _on_message(self, message):
        """Override this function to deactivate command_text parsing"""
        await self.parse_command(message)
        await self.on_message(message)

    async def command(self, message, args, kwargs):
        """Override this function to handle all messages starting with `{prefix}{command_text}`

        Function which is executed for all command_text doesn't match with a `com_{subcommand}` function"""
        pass

    def save_object(self, object_instance, object_name):
        with open(os.path.join("storage", self.name, object_name), "wb") as f:
            pickler = pickle.Pickler(f)
            pickler.dump(object_instance)

    def load_object(self, object_name):
        if self.save_exists(object_name):
            with open(os.path.join("storage", self.name, object_name), "rb") as f:
                unpickler = pickle.Unpickler(f)
                return unpickler.load()

    def save_exists(self, object_name):
        return os.path.exists(os.path.join("storage", self.name, object_name))

    def on_load(self):
        pass

    async def on_socket_raw_receive(self, message):
        """Override this function to handle this event."""
        pass

    async def on_socket_raw_send(self, payload):
        """Override this function to handle this event."""
        pass

    async def on_typing(self, channel, user, when):
        """Override this function to handle this event."""
        pass

    async def on_message(self, message):
        """Override this function to handle this event."""
        pass

    async def on_message_delete(self, message):
        """Override this function to handle this event."""
        pass

    async def on_raw_message_delete(self, payload):
        """Override this function to handle this event."""
        pass

    async def on_raw_bulk_message_delete(self, payload):
        """Override this function to handle this event."""
        pass

    async def on_message_edit(self, before, after):
        """Override this function to handle this event."""
        pass

    async def on_raw_message_edit(self, payload):
        """Override this function to handle this event."""
        pass

    async def on_reaction_add(self, reaction, user):
        """Override this function to handle this event."""
        pass

    async def on_raw_reaction_add(self, payload):
        """Override this function to handle this event."""
        pass

    async def on_reaction_remove(self, reaction, user):
        """Override this function to handle this event."""
        pass

    async def on_raw_reaction_remove(self, payload):
        """Override this function to handle this event."""
        pass

    async def on_reaction_clear(self, message, reactions):
        """Override this function to handle this event."""
        pass

    async def on_raw_reaction_clear(self, payload):
        """Override this function to handle this event."""
        pass

    async def on_private_channel_delete(self, channel):
        """Override this function to handle this event."""
        pass

    async def on_private_channel_create(self, channel):
        """Override this function to handle this event."""
        pass

    async def on_private_channel_update(self, before, after):
        """Override this function to handle this event."""
        pass

    async def on_private_channel_pins_update(self, channel, last_pin):
        """Override this function to handle this event."""
        pass

    async def on_guild_channel_delete(self, channel):
        """Override this function to handle this event."""
        pass

    async def on_guild_channel_create(self, channel):
        """Override this function to handle this event."""
        pass

    async def on_guild_channel_update(self, before, after):
        """Override this function to handle this event."""
        pass

    async def on_guild_channel_pins_update(self, channel, last_pin):
        """Override this function to handle this event."""
        pass

    async def on_member_join(self, member):
        """Override this function to handle this event."""
        pass

    async def on_member_remove(self, member):
        """Override this function to handle this event."""
        pass

    async def on_member_update(self, before, after):
        """Override this function to handle this event."""
        pass

    async def on_guild_join(self, guild):
        """Override this function to handle this event."""
        pass

    async def on_guild_remove(self, guild):
        """Override this function to handle this event."""
        pass

    async def on_guild_update(self, before, after):
        """Override this function to handle this event."""
        pass

    async def on_guild_role_create(self, role):
        """Override this function to handle this event."""
        pass

    async def on_guild_role_delete(self, role):
        """Override this function to handle this event."""
        pass

    async def on_guild_role_update(self, before, after):
        """Override this function to handle this event."""
        pass

    async def on_guild_emojis_update(self, guild, before, after):
        """Override this function to handle this event."""
        pass

    async def on_guild_available(self, guild):
        """Override this function to handle this event."""
        pass

    async def on_guild_unavailable(self, guild):
        """Override this function to handle this event."""
        pass

    async def on_voice_state_update(self, member, before, after):
        """Override this function to handle this event."""
        pass

    async def on_member_ban(self, guild, user):
        """Override this function to handle this event."""
        pass

    async def on_member_unban(self, guild, user):
        """Override this function to handle this event."""
        pass

    async def on_group_join(self, channel, user):
        """Override this function to handle this event."""
        pass

    async def on_group_remove(self, channel, user):
        """Override this function to handle this event."""
        pass

    async def on_relationship_add(self, relationship):
        """Override this function to handle this event."""
        pass

    async def on_relationship_remove(self, relationship):
        """Override this function to handle this event."""
        pass

    async def on_relationship_update(self, before, after):
        """Override this function to handle this event."""
        pass

    async def on_ready(self):
        """Override this function to handle this event."""
        pass

    async def on_connect(self):
        """Override this function to handle this event."""
        pass

    async def on_shard_ready(self):
        """Override this function to handle this event."""
        pass

    async def on_resumed(self):
        """Override this function to handle this event."""
        pass

    async def on_error(self, event, *args, **kwargs):
        """Override this function to handle this event."""
        pass

    async def on_guild_integrations_update(self, guild):
        """Override this function to handle this event."""
        pass

    async def on_webhooks_update(self, channel):
        """Override this function to handle this event."""
        pass
