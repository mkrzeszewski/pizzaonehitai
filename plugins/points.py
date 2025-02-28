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
    return modifyPoints('discord_id', discord_id, amount)

def modifyPoints(key, value, amount):
    user = db.retrieveUser(key, value)
    if user:
        newPoints = 0
        if (int(user['points']) + int(amount)) > 0:
            newPoints = int(user['points']) + int(amount)
        
        db.updateUser('discord_id', str(user['discord_id']), 'points', newPoints)
    return None

def fetchRandomUser():
    return random.choice(db.retrieveAllusers())

def generateDaily():
    winner = db.retrieveRandomUser()
    loser = db.retrieveRandomUser()
    while winner == loser:
        loser = db.retrieveRandomUser()

    #winner gets +10% +200
    addPoints(winner['discord_id'], int(int(winner['points']) * 0.1) + 200)

    #loser gets -200
    addPoints(loser['discord_id'], int(int(loser['points']) * 0.1) * -1)
    return winner, loser