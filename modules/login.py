async def print_user(client):
	print('''\nLe mot de passe c'est trois @''' + client.user.name + "#" + client.user.discriminator)
	print('-------')
