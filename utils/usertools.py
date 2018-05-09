async def UserByName(client, name):
	for member in client.get_all_members() :
		print(member.name)
		if member.name == name :
			return member
	return False
