import discord

import settings.newuser

async def addrole(client, member):
    print(member.roles)
    if len(member.roles) == 1 :
        await client.add_roles(member, discord.utils.get(member.server.roles, id=settings.newuser.roleid))
async def initscan(client):
    for member in client.get_all_members() :
        print(member.roles)
        if len(member.roles) == 1:
            await client.add_roles(member, discord.utils.get(member.server.roles, id=settings.newuser.roleid))

async def giveroleMessage(client, message):
    if message.content.lower()=="cacahuète" or message.content.lower()=="cacahuete" :
        try:
            await client.add_roles(message.author, discord.utils.get(message.author.server.roles, id=settings.newuser.rulesroleid))
            await asyncio.sleep(1)
            await client.remove_roles(message.author, discord.utils.get(message.author.server.roles, id=settings.newuser.newuserroleid))
        except:
            found=False
            for member in client.get_all_members():
                if str(member.id) == str(message.author.id) :
                    try:
                        await client.add_roles(member, discord.utils.get(member.server.roles, id=settings.newuser.rulesroleid))
                        await asyncio.sleep(1)
                        await client.remove_roles(member, discord.utils.get(member.server.roles, id=settings.newuser.newuserroleid))
                        found=True
                    except:
                        pass
            if not found:
                raise
