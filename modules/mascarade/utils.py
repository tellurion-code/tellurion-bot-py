def display_money(money):
    if money == 0:
        return "🚫"

    bags, coins = 0, money
    while coins >= 5:
        bags += 1
        coins -= 5

    return "💰" * bags + "🟡" * coins
