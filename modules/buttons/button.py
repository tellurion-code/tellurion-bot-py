import discord
from discord_components import Button, ButtonStyle

import modules.buttons.globals as global_values

class ComponentMessage:
	def __init__(self, actionrows, **kwargs):
		self.temporary = kwargs["temporary"] if "temporary" in kwargs else True
		self.components = []

		i = 0
		for row in actionrows:
			self.components.append([])
			for component in row:
				self.components[len(self.components) - 1].append(FullButton(self, i, **component))
				i += 1

		self.message = None
		self.embed = None
		self.content= None

	# Envoie le choix
	async def send(self, _channel, **kwargs):
		self.embed = kwargs["embed"] if "embed" in kwargs else None
		self.content = kwargs["content"] if "content" in kwargs else None

		if not (self.content or self.embed):
			raise Exception("Missing content or embed")

		self.message = await _channel.send(self.content, embed=self.embed, components=self.components)

	#Met à jour le message
	async def update(self, actionrows=None):
		if not self.message:
			return

		if actionrows:
			for row in self.components:
				for component in row:
					component.delete()

			self.components = []

			i = 0
			for row in actionrows:
				self.components.append([])
				for component in row:
					self.components[len(self.components) - 1].append(FullButton(self, i, **component))
					i += 1

		await self.message.edit(self.content, embed=self.embed, components=self.components)

	# Supprime l'objet (et le message si force=True)
	async def delete(self, force=False, keepButtons=False):
		if self.temporary or force:
			await self.message.delete()
		elif not keepButtons:
			await self.message.edit(components=[])

		for row in self.components:
			for component in row:
				component.delete()
				del component


class FullButton(Button):
	def __init__(self, _componentMessage, index, **kwargs):
		self.effect = kwargs.pop("effect")
		self.cond = kwargs.pop("cond")

		super().__init__(**kwargs)

		self.componentMessage = _componentMessage
		self.index = index

		global_values.components[self.id] = self

	async def disable(self):
		self.disabled = True
		await self.componentMessage.update()

	async def enable(self):
		self.disabled = False
		await self.componentMessage.update()

	def delete(self):
		del global_values.components[self.id]

#  Module créé par Le Codex#9836
