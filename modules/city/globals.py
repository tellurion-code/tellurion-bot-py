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
	tile_decorations = ["🌲", "🌳", "🌴", ":rock:"]
	player_colors = [0xff3333, 0x3388ff, 0x33ff33, 0x333333]
	unit_emojis = ["🧍", "🤺", "🏇"]
