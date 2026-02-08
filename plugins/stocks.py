import plugins.pizzadatabase as db
import plugins.ai as ai
import plugins.points as points
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

TAX_RATE = 0.10

def generateTrend(current_price, initial_price=1000):
    # 1. Start with the base random roll
    roll = random.random() * 100 
    
    # 2. Calculate the "Growth Ratio" (e.g., 2.0 means it doubled)
    ratio = current_price / initial_price if initial_price > 0 else 1
    
    # 3. Apply Bias
    # Low Price Protection (If price is near 50)
    if current_price < 150:
        roll += 4.0 #help for the wicked
    
    # High Price Resistance (If price is > 20x)
    elif ratio > 15:
        # If it's 20x, we subtract heavily from the roll
        # This drags the stock toward the 'Bear' and 'Stable' categories
        high_bias = (ratio - 15) * 4 
        roll -= high_bias

    # trend logic
    if roll <= 1.5:    trend = random.uniform(-0.40, -0.30)
    elif roll <= 7:    trend = random.uniform(-0.20, -0.10)
    elif roll <= 25:   trend = random.uniform(-0.08, -0.03)
    elif roll <= 75:   trend = random.uniform(-0.04, 0.04)
    elif roll <= 93:   trend = random.uniform(0.03, 0.08)
    elif roll <= 98.5: trend = random.uniform(0.12, 0.20)
    else:              trend = random.uniform(0.25, 0.40)

    # 5. The "Safety Net" Hard Cap
    # If it's already at 50x, we force a small increase if it happens to somehow stil lrise trend to prevent 100x+
    if ratio > 50 and trend > 0:
        return round(random.uniform(0.01, 0.04), 3)

    return round(trend, 3)

#we do it once per month
def generateStocks():
    users = db.retrieveAllUsers()
    userList = []
    for user in users:
        userList.append(user['name'])
    response = ai.generateStocks(userList)
    json_response = response.strip().lstrip('```json\n').rstrip('```')
    initiateStocksDB(json_response)

    #debug
    print("[STOCKS] " + str(response))
    return str(response)

def initiateStocksDB(json_stocks):
    users = db.retrieveAllUsers()
    currentShares = list(db.retrieveAllStocks())
    if users:
        for user in users:
            cashout(user['name'])

    if(len(currentShares) > 0):
        for share in currentShares:
            db.insertStockHistory(share)

    db.removeAllStocks()
    if json_stocks:
        json_stocks = json.loads(json_stocks)
        for stock in json_stocks:
            db.insertStock(stock['name'], stock['ceo'], stock['symbol'])
    simulateTrends()

#we do it once per month
def removeAllStocks():
    currentShares = list(db.retrieveAllStocks())
    if(len(currentShares)> 0):
        for share in currentShares:
            db.insertStockHistory(share)
            
    db.removeAllStocks()
    return ""

#simulate trends
def simulateTrends():
    allStocks = db.retrieveAllStocks()
    if allStocks:
        for stock in allStocks:
            db.updateStockTrend(stock['name'],generateTrend(int(stock['price'])))

#to check how much stock has changed in last X time
def informOnStocksUpdate():
    allStocks = list(db.retrieveAllStocks())
    msg = "Od ostatniego sprawdzenia: "
    if len(allStocks) > 0:
        for stock in allStocks:
            change = ((int(stock['lastPrice']) - int(stock['price'])) / int(stock['lastPrice']))
            abs_change = round(abs(change) * 100, 2) 
            if int(stock['lastPrice']) < int(stock['price']):
                msg += "\n<:stonks:1470032691750637722> [" + str(stock['symbol']) + "] - wzrost o " + str(int(abs_change)) + "%"
            elif int(stock['lastPrice']) > int(stock['price']):
                msg += "\n<:notstonks:1470032747920756880> [" + str(stock['symbol']) + "] - spadek o " + str(int(abs_change)) + "%"
            else:
                msg += "\n [" + str(stock['symbol']) + "] - bez zmian!"
            db.updateStocksLastPrice(stock['name'], stock['price'])
    return msg

