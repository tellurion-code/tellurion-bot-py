# Tellurion - Bot Discord

[![viendez sur le serveur!](https://badgen.net/discord/members/7f8VZxE?icon=discord)](https://discord.gg/7f8VZxE) ![python version: 3.9+](https://badgen.net/badge/python/3.9+/blue)

## Installer le bot

Tout ce qui suit est prévu pour créer une instance "locale" du bot, afin de pouvoir développer sans casser le bot en ligne (pas comme moi, donc).

### Prérequis

On va partir du principe que vous savez déjà pourquoi vous voulez suivre ce tuto, et donc que vous avez sous la main :

- Un compte GitHub, ainsi que Git installé sur votre machine.
- Un compte Discord, ainsi qu'un serveur où vous êtes propriétaire.
- Python 3.9 (ou ultérieur) installé et **disponible en ligne de commande** (pour ceux qui auraient l'idée saugrenue de développer sur Windows)

### Etape 1 : Le module à installer

```
pip install pipenv
```

(sous Windows, faites un clic droit, et sélectionnez `Ouvrir la fenêtre PowerShell ici` pour ouvrir un terminal.)

### Etape 2 : Forker et cloner le repo

Une fois que c'est fait, il faut maintenant forker le repo pour pouvoir continuer. Si vous êtes connecté en lisant ceci, remontez la page et appuyez sur le bouton Fork en haut à droite (sinon, connectez-vous et relisez cette phrase). Une fois que c'est fait, il ne reste plus qu'à cloner ce fork :

- Si vous utilisez GitHub Desktop, cela se fait via le menu `File > Clone Repository...` : sélectionnez votre fork et choisissez ensuite l'emplacement du dossier sur votre disque.

- Si vous êtes en ligne de commande :
```bash
$ git clone https://github.com/<votre-username-git>/tellurion-bot-py.git
```
(où `<votre-username-git>` est à remplacer avec ce qui correspond dans votre cas)

### Etape 3 : Créer et inviter un bot discord

Avant de donner vie à un clone d'Alset, il va falloir créer ce clone d'abord (logique).
Rendez-vous sur https://discord.com/developers et connectez-vous. À partir de là, créez une nouvelle application et donnez-lui le nom que vous voulez.

Après quoi, rendez-vous dans le menu `Bot`, et créez un bot pour votre application, qui servira de clone d'Alset.

**Important** : Pour que le bot fonctionne correctement, activez les *Privileged Gateway Intents* qui se trouvent plus bas.

Enfin, remontez la page et cliquez sur le bouton `Copy` : le *token* de votre bot (i.e. son jeton d'authentification) vient d'être copié dans votre presse-papier. Gardez-le dans un coin, parce qu'il va servir plus tard.

Pour inviter le bot sur votre serveur, allez sur la page `OAuth2` et scrollez pour trouver un tableau de cases à cocher. Cochez `bot` et scrollez encore pour faire apparaître un autre tableau avec les permissions. Cochez celles qui sont pertinentes pour votre application.

Une fois que c'est fait, une URL devrait avoir été générée entre les deux tableaux : copiez-la dans un autre onglet. Discord va vous demander où vous souhaitez inviter le bot - d'où l'intérêt de disposer d'un serveur où vous êtes propriétaire (ou que vous pouvez gérer *a minima*) - et si vous souhaitez lui refiler les droits que vous aurez choisis. Confirmez une dernière fois : votre bot est désormais présent sur votre serveur.

### Etape 4 : Démarrer et interagir avec le bot

C'est la partie un peu délicate de ce tutoriel. Mais si vous suivez les instructions, ça devrait aller.

Dans un premier temps, avec votre éditeur préféré, créez un fichier appelé `.env` (à placer dans le même dossier que `main.py`) et mettez ceci :
```
# .env
DISCORD_TOKEN='<votre-token>'
```

`<votre-token>` étant bien évidemment à remplacer avec le *token* du bot que vous aviez gardé dans un bloc-notes.

Ensuite, dans un terminal, exécutez :
```
pipenv --python 3.10.6
pipenv install
```
(si vous avez la version 3.10.6 d'installée, sinon ajustez en fonction)

Cela devrait vous créer un environnement virtuel de travail et installer les dépendances nécessaires. A partir de là, démarrez une première fois le bot, puis arrêtez-le immédiatement après (avec un bon Ctrl-C). Cela permet de créer le dossier `data` avec les fichiers de configuration.

On a presque fini. Il faut maintenant configurer manuellement le bot pour que vous puissiez faire des tests. Dans cette optique, ouvrez le fichier `data/config.toml`. Dans ce fichier, après l'en-tête, se trouvent des blocs comme ceci :
```TOML
[mod-modules]
help_active = true
color = 0
auth_everyone = false
authorized_roles = []
authorized_users = []
command_text = "modules"
configured = false
```
Normalement, seuls deux blocs se trouvent ici : `mod-modules` et `mod-errors`. Il faut mettre `configured` à `true` pour que les modules soient exploitables.

Par ailleurs, à la ligne 4 de ce fichier se trouve la variable `admin_users`. Si vous ne voulez pas que votre clone d'Alset vous interdise l'accès à ses commandes, vous devez rajouter votre Discord ID à cette liste :
```TOML
admin_users = [314159265358979323,]
```
Comment obtenir cet ID ? Rien de plus simple : activez le mode développeur dans les paramètres Discord (section `Avancés`), faites un clic droit sur votre pseudo, et sélectionnez `Copier l'identifiant`.

(Note: il existe aussi la variable `admin_roles`, qui fonctionne avec des IDs de rôles.)

L'heure est maintenant venue de lancer le bot. Ouvrez un terminal, placez-vous dans le dossier contenant `main.py`, et exécutez :
```
pipenv run py main.py
```

Si tout se déroule comme prévu, les premières lignes de la console devraient être celles-ci :

```SHELL
$ pipenv run python main.py
Loading .env environment variables...
INFO:LBI:Starts to load modules...
INFO:LBI:Start loading module modules...
INFO:LBI:Module modules successfully imported.
INFO:LBI:Start loading module errors...
INFO:LBI:Module errors successfully imported.
INFO:LBI:Start loading module restart...
INFO:LBI:Module restart successfully imported.
INFO:LBI:Start loading module help...
INFO:LBI:Module help successfully imported.
```

Il ne vous reste plus qu'à vérifier que le bot répond correctement via Discord :
```
%modules list
```

Pour terminer, n'oubliez pas d'activer le module `restart` avec la commande `%modules enable restart` et en changeant la valeur de `configured` dans `data/config.toml` : cela vous permettra de stopper le bot pendant son exécution avec la commande `%restart`. Néanmoins, vous devrez le relancer manuellement via le terminal (ou bien coder un script pour le faire à votre place).
