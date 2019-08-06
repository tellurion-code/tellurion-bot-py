# dummy module

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "Git"

    super_users = [431043517217898496]

    color = 0x000000

    help_active = True
    help = {
        "description": "Module gérant les redémarages du bot",
        "commands": {
            "`{prefix}{command} update`": "Execute les commandes suivantes dans le dossier du bot:"
                                          "```BASH\n"
                                          "git fetch --all "
                                          "git reset --hard origin/<branch_name>```",
        }
    }

    command_text = "git"

    async def com_update(self, message, args, kwargs):
#        with os.popen('git fetch --all') as std_in:
#            await message.channel.send(std_in.read())
##        with os.popen('git symbolic-ref HEAD 2>/dev/null') as std_in:
 #           branch = std_in.read().replace('refs/heads/', '')
 #       with os.popen('git reset --hard origin/%s' % branch) as std_in:
 #           await message.channel.send(std_in.read())
        await message.channel.send(message.author.mention + ", Le dépôt a été mis à jour (fetch + reset --hard).")
        print("git update")
