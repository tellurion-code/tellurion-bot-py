from modules.base import BaseClassPython

class MainClass(BaseClassPython):
    name = "Purge"
    help = {
        "description": "Suppression de messages en block.",
        "commands": {
            "`{prefix}{command} <message_id>`": "Supprime tous les messages du salon jusqu'au message spécifié",
        }
    }

    async def command(self, message, args, kwargs):
        message_id = None
        try: 
            message_id = int(args[0])
        except ValueError:
            pass
        if len(args) and message_id is not None:
            messages_list=[]
            done=False
            async for current in message.channel.history(limit=None):
                if int(current.id) == message_id:
                    done = True
                    break
                elif message.id != current.id:
                    messages_list.append(current)
            if done:
                chunks = [messages_list[x:x+99] for x in range(0, len(messages_list), 99)]
                for chunk in chunks:
                    await message.channel.delete_messages(chunk)
                await message.channel.send(f"**{len(messages_list)}** messages supprimés.")
            else:
                await message.channel.send("Le message spécifié n'a pas été trouvé.")
        else:
            await message.channel.send("Arguments invalides.")
