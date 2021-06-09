import discord
from discord_components import DiscordComponents
from modules.base import BaseClassPython

from modules.buttons.button import ComponentMessage
import modules.buttons.globals as global_values
global_values.init()

class MainClass(BaseClassPython):
    name = "Buttons"
    help = {
        "description": "Manages buttons properly",
        "commands": {}
    }

    def __init__(self, client):
        super().__init__(client)
        self.config["auth_everyone"] = True
        self.config["configured"] = True
        self.config["help_active"] = False
        self.config["command_text"] = "button"
        self.config["color"] = global_values.color

    async def on_ready(self):
        DiscordComponents(self.client)
        print("COMPONENTS INIT")

    async def command(self, message, args, kwargs):
        async def effect(self, interaction):
            await self.disable()
            await interaction.respond(content="Validé " + str(self.index + 1))

            if not len([0 for r in self.componentMessage.components for x in r if not x.disabled]):
                await self.componentMessage.delete()

        def cond(interaction):
            return interaction.user.id == message.author.id

        await ComponentMessage(
            [
                [
                    {
                        "cond": cond,
                        "effect": effect,
                        "label": "TEST 1",
                        "style": 1
                    },
                    {
                        "cond": cond,
                        "effect": effect,
                        "label": "TEST 2",
                        "style": 2
                    }
                ],
                [
                     {
                         "cond": cond,
                         "effect": effect,
                         "label": "TEST 3",
                         "style": 3
                     },
                     {
                         "cond": cond,
                         "effect": effect,
                         "label": "TEST 4",
                         "style": 4
                     }
                ]
            ],
            temporary=False
        ).send(
            message.channel,
            discord.Embed(
                title="Message de Test",
                descirption="Ce message a pour but de tester les messages avec des réactions interactives",
                color=global_values.color
            )
        )

    async def on_button_click(self, interaction):
        if interaction.component.id in global_values.components:
            button = global_values.components[interaction.component.id]

            if button.cond(interaction) and not button.disabled:
                await button.effect(button, interaction)
            else:
                await interaction.respond(type=6)
        else:
            await interaction.respond(type=6)
