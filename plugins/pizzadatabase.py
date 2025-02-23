from pymongo import MongoClient
from os import environ

#connect to mongodb database and get proper database
CONN_URL = "mongodb://" + environ["MONGO_USERNAME"] + ":" + environ["MONGO_PASSWORD"] + "@" + environ["MONGO_ENDPOINT"]
dbclient = MongoClient(CONN_URL)
db = dbclient['discord']

def retrieveUser(key, value):
    userCollection = db['users']
    return userCollection.find_one({key: value})

def retrieveAllTFTMatches():
    matchesCollection = db['parsed_tft_matches']
    allMatches = matchesCollection.find({})
    return allMatches

def retrieveTFTMatch(match_id):
    matchesCollection = db['parsed_tft_matches']
    return matchesCollection.find_one({'riotid': match_id})

def insertTFTMatch(match_id):
    matchesCollection = db['parsed_tft_matches']
    matchesCollection.insert_one({"riotid": match_id})

def retrieveAllusers():
    userCollection = db['users']
    return userCollection.find({})

def retrieveAllUsersSorted(key):
    userCollection = db['users']
    return userCollection.find({}).sort({key: 1})

def retrieveAllUsersRevSorted(key):
    userCollection = db['users']
    return userCollection.find({}).sort({key: -1})

def updateDiscordUser(discord_id, key, value):
    userCollection = db['users']
    user = userCollection.find_one({'discord_id': str(discord_id)})
    result = userCollection.update_one(
    {"discord_id": discord_id},  # Match the document where 'id' equals the specified user ID
    {"$set": {key: value}}  # Set the new points value
    )
    text = ""

    print("[DBINFO] DB MODIFY: {" + str(discord_id) + " - " + str(key) + " = " + str(value) + "} - result: " + str(result))
    if result.matched_count > 0:
        text = "Zaktualizowano pole " + str(key) + " dla uzytkownika: " + str(user['name']) + "."
    else:
        text = "User not found."

    return text

def updateUser(querykey, queryvalue, key, value):
    userCollection = db['users']
    user = userCollection.find_one({querykey: queryvalue})
    result = userCollection.update_one(
    {querykey: queryvalue},
    {"$set": {key: value}}
    )
    text = ""
    print("[DBINFO] DB MODIFY: {" + str(user['name']) + " - " + str(key) + " = " + str(value) + "} - result: " + str(result))
    if result.matched_count > 0:
        text = "Zaktualizowano pole " + str(key) + " dla uzytkownika: " + str(user['name']) + "."
    else:
        text = "User not found."

    return text