import traceback
import discord
import random
import asyncio

import settings
async def sendError(client, event, *args, **kwargs):
	try:
		message = args[0]
		embed = discord.Embed(title="Aïe :/", description="```PYTHON\n{0}```".format(traceback.format_exc()), color=0xdb1348)
		embed.set_footer(text="Ce message s'autodétruira dans une minute.", icon_url=settings.embederror.icon)
		embed.set_image(url=random.choice(settings.embederror.memes))
		messages_to_delete = []
		try:
			messages_to_delete.append(await client.send_message(message.channel, embed=embed))
		except:
			pass
		for member in client.get_all_members() :
			for ID in settings.owners :
				if ID == member.id :
					messages_to_delete.append(await client.send_message(member, embed=embed))
		await asyncio.sleep(60)
		await client.delete_messages(messages_to_delete)
	except:
		pass
