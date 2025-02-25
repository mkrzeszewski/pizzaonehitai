from pymongo import MongoClient
from os import environ
import time

#connect to mongodb database and get proper database
CONN_URL = "mongodb://" + environ["MONGO_USERNAME"] + ":" + environ["MONGO_PASSWORD"] + "@" + environ["MONGO_ENDPOINT"]
dbclient = MongoClient(CONN_URL)
db = dbclient['discord']
userCollection = db['users']
ruletasCollection = db['ruletas']
matchesCollection = db['parsed_tft_matches']
aiCollection = db['ai_history']

def addRouletteEntry():
    count = ruletasCollection.estimated_document_count()
    formatted_time = str(time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
    ruletasCollection.insert_one({'date': formatted_time,
                                  'winner': "",
                                  'players':[],
                                  'ruleta_id': count})
    return count

def updateRouletteEntry(ruleta_id, winner):
    ruletasCollection.update_one(
    {"ruleta_id": ruleta_id},
    {"$set": {'winner': winner}}
    )
    return None

def addRoulettePlayer(ruleta_id, players):
    if not isinstance(players, list):
        players = [players]
    ruletasCollection.update_one(
    {"ruleta_id": ruleta_id},
    {"$push": {'players': {"$each":players}}}
    )

def retrieveUser(key, value):
    return userCollection.find_one({key: value})

def retrieveAllTFTMatches():
    allMatches = matchesCollection.find({})
    return allMatches

def retrieveTFTMatch(match_id):
    return matchesCollection.find_one({'riotid': match_id})

def insertTFTMatch(match_id):
    matchesCollection.insert_one({"riotid": match_id})

def retrieveAllusers():
    return userCollection.find({})

def retrieveAllUsersSorted(key):
    return userCollection.find({}).sort({key: 1})

def retrieveAllUsersRevSorted(key):
    return userCollection.find({}).sort({key: -1})

def updateDiscordUser(discord_id, key, value):
    return updateUser('discord_id', discord_id, key, value)

def updateUser(querykey, queryvalue, key, value):
    text = "User not found."
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

def retrieveAllAIHistory(discord_id):
    result = aiCollection.find({'discord_id': str(discord_id)}, {'_id': 0, 'message': 1})
    return [doc['message'] for doc in result]
def insertAIHistory(discord_id, message):
    aiCollection.insert_one({
                                'discord_id': discord_id,
                                'message':message,
                                'date': str(time.strftime('%Y-%m-%d %H:%M', time.gmtime()))})
    return None