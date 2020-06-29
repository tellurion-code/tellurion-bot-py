def init():
    global games
    global debug
    global reaction_messages
    global number_emojis
    global color
    global quest_emojis
    global visual_roles

    games = {}
    debug = False
    reaction_messages = []
    number_emojis = [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ,"🔟" ]
    color = 0xfff700
    quest_emojis = {"success": "✅", "failure": "❌", "reverse": "🔄"}
    visual_roles = {
        "good": "🟦 Gentil",
        "evil": "🟥 Méchant",
        "merlin": "🧙‍♂️ Merlin",
        "percival": "🤴 Perceval",
        "lancelot": "🛡️ Lancelot",
        "karadoc": "🥴 Karadoc",
        "galaad": "🙋 Galaad",
        "uther": "👨‍🦳 Uther",
        "assassin": "🗡️ Assassin",
        "morgane": "🧙‍♀️ Morgane",
        "mordred": "😈 Mordred",
        "oberon": "😶 Oberon",
        "agrav1": "⚔️ Agravain",
        "agrav2": "⚔️ Agravain"
    }
