
Bot discord Python pour le serveur officiel d'e-penser
=
Ce bot est un supplément au [Bot JS](https://github.com/epenserdiscord/epenser-bot)


## Installer le bot en environnement de développement

Si vous souhaitez développer sur le bot sans vouloir le lancer en continue, vous avez juste à cloner ce repository en utilisant
```sh
git clone https://github.com/epenserdiscord/epenser-bot-py.git
```
Vous pouvez ensuite le lancer en utilisant
```sh
export DISCORD_TOKEN=token
make
```
Remplacez seulement `token` par le token de votre bot, disponible sur https://discordapp.com/developers/applications/me.

Vous pouvez aussi utiliser [python-dotenv](https://github.com/theskumar/python-dotenv) (`sudo pip install -U "python-dotenv[cli]"`) et lancer avec `dotenv run make` pour charger votre token à partir du fichier `.env`.

Contenu du `.env` :
```sh
DISCORD_TOKEN=token
```
**Attention**, ne jamais commit le fichier `.env`.

## Installer le bot en environnement de production

Si vous souhaitez utiliser le bot dans un milieu de production, vous pouvez utiliser un script systemd comme ceci :
On utilise ici [python-dotenv](https://github.com/theskumar/python-dotenv) pour charger les variables d'environnement à partir du fichier `.env`.

```
[Unit]
Description=Epenser bot python

[Service]
Type=simple
PIDFile=/run/epenser-bot-py.pid
ExecStart=/usr/local/bin/dotenv run /user/bin/make 
User=user
Group=user
WorkingDirectory=/path/to/epenser-bot-py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Remplacez `user` par l'utilisateur que vous utilisez, et `/path/to/epenser-bot-py` par l'emplacement du repository git.

Ce fichier doit être écrit à l'emplacement `/etc/systemd/system/epenser-bot-py.service`.
Vous devez ensuite lancer `sudo systemctl enable epenser-bot-py.service` pour activer le service.

Le bot est installé, vous pouvez le démarrer avec `sudo service epenser-bot-py start`, le stopper, le redémarrer ou encore voir son status. Le bot redémarrera automatiquement et sera lancé automatiquement lors d'un redémarrage de la machine. 
