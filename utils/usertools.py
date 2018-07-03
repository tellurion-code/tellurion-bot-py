from async_lru import alru_cache #pip3 install async_lru

async def UserByName(client, name):
    for member in client.get_all_members() :
        if member.name == name :
            return member
    return False
@alru_cache(maxsize=4096)
async def UserByID(client, id):
    for member in client.get_all_members() :
        if member.id == id :
            return member
    return False
