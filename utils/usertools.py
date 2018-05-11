async def UserByName(client, name):
	for member in client.get_all_members() :
		if member.name == name :
			return member
	return False