#dillude stock
def stockSplit(stock):
    users = db.retrieveAllUsers()
    newPrice = stock['price'] // 10
    newShares = stock['availableShares'] * 10
    newLastPrice = stock['lastPrice'] // 10
    db.updateStock('name',stock['name'],'availableShares', int(newShares))
    db.updateStock('name',stock['name'],'price', int(newPrice))
    db.updateStock('name',stock['name'],'lastPrice', int(newLastPrice))
    db.updateStock('name',stock['name'],'totalShares', (int(stock['totalShares']) * 10))
    for user in users:
            if user['stocksOwned']:
                for share in user['stocksOwned']:
                    if share['symbol'] == stock['symbol']:
                        db.updateStocksForUser('name',user['name'],stock['symbol'], int(share['amount'] * 9))
                        break
#consolidate stock
def stockConsolidation(stock):
    users = db.retrieveAllUsers()
    newPrice = stock['price'] * 10
    newShares = stock['availableShares'] // 10
    newLastPrice = stock['lastPrice'] * 10
    db.updateStock('name',stock['name'],'availableShares', int(newShares))
    db.updateStock('name',stock['name'],'price', int(newPrice))
    db.updateStock('name',stock['name'],'lastPrice', int(newLastPrice))
    db.updateStock('name',stock['name'],'totalShares', (int(stock['totalShares']) / 10))
    for user in users:
            if user['stocksOwned']:
                for share in user['stocksOwned']:
                    if share['symbol'] == stock['symbol']:
                        reduction = -(int(share['amount'] * 0.9))
                        db.updateStocksForUser('name',user['name'],stock['symbol'], reduction)
                        break


#update according to price
def updatePrices():
    allStocks = db.retrieveAllStocks()
    bankrupts = []
    if allStocks:
        for stock in allStocks:
            trend = float(stock['trend'])
            noiseMultiplier = random.uniform(0.85, 1.15)
            trend = trend * noiseMultiplier
            newPrice = int(trend * float(int(stock['price']))) + int(stock['price'])
            db.updateStockPrice(stock['name'], newPrice)
            if newPrice < 50:
                if stock['totalShares'] == 100:
                    users = db.retrieveAllUsers()
                    badInvestors = []
                    for user in users:
                        if user['stocksOwned']:
                            for share in user['stocksOwned']:
                                if share['symbol'] == stock['symbol']:
                                    badInvestors.append(user['name'])
                                    db.removeStocksFromUser(user['name'],share['symbol'], share['amount'])
                                    break
                    db.removeStock(stock['name'])
                    print("[STOCKS] " + str(stock['name'] + " has filed for bankrupcy."))
                    bankrupts.append([stock, badInvestors])
                else:
                    stockConsolidation(stock)
                    print("[STOCKS] " + str(stock['name']) + " has been consolidated!")
            else:
                if newPrice >= 100000:
                    stockSplit(stock) #we add more shares to market but lower the price
                    print("[STOCKS] " + str(stock['name']) + " has been dilluded!")
    return bankrupts

def purchaseStocks(username, stocksymbol, amount):
    success = False
    msg = ""
    user = db.retrieveUser('name', username)
    stock = db.retrieveStock('symbol', stocksymbol)
    if user and stock:
        userPoints = int(user['points'])
        if int(stock['availableShares']) >= amount:
            if userPoints >= int(stock['price'] * amount):
                db.updateStockShares(stock['name'], int(stock['availableShares']) - amount)
                cost = int(int(stock['price']) * int(amount))
                points.modifyPoints('name',user['name'], -1 * int(cost))
                db.updateStocksForUser('name',user['name'],stock['symbol'], amount)
                msg = str(user['name']) + " zakupil " + str(amount) + " akcjii " + str(stock['name']) + " za " + str(cost) + " ppkt."
                print("[STOCKS] " + str(msg))
                success = True
            else:
                msg = str(username) + " - nie masz funduszy na zakup tylu akcji!\nTwoje punkty: " + str(userPoints) + "\nKoszt: " + str(int(stock['price'] * amount))
        else: 
            msg = str(stock['name']) + " - nie ma tylu udzialow na rynku!\nTwoja proba: " + str(amount) + "\nDostepne udzialy: " + str(int(stock['availableShares']))
        return success, msg
    msg = "User " + str(username) + " or stock " + str(stocksymbol) + " not found."
    return success, msg

