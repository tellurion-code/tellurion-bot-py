async def UserByName(client, name):
    for member in client.get_all_members() :
        if member.name == name :
            return member
    return False
async def UserByID(client, id):
    for member in client.get_all_members() :
        if member.id == id :
            return member
    return False
