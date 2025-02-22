from pymongo import MongoClient
from os import environ

#connect to mongodb database and get proper database
CONN_URL = "mongodb://" + environ["MONGO_USERNAME"] + ":" + environ["MONGO_PASSWORD"] + "@" + environ["MONGO_ENDPOINT"]
dbclient = MongoClient(CONN_URL)
db = dbclient['discord']

def retrieveUser(key, value):
    user_collection = db['users']
    user = user_collection.find_one({key: value})
    if user:
        return user
    return None