from pymongo import MongoClient
from os import environ
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import json

#connect to mongodb database and get proper database
CONN_URL = "mongodb://" + environ["MONGO_USERNAME"] + ":" + environ["MONGO_PASSWORD"] + "@" + environ["MONGO_ENDPOINT"]
dbclient = MongoClient(CONN_URL)
db = dbclient['discord']
userCollection = db['users']
ruletasCollection = db['ruletas']
matchesCollection = db['parsed_tft_matches']
aiCollection = db['ai_history']
quotesCollection = db['quotes']
begCollection = db['beg']
aiInstructionCollection = db['discord_bot_instructions']
slotsCollection = db['slots']
heistCollection = db['heist_history']
currHeistCollection = db['current_heist']

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

def retrieveUsers(key, value):
    return userCollection.find({key: value})

def retrieveAllTFTMatches():
    allMatches = matchesCollection.find({})
    return allMatches

def retrieveTFTMatch(match_id):
    return matchesCollection.find_one({'riotid': match_id})

def insertTFTMatch(match_id):
    matchesCollection.insert_one({"riotid": match_id})

def retrieveRandomUser():
    return userCollection.aggregate([{"$sample": {"size": 1}}]).next()

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

def insertQuote(discord_id, quote):
    quotesCollection.insert_one({
                                'discord_id': discord_id,
                                'quote':quote,
                                'date': str(time.strftime('%Y-%m-%d %H:%M', time.gmtime()))})
    return None

def retrieveRandomQuote(discord_id):
    return quotesCollection.aggregate([
    {"$match": {"discord_id": discord_id}},  
    {"$sample": {"size": 1}},                
    {"$project": {"quote": 1, "date": 1, "_id": 0}}
])

def createBegEntry(discord_id):
    if begCollection.estimated_document_count() == 0:
        begCollection.create_index('createdAt', expireAfterSeconds=600)
        begCollection.insert_one({
                                'discord_id': discord_id,
                                'createdAt': datetime.now(ZoneInfo("Europe/Warsaw"))})
    
    return None

def isBegAvailable():
    return begCollection.estimated_document_count() == 0

def getBegPerson():
    if begCollection.estimated_document_count() != 0:
        return retrieveUser('discord_id', begCollection.find_one()['discord_id'])
    return None

def retrieveAllAIInstructions():
    return aiInstructionCollection.find({})

def insertAIInstruction(message):
    return aiCollection.insert_one({'instruction':message})

def insertSlotsEntry(wage, discord_id):
    count = slotsCollection.estimated_document_count()
    slotsCollection.insert_one({'wage': wage,
                                  'player': discord_id,
                                  'earnings': 0,
                                  'slots_id': count})
    return count

def updateSlotEntry(slots_id, earnings):
    if slotsCollection.find_one({'slots_id': slots_id}):
        result = slotsCollection.update_one(
        {'slots_id': slots_id},
        {"$set": {'earnings': earnings}}
        )
        if result.matched_count > 0:
            return result
    return None

def isHeistOngoing():
    return currHeistCollection.estimated_document_count() == 0

def initializeHeist(heist_name, potential_loot, success_chance, date):
    currHeistCollection.insert_one({
                                      'heist_name': heist_name,
                                      'members': [],
                                      'potential_loot': potential_loot,
                                      'success_chance': success_chance,
                                      'when_starts': date,
                                      'ongoing': False})

def retrieveCurrentHeist():
     return currHeistCollection.find_one({})

def addMemberToHeist(member):
    currHeistCollection.update_one({},{"$push": {"members": member}})

def moveCurrentHeistToHistory(json_result):
    if json_result:
        heistCollection.insert_one(json.loads(json_result))
    currHeistCollection.delete_one({})
    
def appendHeistMember(name, value):
    new_entry = [name, value]
    currHeistCollection.update_one(
        {},
        {"$push": {"members": new_entry}}
    )

def isUserPartOfCurrentHeist(name):
    return currHeistCollection.find_one({"members": {"$elemMatch": {"0": name}}})

def isHeistAvailable():
    result = currHeistCollection.find_one({})
    if result and result["ongoing"] == False:
        return True
    else:
        return False
    
def setHeistOngoing():
    currHeistCollection.update_one({},{"$set": {"ongoing": True}})

def retrieveHeistMembers():
    return currHeistCollection.find_one({}, {"members": 1, "_id": 0})['members']

def retrieveHeistInfo():
    return currHeistCollection.find_one({}, {"heist_name": 1, "members": 1, "_id": 0, "when_starts": 1})

def isUserArrested(key, value):
    user = userCollection.find_one({key: value},{"arrested": 1})
    return user['arrested'] if user else False

def retrieveArrestedUsers():
    return userCollection.find({"arrested": True}, {"_id": 0, "name":1})

def freeAllUsers():
    freedUsers = userCollection.find({"arrested": True}, {"_id": 0, "name":1})
    userCollection.update_many({}, {"$set": {"arrested": False}})
    return freedUsers

def arrestUser(key, value):
    return userCollection.update_one({key: value},{"$set": {"arrested": True}}).matched_count

def freeUser(key, value):
    return userCollection.update_one({key: value},{"$set": {"arrested": False}}).matched_count