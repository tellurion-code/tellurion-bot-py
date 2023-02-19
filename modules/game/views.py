import discord
import traceback

class GameView(discord.ui.View):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.timeout = None

    async def clear(self):
        self.clear_items()
        await self.message.edit(view=self)
        self.stop()

    async def freeze(self):
        self.disable_all_items()
        await self.message.edit(view=self)
        self.stop()

    async def delete(self):
        await self.message.delete()
        self.stop()

    async def on_check_failure(self, interaction):
        await interaction.response.defer()

    async def on_error(self, error, item, interaction):
        embed = discord.Embed(
            title="[Erreur] Aïe :/",
            description="```python\n{0}```".format(traceback.format_exc())
        )

        # Send message to dev channels
        config = self.game.mainclass.client.modules["errors"]["initialized_class"].config
        for chanid in config.dev_chan:
            try:
                await self.game.mainclass.client.get_channel(chanid).send(embed=embed.set_footer(text="Ce message ne s'autodétruira pas."))
            except BaseException as e:
                raise e


class PlayView(GameView):
    async def interaction_check(self, interaction):
        return interaction.user.id in self.game.players
