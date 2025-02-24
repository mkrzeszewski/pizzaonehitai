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