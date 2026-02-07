import plugins.pizzadatabase as db
import plugins.ai as ai

#we do it once per month
def generateStocks():
    db.removeAllStocks()
    users = db.retrieveAllUsers()
    userList = []
    for user in users:
        userList.append(user['name'])
    response = ai.generateStocks(userList)
    print(str(response))
    return str(response)

#we do it once per month
def removeAllStocks():
    return ""

#simulate trends
def simulateTrends():
    return ""

#update according to trends
def updateAllStocks():
    return ""
