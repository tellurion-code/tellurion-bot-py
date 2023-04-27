"""Role classes."""

# from modules.timebomb.utils import ...

class Role:
    icon = "❌"
    name = "Invalide"
    allegiance = None
    description = "Ce rôle ne devrait pas être visible"

    def __init__(self, game):
        self.game = game

    def __str__(self):
        return f"{self.icon} **{self.name}**"
    
    def get_starting_info(self):
        return f"Votre rôle est {self}: {self.description}"


class Good(Role):
    icon = "🟦"
    name = "Gentil"
    allegiance = "good"
    description = "Vous êtes dans l'équipe de Sherlock. **Trouvez les fils à désamorcer** avant qu'il ne soit trop tard!"


class Evil(Role):
    icon = "🟥"
    name = "Méchant"
    allegiance = "evil"
    description = "Vous êtes dans l'équipe de Moriarty. **Cachez les fils à désamorcer** avant la fin du temps, ou **trouvez la bombe** et activez-la!"

    def get_starting_info(self):
        info = super().get_starting_info()
        if len(self.game.players) > 4: info + "\nVotre équipe est composée de " + ", ".join(p for p in self.game.players.values() if p.role.allegiance == "evil")
        return info