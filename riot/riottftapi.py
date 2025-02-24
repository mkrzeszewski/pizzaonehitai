import requests
import time
from operator import itemgetter
import math
from os import environ
import plugins.pizzadatabase as db
import plugins.points as points

#token for RIOT - defined in ENV file
API_KEY = environ["RIOT_API_TOKEN"]

#get all users from mongodb database
users = db.retrieveAllusers()
importantPeople = []
players = []
oldMatches = []

if users != None:
    for user in users:
        players.append(user)
        importantPeople.append(user['riotid'])

def setAPIKey(updatedApiKey):
    global API_KEY
    API_KEY = updatedApiKey

#imitate real browser
headers = {
    "authority": "www.google.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "X-Riot-Token": API_KEY
}

#API & URL FOR API
API_SUFFIX = ""# "?api_key=" + API_KEY
SUMMONER_RANK_URL = "https://eun1.api.riotgames.com/tft/league/v1/entries/by-summoner/"
SUMMONER_API_URL = "https://eun1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/"
MATCHESID_DATA_URL = "https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/"
MATCHESID_SUFFIX = "/ids?start=0&count=20" #&api_key=" + API_KEY
MATCH_DATA_URL = "https://europe.api.riotgames.com/tft/match/v1/matches/"
PLATFORM_STATUS_URL = "https://eun1.api.riotgames.com/tft/status/v1/platform-data"

def isAPIDown():
    API_RESPONSE = requests.get(PLATFORM_STATUS_URL + API_SUFFIX, headers=headers)
    if API_RESPONSE.status_code == 200:
        return False
    return API_RESPONSE.status_code

#this function is to exchange numeric rank (obtained by getRankByString) to its proper correspondet rank name (i.e 17 = Platinum IV)
def getRankByNumber(number):

    rest = number % 4
    main = int(number / 4.0) 

    rank = ""
    if main == 0:
        rank = "IRON"
    elif main == 1:
        rank = "BRONZE"
    elif main == 2:
        rank = "SILVER"
    elif main == 3:
        rank = "GOLD"
    elif main == 4:
        rank = "PLATINUM"
    elif main == 5:
        rank = "EMERALD"
    elif main == 6:
        rank = "DIAMOND"
    elif main == 7:
        rank = "MASTER"
    elif main == 8:
        rank = "GRANDMASTER"
    elif main == 9:
        rank = "CHALLENGER"

    
    if rest == 0:
        rank = rank + " IV"
    elif rest == 1:
        rank = rank + " III"
    elif rest == 2:
        rank = rank + " II"
    elif rest == 3:
        rank = rank + " I"

    #print("Numer na wejsciu to : " + str(number) + ", reszta z modulo 4 to : " + str(rest) + ", main ranga to " + str(main) + ", wiec ranga to : " + rank)

    return rank

#this function is to change literal rank name (I.E - Platinum IV) to numeric rank (in case of P4 - 17). It's counterpart is getRankByNumber
def getRankByString(tier, division):
    div = 0
    mult = 0
    if tier == "BRONZE":
        mult = 1
    elif tier == "SILVER":
        mult = 2
    elif tier == "GOLD":
        mult = 3
    elif tier == "PLATINUM":
        mult = 4
    elif tier == "EMERALD":
        mult = 5
    elif tier == "DIAMOND":
        mult = 6
    elif tier == "MASTER":
        mult = 7
    elif tier == "GRANDMASTER":
        mult = 8
    elif tier == "CHALLENGER":
        mult = 9

    if division == "IV":
        div = 0
    elif division == "III":
        div = 1
    elif division == "II":
        div = 2
    elif division == "I":
        div = 3

    number = (4 * mult) + div

    #print(tier + " " + division + " - " + str(number))
    
    return number

#modify names from TFT Api to what we know as playing
def getProperCharacterName(originalName):
    name = originalName.removeprefix("TFT13_")
    if name == "Beardy":
        name = "Loris"
    return name

#this is called every 5 minutes by bot
def getMatchesToAnalyze():
    matchesToAnalyze = []
    for player in players:
        tempMatches = getUserMatchHistory(player['puuid'])

        #this is quick-fix for an exception and should be handled properly later on
        if tempMatches == None:
            return 
        
        #check if match is already in DB or if is already in list during this for instruction
        for match in tempMatches:
            if db.retrieveTFTMatch(match) or match in matchesToAnalyze:
                pass
            else:
                matchesToAnalyze.append(match)

    if matchesToAnalyze:
        print(matchesToAnalyze)
        return matchesToAnalyze
    else:
        print ("[INFO] " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " - Nie ma obecnie meczy TFT do analizy.")
        return None
    
