import plugins.pizzadatabase as db
import plugins.points as points
import re
import time

ADMIN_ID = 326259887007072257
MIN_BET_AMOUNT = 10

def parseQuotedArgs(message):
    """Parse quoted arguments from a message, e.g. "Kto wygra?" "Polska" "Niemcy" """
    return re.findall(r'"([^"]*)"', message)

def createBet(creator_discord_id, creator_name, title, options_list):
    if len(options_list) < 2:
        return None, "Musisz podac co najmniej 2 opcje w cudzyslowach!"
    
    if len(title.strip()) == 0:
        return None, "Tytul zakladu nie moze byc pusty!"

    options = []
    for i, label in enumerate(options_list):
        options.append({
            "key": i + 1,
            "label": label,
            "bets": [],
            "pool": 0
        })

    bet_id = db.getBetCount()
    bet_data = {
        "bet_id": bet_id,
        "creator_discord_id": str(creator_discord_id),
        "creator_name": creator_name,
        "title": title,
        "options": options,
        "status": "open",
        "winner_key": None,
        "total_pool": 0,
        "created_at": str(time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
    }

    db.insertBet(bet_data)
    return bet_data, None

def placeBet(discord_id, username, bet_id, option_key, amount):
    bet = db.retrieveBet(bet_id)
    if not bet:
        return None, "Zaklad #" + str(bet_id) + " nie istnieje!"
    
    if bet['status'] != "open":
        return None, "Zaklad #" + str(bet_id) + " jest juz zamkniety!"

    if amount < MIN_BET_AMOUNT:
        return None, "Minimalna kwota zakladu to " + str(MIN_BET_AMOUNT) + " ppkt!"

    user = db.retrieveUser('discord_id', str(discord_id))
    if not user:
        return None, "Nie znaleziono uzytkownika w bazie!"

    if int(user['points']) < amount:
        return None, "Nie masz wystarczajaco punktow! Posiadasz: " + str(user['points']) + " ppkt."

    # check if option exists
    valid_option = False
    for opt in bet['options']:
        if int(opt['key']) == int(option_key):
            valid_option = True
            break
    
    if not valid_option:
        return None, "Opcja " + str(option_key) + " nie istnieje w zakladzie #" + str(bet_id) + "!"

    # check if user already bet on a different option
    for opt in bet['options']:
        if int(opt['key']) != int(option_key):
            for b in opt['bets']:
                if str(b['discord_id']) == str(discord_id):
                    return None, "Juz obstawiles opcje \"" + str(opt['label']) + "\" w tym zakladzie! Nie mozesz obstawiac roznych opcji."

    # deduct points and place bet
    points.addPoints(str(discord_id), -1 * amount)
    db.appendBetOption(bet_id, int(option_key), str(discord_id), username, amount)

    updated_bet = db.retrieveBet(bet_id)
    return updated_bet, None

def resolveBet(discord_id, bet_id, winner_key):
    bet = db.retrieveBet(bet_id)
    if not bet:
        return None, None, "Zaklad #" + str(bet_id) + " nie istnieje!"
    
    if bet['status'] != "open":
        return None, None, "Zaklad #" + str(bet_id) + " jest juz zamkniety!"

    if str(bet['creator_discord_id']) != str(discord_id):
        return None, None, "Tylko tworca zakladu moze go rozstrzygnac!"

    # check if option exists
    winning_option = None
    for opt in bet['options']:
        if int(opt['key']) == int(winner_key):
            winning_option = opt
            break
    
    if not winning_option:
        return None, None, "Opcja " + str(winner_key) + " nie istnieje w zakladzie #" + str(bet_id) + "!"

    total_pool = int(bet['total_pool'])
    winning_pool = int(winning_option['pool'])

    # calculate payouts
    winners = []
    if winning_pool > 0 and total_pool > 0:
        for b in winning_option['bets']:
            payout = int(int(b['amount']) / winning_pool * total_pool)
            points.addPoints(str(b['discord_id']), payout)
            winners.append({
                "name": b['name'],
                "discord_id": b['discord_id'],
                "bet_amount": b['amount'],
                "payout": payout
            })
    elif winning_pool == 0 and total_pool > 0:
        # no one bet on the winning option - return points to all participants
        for opt in bet['options']:
            for b in opt['bets']:
                points.addPoints(str(b['discord_id']), int(b['amount']))

    db.updateBetWinner(bet_id, int(winner_key))
    db.updateBetStatus(bet_id, "resolved")

    resolved_bet = db.retrieveBet(bet_id)
    return resolved_bet, winners, None

def cancelBet(discord_id, bet_id):
    bet = db.retrieveBet(bet_id)
    if not bet:
        return None, "Zaklad #" + str(bet_id) + " nie istnieje!"
    
    if bet['status'] != "open":
        return None, "Zaklad #" + str(bet_id) + " jest juz zamkniety!"

    # only creator or admin can cancel
    if str(bet['creator_discord_id']) != str(discord_id) and int(discord_id) != ADMIN_ID:
        return None, "Tylko tworca zakladu (lub admin) moze go anulowac!"

    # return all points to participants
    for opt in bet['options']:
        for b in opt['bets']:
            points.addPoints(str(b['discord_id']), int(b['amount']))

    db.updateBetStatus(bet_id, "cancelled")

    cancelled_bet = db.retrieveBet(bet_id)
    return cancelled_bet, None

def getActiveBets():
    return list(db.retrieveActiveBets())

def getBetInfo(bet_id):
    return db.retrieveBet(bet_id)

def getUserBets(discord_id):
    active_bets = list(db.retrieveActiveBets())
    user_bets = []
    for bet in active_bets:
        for opt in bet['options']:
            for b in opt['bets']:
                if str(b['discord_id']) == str(discord_id):
                    user_bets.append({
                        "bet": bet,
                        "option_label": opt['label'],
                        "option_key": opt['key'],
                        "amount": b['amount']
                    })
                    break
    return user_bets

def calculatePotentialWinnings(discord_id, bet_id):
    bet = db.retrieveBet(bet_id)
    if not bet:
        return None, None, "Zaklad #" + str(bet_id) + " nie istnieje!"
    
    if bet['status'] != "open":
        return None, None, "Zaklad #" + str(bet_id) + " jest juz zamkniety!"

    total_pool = int(bet['total_pool'])
    user_option = None
    user_amount = 0

    for opt in bet['options']:
        for b in opt['bets']:
            if str(b['discord_id']) == str(discord_id):
                user_option = opt
                user_amount = int(b['amount'])
                break
        if user_option:
            break

    if not user_option:
        return None, None, "Nie obstawiles jeszcze w zakladzie #" + str(bet_id) + "!"

    option_pool = int(user_option['pool'])
    potential_payout = 0
    if option_pool > 0:
        potential_payout = int(user_amount / option_pool * total_pool)
    profit = potential_payout - user_amount

    result = {
        "bet": bet,
        "user_option_label": user_option['label'],
        "user_option_key": user_option['key'],
        "user_amount": user_amount,
        "option_pool": option_pool,
        "total_pool": total_pool,
        "potential_payout": potential_payout,
        "profit": profit
    }
    return result, bet, None
