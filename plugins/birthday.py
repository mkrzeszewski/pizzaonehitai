from pymongo import MongoClient
from datetime import datetime
from os import environ
import plugins.pizzadatabase as db

def getBirthdayPeople():
    #connect to mongodb database and get proper database
    

    #get todays date - format it accordingly to <MONTH>-<DAY> - 31st of January would be 1-31
    current_time = datetime.now()

    #query for it in mongodb
    birthday_query = { "birthday": str(current_time.month) + "-" + str(current_time.day) }
    users = db.retrieveUsers(birthday_query)

    #if it exists; return list, else return None
    birthdayBoys = []
    if users:
        for user in users:
            birthdayBoys.append(user)
    else:
        return None
    return birthdayBoys