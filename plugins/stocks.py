import plugins.pizzadatabase as db
import plugins.ai as ai
import json

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
            
#we do it once per month
def removeAllStocks():
    return ""

#simulate trends
def simulateTrends():
    return ""

#update according to trends
def updateAllStocks():
    return ""
