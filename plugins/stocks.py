import plugins.pizzadatabase as db
import plugins.ai as ai
import plugins.points as points
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

TAX_RATE = 0.10

def generateTrend():
    roll = random.random() * 100 
    trend = 0
    if roll <= 1:    trend = random.uniform(-0.50, -0.40) # 1% - THE BLACK SWAN (Total devastation)
    elif roll <= 5:  trend = random.uniform(-0.30, -0.15) # 4% - BUMMER WEEK (Hard dip)
    elif roll <= 20: trend = random.uniform(-0.12, -0.05) # 15% - BEARISH (Consistent sell-off)
    elif roll <= 80: trend = random.uniform(-0.02, 0.03) # 60% - STABLE (The "Normal" Day) 
    elif roll <= 95: trend = random.uniform(0.05, 0.12) # 15% - BULLISH (Good news!)   
    elif roll <= 99: trend = random.uniform(0.20, 0.35) # 4% - TO THE MOON (Huge hype)  
    else:            trend = random.uniform(0.45, 0.60) # 1% - THE BIG SQUEEZE (God-tier gains)

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
    if users:
        for user in users:
            cashout(user['name'])
    db.removeAllStocks()
    if json_stocks:
        json_stocks = json.loads(json_stocks)
        for stock in json_stocks:
            db.insertStock(stock['name'], stock['ceo'], stock['symbol'])
    simulateTrends()

#we do it once per month
def removeAllStocks():
    return ""

#simulate trends
def simulateTrends():
    allStocks = db.retrieveAllStocks()
    if allStocks:
        for stock in allStocks:
            db.updateStockTrend(stock['name'],generateTrend())

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
                for user in users:
                    if user['stocksOwned']:
                        for share in user['stocksOwned']:
                            if share['symbol'] == stock['symbol']:
                                db.removeStocksFromUser(user['name'],share['symbol'], share['amount'])
                                break
                db.removeStock(stock['name'])
                print("[STOCKS] " + str(stock['name'] + " has filed for bankrupcy."))
                bankrupts.append(stock)
            else:
                db.updateStockPrice(stock['name'], newPrice)
    return bankrupts

def purchaseStocks(username, stocksymbol, amount):
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
                return info
            else:
                return "User " + str(username) + " doesnt have funds to purchase that many stock.\n" + str(userPoints) + "/" + str(int(stock['price'] * amount))
        else: 
            return "Stock " + str(stock['name']) + " doesnt have enough shares on the market.\n" + str(amount) + "/" + str(int(stock['shares']))
    return "User " + str(username) + " or stock " + str(stocksymbol) + " not found."

def sellStocks(username, stocksymbol, amount):
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
            info = "[Stocks] User " + str(user['name']) + " has sold " + str(amount) + " shares of " + str(stock['name']) + " for " + str(returnMoney) + " (10% tax was applied)."
            print(info)
            db.removeStocksFromUser(user['name'],stock['symbol'], amount)
        else: 
            return "User " + str(username) + " doesnt have enough shares.\n" + str(amount) + "/" + str(userShares)
    return "User " + str(username) + " or stock " + str(stocksymbol) + " not found."

def cashout(username):
    user = db.retrieveUser('name', username)
    returnMoney = 0
    if user['stocksOwned']:
        for share in user['stocksOwned']:
            stock = db.retrieveStock('symbol',share['symbol'])
            returnMoney += int(int(int(stock['price']) * int(share['amount'])) * (1 - TAX_RATE))
            db.removeStocksFromUser(user['name'],share['symbol'], share['amount'])
        points.modifyPoints('name',user['name'], int(returnMoney))
        info = "[Stocks] User " + str(user['name']) + " has sold all their shares for " + str(returnMoney) + " (10% tax was applied)."
        print(info)
        return info
    else:
        return "User " + str(user['name']) + " doesn't have any shares."

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