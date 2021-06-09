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


    # Envoie le choix
    async def send(self, _channel, _embed, **kwargs):
        self.embed = _embed

        if "fields" in kwargs:
            for field in kwargs["fields"]:
                self.embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"] if "inline" in field else False
                )

        self.message = await _channel.send(embed=self.embed, components=self.components)

    #Met à jour le message
    async def update(self):
        if not self.message:
            return

        await self.message.edit(embed=self.embed, components=self.components)

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
