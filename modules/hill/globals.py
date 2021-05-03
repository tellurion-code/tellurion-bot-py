def init():
	global games
	global debug
	global number_emojis
	global choice_emojis
	global color
	global tile_colors
	global player_colors
	global victory_symbols

	games = {}
	debug = False
	number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
	choice_emojis = ["⬅️", "⬆️", "⬇️", "➡️", "🦸"]
	color = 0xa4cd32
	tile_colors = ["⬜", "⬛", "🟥", "🟦", "🟩", "🟨", "🟪", "🟧"]
	player_colors = [0xff3333, 0x3388ff, 0x33ff33, 0xffff33, 0xb366ff, 0xff8000]
	victory_symbols = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠"]
