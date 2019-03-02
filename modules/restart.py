class MainClass:
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message']  # events list
        self.command = "%srestart" % self.prefix  # command prefix (can be empty to catch every single messages)

        self.name = "Restart"
        self.description = "Module gérant les redémarrages du bot"
        self.interactive = True
        self.authlist = [431043517217898496]
        self.color = 0x000000
        self.help = """\
 </prefix>restart
"""

    async def on_message(self, message):
        args = message.content.split(" ")
        if args[0] == '%srestart' % self.prefix:
            if 'py' in args:
                await message.channel.send(message.author.mention + ", Le bot va redémarrer...")
            await self.client.logout()
        else:
            await self.modules['help'][1].send_help(message.channel, self)
