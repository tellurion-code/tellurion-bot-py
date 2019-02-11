import discord
import asyncio
import datetime
import time

class MainClass():
    def __init__(self, client, modules, owners):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.events=['on_message'] #events list
        self.command="/perdu" #command prefix (can be empty to catch every single messages)

        self.channel=463354857537929217

        self.name="Archive"
        self.description="Module donnant les statistiques sur les perdants"
        self.interactive=True
        self.color=0xff6ba6
        self.help="""\
 /perdu
 => Donne les statistiques des perdants du dernier mois
 
 /perdu <durée en jours>
 => Donne les statistiques des perdants depuis la durée donnée (exemple /perdu 30 donnera les statistiques des 30 derniers jours.)
 
 /perdu all
 => Donne les statistiques des perdants depuis la création du salon
"""
    async def fetch_stats(self, upto, today): #upto in days (integer)

        for channel in self.client.get_all_channels():
            if channel.id==self.channel:
                break

        messagedic={}
        async for message in channel.history(limit=None):
            if not message.author.id in messagedic.keys(): 
                messagedic[message.author.id]=[message]
            else:
                messagedic[message.author.id].append(message)

        statdic={}
        for userid,messagelist in messagedic.items():
            messagelist=messagelist[::-1]
            messagelist2=[]
            lastmessage=None
            print(userid, " ",len(messagelist))
            for message in messagelist:
                #userid==281166473102098433 and print((time.mktime(today.timetuple()) - time.mktime(message.created_at.timetuple()))/60/60/24, " ", upto)
                if (time.mktime(today.timetuple()) - time.mktime(message.created_at.timetuple()))/60/60/24 < upto and (lastmessage is None or ((time.mktime(message.created_at.timetuple())-time.mktime(lastmessage.created_at.timetuple()))/60 > 30)):
                    messagelist2.append(message)
                    lastmessage=message
            messagelist=messagelist2
            del messagelist2
            print(userid, " ",len(messagelist))
        return messagedic


    async def on_message(self, message):
        args=message.content.split()
        if len(args)==1:
            async with message.channel.typing():
                await self.fetch_stats(30, message.created_at)
        elif args[1]=="all":
            async with message.channel.typing():
                await self.fetch_stats(1e1000, message.created_at)
        else:
            async with message.channel.typing():
                await self.fetch_stats(int(args[1]), message.created_at)
