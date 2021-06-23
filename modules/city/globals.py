def init():
	global games
	global debug
	global color
	global tile_colors
	global tile_decorations
	global player_colors
	global unit_emojis

	games = {}
	debug = False
	color = 0xcc00ff
	tile_colors = ["🟥", "🟦", "🟩", "⬛"]
	tile_decorations = ["🌲", "🌳"]
	player_colors = [0xff3333, 0x3388ff, 0x33ff33, 0x333333]
	unit_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
