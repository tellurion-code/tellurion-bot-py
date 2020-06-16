import discord

import modules.secrethitler.globals as globals

class ReactionMessage:
    def __init__(self, _cond, _effect, **kwargs):
        self.check = kwargs["check"] if "check" in kwargs else lambda r, u: True
        self.update_function = kwargs["update"] if "update" in kwargs else None
        self.temporary = kwargs["temporary"] if "temporary" in kwargs else True
        self.cond = _cond
        self.effect = _effect
        self.block = False

        self.reactions = {}

    #Envoies le choix
    async def send(self, _channel, _title, _description, _color, _choices, **kwargs):
        if len(_choices) == 0:
            raise Exception("Le nombre de choix doit être supérieur à 0")

        embed = discord.Embed(
            title = _title,
            description = _description,
            color = _color
        )

        if "fields" in kwargs:
            for field in kwargs["fields"]:
                embed.add_field(name = field["name"], value = field["value"], inline = field["inline"] if "inline" in field else False)

        self.number_emojis = (kwargs["emojis"] if "emojis" in kwargs else globals.number_emojis)[:len(_choices)]
        self.number_emojis.append(kwargs["validation_emoji"] if "validation_emoji" in kwargs else "✅")

        if "silent" not in kwargs:
            i = 0
            for choice in _choices:
                embed.description += self.number_emojis[i] + " " + choice + "\n"
                i += 1

        self.message = await _channel.send(embed = embed)

        for i,_ in enumerate(_choices):
            await self.message.add_reaction(self.number_emojis[i])

        globals.reaction_messages.append(self)

    #Trigger quand une réaction est ajoutée
    async def add_reaction(self, reaction, user):
        print("add " + str(user.id))
        if user.id in self.reactions:
            if reaction.emoji != self.number_emojis[-1]:
                self.reactions[user.id].append(self.number_emojis.index(reaction.emoji))
        else:
            self.reactions[user.id] = [self.number_emojis.index(reaction.emoji)]

        condition_on = await self.cond(self.reactions)
        if reaction.emoji == self.number_emojis[-1] and condition_on and not self.block:
            self.block = True
            await self.effect(self.reactions)

            if self.temporary:
                await self.message.delete()

            globals.reaction_messages.remove(self)
        else:
            await self.update(reaction)

    #Trigger quand une réaction est retirée
    async def remove_reaction(self, reaction, user):
        print("remove " + str(user.id))
        self.reactions[user.id].remove(self.number_emojis.index(reaction.emoji))

        # if len(self.reactions[user.id]) == 0:
        #     self.reactions.pop(user.id)

        await self.update(reaction)

    #Vérifie si la coche doit être affichée et fait la fonction update_function si elle existe
    async def update(self, reaction):
        print("UPDATE")
        print(self.reactions)

        if self.update_function:
            await self.update_function(self.reactions)

        if await self.cond(self.reactions):
            print("Try and add")
            await self.message.add_reaction(self.number_emojis[-1])
        else:
            if reaction.message.guild:
                await self.message.remove_reaction(self.number_emojis[-1], reaction.message.guild.me)
            else:
                await self.message.remove_reaction(self.number_emojis[-1], reaction.message.channel.me)
