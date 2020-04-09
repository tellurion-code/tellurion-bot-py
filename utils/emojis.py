NUMBERS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

THUMBS_UP = "👍"
THUMBS_DOWN = "👎"
WHITE_CHECK_MARK = "✅"


def write_with_number(i):
    raw = str(i)
    s = ""
    for c in str(i):
        if raw == ".":
            s += "."
        else:
            s += NUMBERS[int(c)]
    return s
