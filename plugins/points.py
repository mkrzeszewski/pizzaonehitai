import plugins.pizzadatabase as db

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
        db.updateUser(str(discord_id), 'points', int(user['points']) + amount)
        print("[INFO] Adding " + str(amount) + " points to: " +  user['name'] + ".")
    return None

def removePoints(discord_id, amount):
    user = db.retrieveUser('discord_id', discord_id)
    if user:
        newPoints = 0
        if (int(user['points']) - int(amount)) > 0:
            newPoints = int(user['points']) - int(amount)
        db.updateUser(str(discord_id), 'points', int(user['points']) + amount)
        print("[INFO] Removing " + str(amount) + " points from: " +  user['name'] + ".")
    return None