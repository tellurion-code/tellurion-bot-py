async def hasrole(member, roleidlist):
	return True
	for role in member.roles :
		for roleid in roleidlist:
			print(roleid + " " + role.id)
			if role.id == roleid :
				return True
	return False
