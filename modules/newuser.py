import settings.newuser
import discord
async def addrole(client, member):
    print(member.roles)
    if len(member.roles) == 1 :
        await client.add_roles(member, discord.utils.get(member.server.roles, id=settings.newuser.roleid))
async def initscan(client):
    for member in client.get_all_members() :
        print(member.roles)
        if len(member.roles) == 1:
            await client.add_roles(member, discord.utils.get(member.server.roles, id=settings.newuser.roleid))
