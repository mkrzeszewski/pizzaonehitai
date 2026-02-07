import plugins.pizzadatabase as db
import plugins.ai as ai

#we do it once per month
def generateStocks():
    db.removeAllStocks()
    users = db.retrieveAllUsers()
    userList = []
    for user in users:
        userList.append(user['name'])
    print(ai.generateStocks(userList))

#we do it once per month
def removeAllStocks():
    return ""

#simulate trends
def simulateTrends():
    return ""

#update according to trends
def updateAllStocks():
    return ""
