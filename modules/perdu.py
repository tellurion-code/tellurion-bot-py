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

        self.channel=431016132040851459
        self.lost_role=544845665910390784 #grand_perdant

        self.name="Perdu"
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
        messagedicreduced={}
        for userid,messagelist in messagedic.items():
            messagelist=messagelist[::-1]
            messagelist2=[messagelist[0].author]
            lastmessage=None
            for message in messagelist:
                if (time.mktime(today.timetuple()) - time.mktime(message.created_at.timetuple()))/60/60/24 < upto and (lastmessage is None or ((time.mktime(message.created_at.timetuple())-time.mktime(lastmessage.created_at.timetuple()))/60 > 26)) and (not message.author.id==self.client.user.id):
                    messagelist2.append(message)
                    lastmessage=message
            messagelist=messagelist2
            del messagelist2
            messagedicreduced.update({userid:messagelist})
        sorted_by_losses=sorted(messagedicreduced.items(), key=lambda x: len(x[1]))[::-1]
        stats=[]
        for user in sorted_by_losses:
            to_append=[user[1][0], len(user[1])-1, 0] #user mention, number of losses, average time between each loss
            lastmessage=None
            i=0
            if len(user[1][1::])>1:
                to_append[2]=(time.mktime(user[1][1::][-1].created_at.timetuple()) - time.mktime(user[1][1::][0].created_at.timetuple()))/((len(user[1][1::])-1)*3600)
            stats.append(to_append)
        return sorted(sorted(stats, key=lambda x: x[2])[::-1], key=lambda x: x[1])[::-1][:10:]


    async def on_message(self, message):
        args=message.content.split()
        if len(args)==1:
            async with message.channel.typing():
                stats=await self.fetch_stats(7, message.created_at)
                if not self.lost_role in [role.id for role in stats[0][0].roles]:
                    for member in self.client.get_all_members():
                        if self.lost_role in [role.id for role in member.roles]:
                            await member.remove_roles(discord.utils.get(member.guild.roles, id=self.lost_role))
                    await stats[0][0].add_roles(discord.utils.get(stats[0][0].guild.roles, id=self.lost_role))
                await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores", description='\n'.join(["%s : %s a **perdu %s fois** durant les %s derniers jours à en moyenne **%s heures d'intervalle.**"%(["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i],user[0].mention,user[1],7,round(user[2],1)) for i,user in enumerate(stats)]), color=self.color))
        elif args[1]=="all":
            async with message.channel.typing():
                await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores", description='\n'.join(["%s : %s a **perdu %s fois** depuis la création du salon à en moyenne **%s heures d'intervalle.**"%(["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i],user[0].mention,user[1],round(user[2],1)) for i,user in enumerate(await self.fetch_stats(1e1000, message.created_at))]), color=self.color))
        else:
            try:
                int(args[1])
                async with message.channel.typing():
                    await message.channel.send(embed=discord.Embed(title="G-Perdu - Tableau des scores", description='\n'.join(["%s : %s a **perdu %s fois** durant les %s derniers jours à en moyenne **%s heures d'intervalle.**"%(["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"][i],user[0].mention,user[1],int(args[1]),round(user[2],1)) for i,user in enumerate(await self.fetch_stats(int(args[1]), message.created_at))]), color=self.color))
            except ValueError:
                await self.modules['help'][1].send_help(message.channel, self)
