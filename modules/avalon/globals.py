import discord

def init():
	global games
	global debug
	global color
	global number_emojis
	global vote_choices
	global quest_choices
	global visual_roles

	games = {}
	debug = False
	color = 0xfff700
	number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
	vote_choices = {
		"names": {"for": "Pour", "against": "Contre"},
		"emojis": {"for": "✅", "against": "❌"},
		"styles": {"for": discord.ButtonStyle.green, "against": discord.ButtonStyle.red},
	}
	quest_choices = {
		"names": {"success": "Réussite", "failure": "Echec", "reverse": "Inversion", "cancel": "Annulation", "sabotage": "Sabotage"},
		"emojis": {"success": "✅", "failure": "❌", "reverse": "🔄", "cancel": "🚫", "sabotage": "‼️"},
		"styles": {"success": discord.ButtonStyle.green, "failure": discord.ButtonStyle.red, "reverse": discord.ButtonStyle.blurple, "cancel": discord.ButtonStyle.gray, "sabotage": discord.ButtonStyle.red},
		"colors": {"success": 0x00ff00, "failure": 0xff0000, "reverse": 0x0000ff, "cancel": 0x00ff55, "sabotage": 0xff5500}
	}
	visual_roles = {
		"good": "🟦 Gentil",
		"merlin": "🧙‍♂️ Merlin",
		"percival": "🤴 Perceval",
		"karadoc": "🥴 Karadoc",
		"gawain": "🛡️ Gauvain",
		"galaad": "🙋 Galaad",
		"uther": "👨‍🦳 Uther",
		"arthur": "👑 Arthur",
		"vortigern": "👴 Vortigern",

		"evil": "🟥 Méchant",
		"assassin": "🗡️ Assassin",
		"morgane": "🧙‍♀️ Morgane",
		"mordred": "😈 Mordred",
		"oberon": "😶 Oberon",
		"lancelot": "⚔️ Lancelot",
		"accolon": "🤘 Accolon",
		"kay": "🧐 Sir Kay",
		"agravain": "🔮 Agravain",

		"elias": "🧙 Elias"
	}
