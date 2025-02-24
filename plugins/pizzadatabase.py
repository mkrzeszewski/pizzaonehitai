from pymongo import MongoClient
from os import environ
import time

#connect to mongodb database and get proper database
CONN_URL = "mongodb://" + environ["MONGO_USERNAME"] + ":" + environ["MONGO_PASSWORD"] + "@" + environ["MONGO_ENDPOINT"]
dbclient = MongoClient(CONN_URL)
db = dbclient['discord']

def addRouletteEntry():
    ruletasCollection = db['ruletas']
    count = ruletasCollection.estimated_document_count()
    formatted_time = str(time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
    ruletasCollection.insert_one({'date': formatted_time,
                                  'winner': "",
                                  'players':[],
                                  'ruleta_id': count})
    return count

def updateRouletteEntry(ruleta_id, winner):
    ruletasCollection = db['ruletas']
    ruletasCollection.update_one(
    {"ruleta_id": ruleta_id},
    {"$set": {'winner': winner}}
    )
    return None

def addRoulettePlayer(ruleta_id, players):
    if not isinstance(players, list):
        players = [players]
    ruletasCollection = db['ruletas']
    ruletasCollection.update_one(
    {"ruleta_id": ruleta_id},
    {"$push": {'players': {"$each":players}}}
    )

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
    return updateUser('discord_id', discord_id, key, value)

def updateUser(querykey, queryvalue, key, value):
    text = "User not found."
    userCollection = db['users']
    user = userCollection.find_one({querykey: queryvalue})
    if user:
        oldValue = user[key]
        result = userCollection.update_one(
        {querykey: queryvalue},
        {"$set": {key: value}}
        )
        print("[DBINFO] DB MODIFY: {" + str(user['name']) + " - " + str(key) + ": " + str(oldValue) + " -> " + str(value) + "} - result: " + str(result))
        if result.matched_count > 0:
            text = "Zaktualizowano pole " + str(key) + " dla uzytkownika: " + str(user['name']) + "."
    return text