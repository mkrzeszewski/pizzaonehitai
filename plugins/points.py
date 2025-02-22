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