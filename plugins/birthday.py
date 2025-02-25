from pymongo import MongoClient
from datetime import datetime
from os import environ

def getBirthdayPeople():
    #connect to mongodb database and get proper database
    CONN_URL = "mongodb://" + environ["MONGO_USERNAME"] + ":" + environ["MONGO_PASSWORD"] + "@" + environ["MONGO_ENDPOINT"]
    client = MongoClient(CONN_URL)
    db = client['discord']
    collection = db['users']

    #get todays date - format it accordingly to <MONTH>-<DAY> - 31st of January would be 1-31
    current_time = datetime.now()

    #query for it in mongodb
    birthday_query = { "birthday": str(current_time.month) + "-" + str(current_time.day) }
    query_result = collection.find(birthday_query)

    #if it exists; return list, else return None
    if query_result:
        return list(query_result)
    else:
        return None