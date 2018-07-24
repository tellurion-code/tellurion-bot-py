
Bot discord Python pour le serveur officiel d'e-penser
=
Ce bot est un supplément au [Bot JS](https://github.com/epenserdiscord/epenser-bot)


Installer le bot
-
```BASH
user : git clone https://github.com/epenserdiscord/epenser-bot-py.git
```
Les dépendances seront installées au moment du lancement du bot.

Lancer le bot
-
```BASH
user : export DISCORD_TOKEN=token Remplacez par le token de votre bot.
user : cd path/to/epenser-bot-py/
user : while true ; do git fetch --all; git reset --hard origin/master; make; done
```
On peut aussi lancer le bot sans la boucle :
```BASH
user : export DISCORD_TOKEN=token Remplacez par le token de votre bot.
user : cd path/to/epenser-bot-py/
user : make
```
Daemoniser le bot
-
Le bot est actuellement organisé de manière à ce que la commande `/restart` quitte le programme et ce qu'un script à part vienne le relancer après avoir, par exemple, mis à jour les sources. Par conséquent, nous avons besoin d'un tel script. Celui qui est utilisé actuellement est séparé en plusieurs parties pour gérer les deux sections (JS et Python) avec :

`/home/epenser/run` (marqué en executable) 
```BASH
#!/bin/bash
export DISCORD_TOKEN=token
export GITHUB_TOKEN=token
sleep 20  #C'est pour le réseau :3
bash /home/epenser/pybot.sh &
bash /home/epenser/jsbot.sh
```
On ne s'intéresse ici pas au `jsbot.sh` mais uniquement `pybot.sh` :

`/home/epenser/pybot.sh`
```BASH
#!/bin/bash
set -o pipefail
cd /home/epenser/epenser-bot/epenser-bot-py/
while [ true ] ;do
date >> log
echo "---- git pull ----" >> log
echo >> log
git fetch --all 2>&1 | tee -a log
git reset --hard origin/master 2>&1 | tee -a log
echo >> log
./main.py 2>&1 | tee -a log
done
```
Le serveur utilisé pour hoster le bot est un raspberry sous raspbian. Il est donc sous systemd. Je ne me suis pas intéressé à Open-RC même si j'aurais pu.

`/etc/init.d/epenser`
```BASH
#!/bin/sh -e
### BEGIN INIT INFO
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
### END INIT INFO
DAEMON="/home/epenser/run"
daemon_OPT=""
DAEMONUSER="epenser"
daemon_NAME="run"

PATH="/sbin:/bin:/usr/sbin:/usr/bin"

test -x $DAEMON || exit 0

. /lib/lsb/init-functions

d_start () {
log_daemon_msg "Starting system $daemon_NAME Daemon"
start-stop-daemon --background --name $daemon_NAME --start --quiet --chuid $DAEMONUSER --exec $DAEMON -- $daemon_OPT
log_end_msg $?
}

d_stop () {
log_daemon_msg "Stopping system $daemon_NAME Daemon"
start-stop-daemon --name $daemon_NAME --stop --retry 5 --quiet --name $daemon_NAME
log_end_msg $?
}

case "$1" in

start|stop)
d_${1}
;;

restart|reload|force-reload)
d_stop
d_start
;;

force-stop)
d_stop
killall -q $daemon_NAME || true
sleep 2
killall -q -9 $daemon_NAME || true
;;

status)
status_of_proc "$daemon_NAME" "$DAEMON" "system-wide $daemon_NAME" && exit 0 || exit $?
;;
*)
echo "Usage: /etc/init.d/$daemon_NAME {start|stop|force-stop|restart|reload|force-reload|status}"
exit 1
;;
esac
exit 0
```
Pensez à remplacer les parties spécifiques.

(Il y a probablement des erreurs dans cette partie, j'ai jamais rien compris à systemD :( )

```BASH
root : systemctl daemon-reload
root : systemctl enable epenser.service
root : systemctl add-wants $(systemctl get-default) epenser.service
```
En théorie, à partir de là, le service est installé. Si on redémarre le système, le service se lancera au démarrage.
Seul problème : Impossible de l'arrêter.
TODO : Modifier le script pour qu'on puisse l'arrêter.
