def init():
    global words
    global games
    global debug
    global color
    global reaction_messages
    global number_emojis
    global gamerules

    words = []
    with open("modules/codenames/words.txt", "r") as f:
        for line in f:
            words.extend(line.split())

    games = {}
    debug = False
    color = 0x880088
    reaction_messages = []
    number_emojis = [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ,"🔟" ]

    objectives = """
    Les joueurs sont répartis en deux équipes (Rouge et Bleue), avec un Spymaster au sein de chaque équipe.
    Chaque équipe doit deviner les mots (8 ou 9 mots selon l'équipe débutant la partie) qui lui appartiennent à l'aide des indices donnés par son Espion.
    La partie s'achève lorsqu'une équipe a deviné tous les mots ou si elle tombe sur le mot de l'Assassin.
    """

    gameprocess = """
    Le jeu se déroule au tour par tour, par équipe. Chaque tour se décompose en deux phases :

    :one: **Phase du Spymaster**

    Lors de cette phase, le Spymaster peut donner un indice qui est nécessairement de la forme `<mot> <chiffre>`, 
    le chiffre désignant le nombre de cartes liées au `<mot>`. 
    :warning: Tout indice ayant une proximité (homonymique, phonétique, sémantique) avec l'une des cartes est considéré comme invalide, 
    tout comme ceux se rapportant à la position ou au nombre de lettes d'une carte.
    :no_entry_sign: En cas d'invalidité, le tour est terminé et l'équipe adverse peut marquer un de ses mots.

    :two: **Phase de l'équipe**

    L'équipe doit, à partir de l'indice du Spymaster, choisir un mot sur la grille.
    Si celui-ci correspond bien, il est marqué et le tour continue : l'équipe peut 
    deviner un autre mot, à partir du même indice.
    :stop_sign: Toute erreur met fin au tour. 
    :dagger: Si le mot de l'Assassin est trouvé, l'équipe a immédiatement perdu.
    """

    gamerules = discord.Embed(title="Codenames - Règles du jeu", color=color)
    gamerules.add_field(name='Objectifs', value=objectives, inline=False)
    gamerules.add_field(name='Déroulement de la partie', value=gameprocess, inline=False)

