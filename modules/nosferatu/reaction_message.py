import discord

import modules.nosferatu.globals as globals

class ReactionMessage:
    def __init__(self, _cond, _effect, **kwargs):
        self.check = kwargs["check"] if "check" in kwargs else lambda r, u: True
        self.update_function = kwargs["update"] if "update" in kwargs else None
        self.cond = _cond
        self.effect = _effect

        self.reactions = {}

    #Envoies le choix
    async def send(self, _channel, _title, _description, _color, _choices):
        embed = discord.Embed(
            title = _title,
            description = _description,
            color = _color
        )

        i = 0
        for choice in _choices:
            embed.description += self.number_emojis[i] + " `" + choice + "`\n"
            i += 1

        self.message = await _channel.send(embed = embed)
        self.number_emojis = globals.number_emojis[:len(_choices)]
        self.number_emojis.append("✅")

        for i in range(len(_choices)):
            await self.message.add_reaction(self.number_emojis[i])

        globals.reaction_messages.append(self)

    #Trigger quand une réaction est ajoutée
    async def add_reaction(self, reaction, user):
        print("add " + str(user.id))
        if user.id in self.reactions:
            if reaction.emoji != "✅":
                self.reactions[user.id].append(self.number_emojis.index(reaction.emoji))
        else:
            self.reactions[user.id] = [self.number_emojis.index(reaction.emoji)]

        if reaction.emoji == "✅" and await self.cond(self.reactions):
            await self.effect(self.reactions)
            globals.reaction_messages.remove(self)

        await self.update()

    #Trigger quand une réaction est retirée
    async def remove_reaction(self, reaction, user):
        print("remove " + str(user.id))
        self.reactions[user.id].remove(self.number_emojis.index(reaction.emoji))

        await self.update()

    #Vérifie si la coche doit être affichée et fait la fonction update_function si elle existe
    async def update(self):
        print("UPDATE")
        print(self.reactions)

        if self.update_function:
            await self.update_function(self.reactions)

        if await self.cond(self.reactions):
            print("Try and add")
            await self.message.add_reaction("✅")
        else:
            print("Try and clear")
            await self.message.clear_reaction("✅")
