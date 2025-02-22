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

def retrieveAllusers():
    user_collection = db['users']
    users = user_collection.find({})
    if users:
        return users
    return None

def retrieveAllUsersSorted(key):
    user_collection = db['users']
    users = user_collection.find({}).sort({key: 1})
    if users:
        return users
    return None

def retrieveAllUsersRevSorted(key):
    user_collection = db['users']
    users = user_collection.find({}).sort({key: -1})
    if users:
        return users
    return None

def updateUser(discord_id, key, value):
    user_collection = db['users']
    user = user_collection.find_one({'discord_id': str(discord_id)})
    result = user_collection.update_one(
    {"discord_id": discord_id},  # Match the document where 'id' equals the specified user ID
    {"$set": {key: value}}  # Set the new points value
    )
    text = ""

    print("[INFO] DB MODIFY: {" + str(discord_id) + " - " + str(key) + " = " + str(value) + "} - result: " + str(result))
    if result.matched_count > 0:
        text = "Zaktualizowano pole " + str(key) + " dla uzytkownika: " + str(user['name']) + "."
    else:
        text = "User not found."

    return text