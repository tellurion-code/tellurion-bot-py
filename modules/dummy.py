# dummy module
class MainClass:
    def __init__(self, client, modules, owners, prefix):
        self.client = client
        self.modules = modules
        self.owners = owners
        self.prefix = prefix
        self.events = ['on_message']  # events list
        self.command = "%sdummy" % self.prefix  # command prefix (can be empty to catch every single messages)

        self.name = "Dummy"
        self.description = "Module d'exemple"
        self.interactive = False
        self.color = 0x000000
        self.help = """\
 Aucune fonction.
"""

    async def on_message(self, message):
        print(message.content)
