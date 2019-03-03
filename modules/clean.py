from modules.base import BaseClass


class MainClass(BaseClass):
    name = "clean"
    help = {
        "description": "Supprime des messages",
        "commands": {
            "`{prefix}clean`": "Supprime tous les messages du bot dans le salon"
        }
    }
    command_text = "clean"

    async def command(self, message, args, kwargs):
        def is_me(m):
            return m.author == self.client.user

        deleted = await message.channel.purge(limit=10000000, check=is_me)
        await message.channel.send('Deleted {} message(s)'.format(len(deleted)))