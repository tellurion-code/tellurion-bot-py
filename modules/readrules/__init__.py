from modules.base import BaseClassPython


class MainClass(BaseClassPython):
    name = "ReadRules"
    color = 0xff071f
    help_active = False
    help = {
        "description": "Module d'accueil",
        "commands": {
        }
    }

    def __init__(self, client):
        super().__init__(client)
        self.config.init({"accepted_role": 0,
                          "new_role": 0,
                          "listen_chan": 0,
                          "log_chan": 0,
                          "passwords": [],
                          "succes_pm": "Félicitations, vous savez lire les règles!",
                          "succes": "{user} a désormais accepté."})

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == self.config.listen_chan:
            if message.content.lower() in self.config.passwords:
                new_role = self.client.id.get_role(id_=self.config.new_role, guilds=[message.channel.guild])
                if new_role in message.author.roles:
                    await message.author.remove_roles(new_role)
                    await message.author.add_roles(self.client.id.get_role(id_=self.config.accepted_role,
                                                                           guild=[message.channel.guild]))
                    await message.author.send(self.config.succes_pm)
                    await message.channel.guild.get_channel(self.config.log_chan).send(
                        self.config.succes.format(user=message.author.mention))
            else:
                await message.author.send(f"Le mot de passe que vous avez entré est incorrect : `{message.content}`.\nNous vous prions de lire le règlement afin d'accéder au serveur complet.")
