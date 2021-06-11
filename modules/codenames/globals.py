def init():
    global words
    global games
    global debug
    global color
    global reaction_messages
    global number_emojis
    global gamerules

    words = []
    with open("modules/codenames/words.txt", "r", encoding='utf-8') as f:
        for line in f:
            words.extend(line.split())

    games = {}
    debug = False
    color = 0x880088
    reaction_messages = []
    number_emojis = [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ,"🔟" ]

