def init():
    global games
    global debug
    global reaction_messages
    global number_emojis
    global color
    global quest_emojis

    games = {}
    debug = False
    reaction_messages = []
    number_emojis = [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ,"🔟" ]
    color = 0xfff700
    quest_emojis = {"success": "☑️", "failure": "❎", "reverse": "🔄"}
