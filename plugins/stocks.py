import plugins.pizzadatabase as db
import plugins.ai as ai
import plugins.points as points
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

TAX_RATE = 0.10

def generateTrend(current_price = 0, initial_price = 1000):
    roll = random.random() * 100 
    trend = 0
    if roll <= 1.5:    trend = random.uniform(-0.40, -0.30) # Crash
    elif roll <= 7:    trend = random.uniform(-0.20, -0.10) # Hard Dip
    elif roll <= 25:   trend = random.uniform(-0.08, -0.03) # Bear
    elif roll <= 75:   trend = random.uniform(-0.04, 0.04)  # STABLE (Balanced 0.0)
    elif roll <= 93:   trend = random.uniform(0.03, 0.08)  # Bull
    elif roll <= 98.5: trend = random.uniform(0.12, 0.20)  # Hype
    else:              trend = random.uniform(0.25, 0.40)  # Squeeze (Nerfed from 0.60)

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
    print(str(response))
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
            db.updateStockTrend(stock['name'],generateTrend())

#to check how much stock has changed in last X time
def informOnStocksUpdate():
    allStocks = list(db.retrieveAllStocks())
    msg = "Od ostatniego sprawdzenia: "
    if len(allStocks) > 0:
        for stock in allStocks:
            msg += "\n [" + str(stock['symbol']) + "] - "
            change = ((int(stock['lastPrice']) - int(stock['price'])) / int(stock['lastPrice']))
            abs_change = round(abs(change), 2)
            if int(stock['lastPrice']) < int(stock['price']):
                msg += "wzrost o " + str(abs_change) + "%! <:stonks:1470032691750637722>"
            elif int(stock['lastPrice']) > int(stock['price']):
                msg += "spadek o " + str(abs_change) + "%..<:notstonks:1470032747920756880>"
            else:
                msg += "bez zmian!"
            db.updateStocksLastPrice(stock['name'], stock['price'])
    return msg

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
            if newPrice < 50:
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
                db.updateStockPrice(stock['name'], newPrice)
    return bankrupts

def purchaseStocks(username, stocksymbol, amount):
    success = False
    user = db.retrieveUser('name', username)
    stock = db.retrieveStock('symbol', stocksymbol)
    if user and stock:
        userPoints = int(user['points'])
        if int(stock['shares']) >= amount:
            if userPoints >= int(stock['price'] * amount):
                db.updateStockShares(stock['name'], int(stock['shares']) - amount)
                cost = int(int(stock['price']) * int(amount))
                points.modifyPoints('name',user['name'], -1 * int(cost))
                info = "[Stocks] User " + str(user['name']) + " has purchased " + str(amount) + " shares of " + str(stock['name']) + " for " + str(cost) + "."
                print(info)
                db.updateStocksForUser('name',user['name'],stock['symbol'], amount)
                msg = str(user['name']) + " zakupil " + str(amount) + " akcjii " + str(stock['name']) + " za " + str(cost) + " ppkt."
                success = True
            else:
                msg = str(username) + " nie ma funduszy na zakup tylu akcji!\nTwoje punkty: " + str(userPoints) + "\nKoszt: " + str(int(stock['price'] * amount))
        else: 
            msg = str(stock['name']) + " nie ma tylu udzialow na rynku!\nTwoja proba: " + str(amount) + "\nDostepne udzialy: " + str(int(stock['shares']))
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
            db.updateStockShares(stock['name'], int(stock['shares']) + amount)
            returnMoney = int(int(int(stock['price']) * int(amount)) * (1 - TAX_RATE))
            points.modifyPoints('name',user['name'], int(returnMoney))
            db.removeStocksFromUser(user['name'],stock['symbol'], amount)
            msg = str(user['name']) + " sprzedaje " + str(amount) + " akcji " + str(stock['name']) + " za " + str(returnMoney) + " ppkt! (-10% podatku fur Deutschland)."
            success = True
        else: 
            msg = str(username) + " - nie masz tylu udzialow.\nTwoja proba: " + str(amount) + "\nUdzialy w Twoim posiadaniu: " + str(userShares)
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
            msg += "\n - [" + str(share['symbol']) + "] " + str(share['name']) + " - " + str(stockPrice) + "."
        msg += "\nTotal: " + str(returnMoney) + ". (10% tax was applied)"
        points.modifyPoints('name',user['name'], int(returnMoney))
        print(msg)
        success = True
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