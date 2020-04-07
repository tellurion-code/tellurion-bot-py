class ReactionMessage:
    number_emojis = [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    def __init__(self, _check, _cond, _effect):
        self.check = _check
        self.cond = _cond
        self.effect = _effect
        self.reactions = {}

    async def add_reaction(self, reaction, user):
        print("add " + str(user.id))
        if user.id in self.reactions:
            if reaction.emoji != "✅":
                self.reactions[user.id].append(reaction.emoji)
        else:
            self.reactions[user.id] = [reaction.emoji]

        if reaction.emoji == "✅" and await self.cond(self.reactions):
            await self.effect(self, self.reactions)

        await self.update()

    async def remove_reaction(self, reaction, user):
        print("remove " + str(user.id))
        self.reactions[user.id].remove(reaction.emoji)

        await self.update()

    async def update(self):
        print("UPDATE")
        print(self.reactions)

        if await self.cond(self.reactions):
            print("Try and add")
            await self.message.add_reaction("✅")
        else:
            print("Try and clear")
            await self.message.clear_reaction("✅")