#returns last 20 IDs of matches in json format, one match ID example: EUN1_3732796685
def getUserMatchHistory(player_puuid):
    currentMatches = []
    RESPONSE_MATCH_IDS = requests.get(MATCHESID_DATA_URL + player_puuid + MATCHESID_SUFFIX, headers=headers)
    if RESPONSE_MATCH_IDS.status_code == 200: 
        for match in RESPONSE_MATCH_IDS.json():
            if match in oldMatches:
                pass
            else:
                currentMatches.append(match)
        return currentMatches
    else:
        print("[ERROR]" + "Something went wrong: ")
        print(MATCHESID_DATA_URL + player_puuid + MATCHESID_SUFFIX)
        print(RESPONSE_MATCH_IDS.status_code)

    return None

#get data from one match (match = MATCHID, example EUN1_3732796685)
def getMatchData(match):
    print ("[INFO] " + "Analysing: " + str(match))
    RESPONSE_MATCH = requests.get(MATCH_DATA_URL + match + API_SUFFIX, headers=headers)
    if RESPONSE_MATCH.status_code == 200: 
        return RESPONSE_MATCH.json()
    elif RESPONSE_MATCH.status_code == 429:
        print("[ERROR]" + "Too many requests! Try again later.")
    else:
        print("[ERROR]" + "Podczas analizy meczu dostalismy status code: " + str(RESPONSE_MATCH.status_code) + ".")
    return 0

#get interesting data from match, returns:date when match took place, results array, players that played.
def analyzeMatch(match, isAutomatic):
    if match == 0:
        print("[ERROR]" + "Empty match data has been parsed to analyzeMatch - aborting.")
        return 
    results = []
    tempPlayers = []
    matchedPlayers = []

    queueType = str(match['info']['queue_id'])
    if queueType == "6100":
        queueType = "NORMAL"
    elif queueType == "1090":
        queueType = "NORMAL"
    elif queueType == "1100":
        queueType = "RANKED"
    elif queueType == "1130":
        queueType = "HYPER ROLL"

    gameType = queueType 
    setCoreName =  str(match['info']['tft_set_core_name'])
    match setCoreName:
        case "TFTSet13":
            setCoreName = "TFT SET 13 - Arcane"
        case "TFTSet4_Act2":
            setCoreName = "TFT SET 4.5 - Fates"

    #for avg rank - later on
    summoner_ids = []

    maxDamage = 0
    currMaxDamageUser = ""
    currEliminationRecord = 0

    for participant in match['info']['participants']:  
        playerName = participant['riotIdGameName']
        placement = participant['placement']
        tempPlayers.append([playerName, placement])
        SUMMONER_ID = requests.get(SUMMONER_API_URL + participant['puuid'] + API_SUFFIX, headers=headers)
        if SUMMONER_ID.status_code == 200:
            summoner_ids.append(SUMMONER_ID.json()['id'])

        if int(participant['total_damage_to_players']) >= maxDamage:
            maxDamage = int(participant['total_damage_to_players'])
            currMaxDamageUser = playerName

        #if someone had lvl4/5 3 star - add info in trivia!
        for unit in participant['units']:
            properName = str(getProperCharacterName(unit['character_id']))
            if (int(unit['rarity']) >= 4) & (int(unit['tier']) >= 3) & (properName != "Sion") :
                results.append(playerName + " had 3 star " + properName + "!")
    tempPlayers = sorted(tempPlayers, key=itemgetter(1)) 

    #add all players to list, bold + underline for important people 
    for player in tempPlayers:
        finalPlayer = player[0]
        placement = player[1]
        if finalPlayer in importantPeople:

            #append points if its automatic match
            if isAutomatic == True:
                modifyPoints = 40 - (10 * placement)
                if placement in [1, 8]:
                    modifyPoints *= 2
                points.modifyPoints('riotid',finalPlayer, modifyPoints)
            finalPlayer = "__**" + finalPlayer + "**__"
        matchedPlayers.append(finalPlayer)

    gameDuration = match['info']['game_length']
    gameDuration = math.ceil(gameDuration / 60)
    
    results.append(gameType)
    results.append(setCoreName)

    #avg rank
    avg = 0
    howManyRanks = 0
    for id in summoner_ids:
        rankBody = requests.get(SUMMONER_RANK_URL + id + API_SUFFIX, headers=headers)
        if rankBody.status_code == 200:
            for object in rankBody.json():
                if object['queueType'] == "RANKED_TFT":
                    tier = object['tier']
                    rank = object['rank']
                    currRank = getRankByString(tier, rank)
                    avg = avg + currRank
                    howManyRanks = howManyRanks + 1


    #TRIVIA

    #avg ranks
    if(howManyRanks > 0):
        results.append("AVG rank: " + getRankByNumber(math.ceil(avg / howManyRanks)) )

    #how long the game took
    results.append("Timeframe: " + str(gameDuration) + "m.")
    
    #max damage
    results.append("Most damage to players: " + str(maxDamage) + " by - " + currMaxDamageUser + ".")

    #ensure this match is not analysed again by bot
    if isAutomatic == True:
        db.insertTFTMatch(match['metadata']['match_id'])

    #date = time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime()
    #print(formatted_time)
    date = int(int(match['info']['game_datetime']) / 1000) + 3600


    return date, results, matchedPlayers
