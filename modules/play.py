import discord
import asyncio
import datetime
import time

class MainClass():
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events=['on_message'] #events list
        self.command="%splay"%prefix #command prefix (can be empty to catch every single messages)

        self.name="Play"
        self.description="Module servant de soundboard"
        self.interactive=True
        self.color=0xc72c48
        self.help="""\
 </prefix>play <nombre>
 => Joue le morceau correspondant au nombre spécifié
 
 </prefix>play list
 => Affiche la liste des morceaux disponibles
"""

    async def on_message(self, message):
        args=message.content.split()
        if len(args) != 2:
            await self.modules['help'][1].send_help(message.channel, self)
        elif args[1] == "list":
            await message.channel.send(message.author.mention + ", ça à l'air de fonctionner, ici.")
        else:
            try:
                number = int(args[1])
                voice = self.client.join_voice_channel(message.author.voice.channel)
                await message.channel.send(message.author.mention + ", ça à l'air de fonctionner, ici aussi.")
                time.sleep(10)
                if voice.is_connected():
                    voice.disconnect()
            except ValueError:
                await self.modules['help'][1].send_help(message.channel, self)
            except:                
                await message.channel.send(message.author.mention + ", ah, ici ça bug. C'est la connexion au vocal qui ne fonctionne pas.")
