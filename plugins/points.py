import plugins.pizzadatabase as db
import random

def getTop(howMany = 5):    
    users = db.retrieveAllUsersRevSorted('points')
    if users:
        increment = 1
        returnUsers = []
        for user in users:
            if increment == howMany + 1:
                return returnUsers
            
            returnUsers.append(user)
            increment = increment + 1
        return returnUsers
    return None

def addPoints(discord_id, amount):
    user = db.retrieveUser('discord_id', discord_id)
    if user:
        db.updateUser('discord_id', str(discord_id), 'points', int(user['points']) + amount)
        #print("[INFO] Adding " + str(amount) + " points to: " +  user['name'] + ".")
    return None

def modifyPoints(key, value, amount):
    user = db.retrieveUser(key, value)
    if user:
        newPoints = 0
        if (int(user['points']) + int(amount)) > 0:
            newPoints = int(user['points']) + int(amount)
        
        operation = "+"
        if(int(amount) < 0):
            operation = "-"
        db.updateUser('discord_id', str(user['discord_id']), 'points', newPoints)
        #print("[INFO] Modifying: " + operation + str(amount) + " points for: " +  user['name'] + ".")
    return None

def fetchRandomUser():
    return random.choice(db.retrieveAllusers())

def generateDaily():
    winner = fetchRandomUser()
    loser = fetchRandomUser()
    while winner == loser:
        loser = fetchRandomUser()

    #winner gets +10% +200
    addPoints(winner['discord_id'], int(int(winner['points']) * 0.1) + 200)

    #loser gets -200
    addPoints(loser['discord_id'], -200)
    return winner, loser