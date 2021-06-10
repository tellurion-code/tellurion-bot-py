def init():
    global words
    global games
    global debug
    global color

    words = []
    with open("modules/codenames/words.txt", "r") as f:
        for line in f:
            words.extend(line.split())

    games = {}
    debug = False
    color = 0x880088
