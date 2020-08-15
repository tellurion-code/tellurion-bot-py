def init():
    global games
    global debug
    global number_emojis
    global choice_emojis
    global direction_emojis
    global color
    global tile_colors
    global player_colors
    global kill_phrases
    global dir_x
    global dir_y

    games = {}
    debug = False
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    choice_emojis = ["↪️", "↩️", "🔼", "🔽", "⏪", "⏩", "💥", "❌", "✅"]
    direction_emojis = ["▶️", "🔼", "◀️", "🔽"]
    color = 0x4B5320
    tile_colors = ["⬛", "🟫", "⬜"]
    player_colors = ["🟥", "🟦", "🟩", "🟨", "🟪", "🟧"]
    kill_phrases = [
        "{} a été explosé par {}",
        "{} était sur le chemin de {}",
        "{} a été brain par {}",
        "{} a rencontré le tir de {}",
        "{} n'a pas réussi à esquiver {}",
        "{} a été détruit par {}",
        "{} a été dominé par {}",
        "{} a été Petri-fié par {}",
        "{} ne sait pas aussi bien manoeuvrer son tank que {}"
    ]
    dir_x = [1, 0, -1, 0]
    dir_y = [0, -1, 0, 1]