def sellStocks(username, stocksymbol, amount):
    success = False
    msg = ""
    user = db.retrieveUser('name', username)
    stock = db.retrieveStock('symbol', stocksymbol)
    userShares = 0
    if user and stock:
        for s in user['stocksOwned']:
            if s['symbol'] == stocksymbol:
                userShares = s['amount']
                break
        if userShares >= amount:
            db.updateStockShares(stock['name'], int(stock['availableShares']) + amount)
            returnMoney = int(int(int(stock['price']) * int(amount)) * (1 - TAX_RATE))
            points.modifyPoints('name',user['name'], int(returnMoney))
            db.removeStocksFromUser(user['name'],stock['symbol'], amount)
            msg = str(user['name']) + " sprzedaje " + str(amount) + " akcji " + str(stock['name']) + " za " + str(returnMoney) + " ppkt! (-10% podatku fur Deutschland)."
            success = True
        else: 
            msg = str(username) + " - nie masz tylu udzialow.\nTwoja proba: " + str(amount) + "\nUdzialy w Twoim posiadaniu: " + str(userShares)
    else:
        msg = "User " + str(username) + " or stock " + str(stocksymbol) + " not found."
    return success, msg

def cashout(username):
    success = False
    user = db.retrieveUser('name', username)
    returnMoney = 0
    msg = ""
    if user['stocksOwned']:
        msg = str(user['name']) + " sprzedaje: "
        for share in user['stocksOwned']:
            stock = db.retrieveStock('symbol',share['symbol'])
            stockPrice = int(int(int(stock['price']) * int(share['amount'])) * (1 - TAX_RATE))
            returnMoney += stockPrice
            db.removeStocksFromUser(user['name'],share['symbol'], share['amount'])
            msg += "\n - [" + str(share['symbol']) + "] - " + str(stockPrice) + "."
        msg += "\nTotal: " + str(returnMoney) + ". (10% tax was applied)"
        points.modifyPoints('name',user['name'], int(returnMoney))
        print("[STOCKS] " + msg)
        success = True
    else:
        msg = "User " + str(user['name']) + " doesn't have any shares."
    return success, msg

def generateGraph():
    stocksData = db.retrieveAllStocks()
    width, height = 1000, 500
    margin = 40
    img = Image.new("RGB", (width, height), (30, 30, 30)) # Dark background
    draw = ImageDraw.Draw(img)

    # 1. Find Global Min/Max to scale the Y-axis
    allPrices = []
    for stock in stocksData:
        for price in stocksData['priceHistory']:
            allPrices.append(price)
    if not allPrices: return None
    
    g_min, g_max = 0, max(allPrices) + 50
    price_range = g_max - g_min if g_max != g_min else 1

    # 2. Find Max History Length to scale the X-axis
    max_points = max(len(s['priceHistory']) for s in stocksData)
    x_step = (width - 2 * margin) / (max_points - 1) if max_points > 1 else 0

    # 3. Draw each stock line
    for stock in stocksData:
        history = stock['priceHistory']
        if len(history) < 2: continue
        line_points = []
        for i, price in enumerate(history):
            # Calculate X (horizontal)
            x = margin + (i * x_step)
            
            # Calculate Y (vertical) - Inverse because 0,0 is Top-Left in PIL
            # We map price to 0-1 range, then scale to height
            normalized_y = (price - g_min) / price_range
            y = (height - margin) - (normalized_y * (height - 2 * margin))
            
            line_points.append((x, y))

        # Draw the line
        color = stock.get('color', (random.randint(100, 255), 
                                    random.randint(100, 255), 
                                    random.randint(100, 255)))
        draw.line(line_points, fill=color, width=3, joint="curve")

    # 4. (Optional) Draw a border or grid
    draw.rectangle([margin, margin, width-margin, height-margin], outline=(100, 100, 100))
    
    return img