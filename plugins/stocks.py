import plugins.pizzadatabase as db
import plugins.ai as ai
import json
import random
import numpy as np

def generateTrend():
    roll = random.random() * 100 
    if roll <= 1:    return random.uniform(-0.50, -0.40) # 1% - THE BLACK SWAN (Total devastation)
    if roll <= 5:    return random.uniform(-0.30, -0.15) # 4% - BUMMER WEEK (Hard dip)
    if roll <= 20:   return random.uniform(-0.12, -0.05) # 15% - BEARISH (Consistent sell-off)
    if roll <= 80:   return random.uniform(-0.02, 0.03)  # 60% - STABLE (The "Normal" Day)
    if roll <= 95:   return random.uniform(0.05, 0.12)  # 15% - BULLISH (Good news!) 
    if roll <= 99:   return random.uniform(0.20, 0.35)   # 4% - TO THE MOON (Huge hype)
    else:            return random.uniform(0.45, 0.60)# 1% - THE BIG SQUEEZE (God-tier gains)

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
    db.removeAllStocks()
    if json_stocks:
        json_stocks = json.loads(json_stocks)
        for stock in json_stocks:
            db.insertStock(stock['name'], stock['symbol'], 100, 10000)
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
    if allStocks:
        for stock in allStocks:
            newPrice = int(float(stock['trend'])*float(int(stock['price']))) + int(stock['price'])
            if newPrice < 50:
                db.removeStock(stock['name'])
                print("[STOCKS] " + str(stock['name'] + " has filed for bankrupcy."))
            else:
                db.updateStockPrice(stock['name'], newPrice)

