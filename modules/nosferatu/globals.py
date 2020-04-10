def init():
    global games
    global reaction_messages
    global number_emojis
    global ritual_names
    global clock_faces
    global card_names
    global debug

    games = {}
    reaction_messages = []
    number_emojis = [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ,"🔟" ]
    ritual_names = {
        "mirror": "🔮 Miroir d'Argent",
        "transfusion": "💉 Transfusion Sanguine",
        "distortion": "🕰️ Distortion Temporelle",
        "water": "🧴 Eau Bénite"
    }
    clock_faces = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛", "🕜", "🕝", "🕞", "🕟", "🕠", "🕡", "🕢", "🕣", "🕤", "🕥", "🕦", "🕧"]
    card_names = {
        "bite": "🧛 Morsure",
        "spell": "📖 Incantation",
        "journal": "🧾 Journal",
        "night": "🌃 Nuit",
        "none": "❌ Manquante"
    }
    debug = False
