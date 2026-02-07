import plugins.pizzadatabase as db
import plugins.ai as ai
import json
import random
import numpy as np
from PIL import Image, ImageDraw
import io

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
    db.removeAllStocks()
    if json_stocks:
        json_stocks = json.loads(json_stocks)
        for stock in json_stocks:
            db.insertStock(stock['name'], stock['symbol'], 100, 1000)
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
                db.removeStock(stock['name'])
                print("[STOCKS] " + str(stock['name'] + " has filed for bankrupcy."))
            else:
                db.updateStockPrice(stock['name'], newPrice)

def generateGraph():
    return ""

