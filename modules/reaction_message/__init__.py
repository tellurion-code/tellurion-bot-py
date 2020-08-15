import discord

from modules.base import BaseClassPython
from modules.reaction_message.reaction_message import ReactionMessage

import modules.reaction_message.globals as global_values
global_values.init()


class MainClass(BaseClassPython):
    name = "ReactionMessage"
    help = {
        "description": "Module des messages de choix",
        "commands": {
            "`{prefix}{command} test`": "Envoies un messgae à réaction par défaut"
        }
    }
    help_active = False
    command_text = "reactionmessage"
    color = global_values.color

    def __init__(self, client):
        super().__init__(client)
        self.config["name"] = self.name
        self.config["coommand_text"] = self.command_text
        self.config["color"] = self.color
        self.config["help_active"] = self.help_active
        self.config["configured"] = True

    async def com_test(self, message, args, kwargs):
        async def effect(reactions):
            await message.channel.send("Le choix **" + [str(x[0] + 1) for x in reactions.values()][0] + "** a été validé")

        async def cond(reactions):
            if message.author.id in reactions:
                return len(reactions[message.author.id]) == 1

        await ReactionMessage(
            cond,
            effect
        ).send(
            message.channel,
            "Message de Test",
            "Ce message a pour but de tester les messages avec des réactions interactives",
            global_values.color,
            ["Choix 1", "Choix 2", "Choix 3", "Choix 4", "Choix 5"]
        )

    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            for message in global_values.reaction_messages:
                if message.message.id == reaction.message.id:
                    if reaction.emoji in message.number_emojis:
                        if message.check(reaction, user):
                            await message.add_reaction(reaction, user)
                        elif reaction.message.guild:
                            await message.message.remove_reaction(reaction.emoji, user)
                    elif reaction.message.guild:
                        await message.message.remove_reaction(reaction.emoji, user)

    async def on_reaction_remove(self, reaction, user):
        if not user.bot:
            for message in global_values.reaction_messages:
                if user.id in message.reactions:
                    if reaction.emoji in message.number_emojis:
                        if message.number_emojis.index(reaction.emoji) in message.reactions[user.id]:
                            if message.message.id == reaction.message.id:
                                await message.remove_reaction(reaction, user)
