import requests
import time
import json
from operator import itemgetter
import math

matches = []
oldMatches = []

riotAPIfile = open ("./riot/riot-api-key","r")
API_KEY = riotAPIfile.read()
riotAPIfile.close()

parsedFile = open("./riot/alreadyParsedTFT.txt","r+")
oldMatches = parsedFile.read().splitlines()
parsedFile.close()

playersFile = open("./riot/riot-players.txt","r")
USERLIST = playersFile.read().splitlines()
playersFile.close()
importantPeople = []
for user in USERLIST:
    importantPeople.append(user.split('#')[0])

API_SUFFIX = "?api_key=" + API_KEY
SUMMONER_RANK_URL = "https://eun1.api.riotgames.com/tft/league/v1/entries/by-summoner/"
SUMMONER_API_URL = "https://eun1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/"
MATCHESID_DATA_URL = "https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/"
MATCHESID_SUFFIX = "/ids?start=0&count=20&api_key=" + API_KEY
MATCH_DATA_URL = "https://europe.api.riotgames.com/tft/match/v1/matches/"
URLS = []
playersData = {}

with open('./riot/puuid-list.json','r') as playerFile:
    playersData = json.load(playerFile)

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

#returns last 20 IDs of matches in json format, one match ID example: EUN1_3732796685
def getUserMatchHistory(player_puuid):
    currentMatches = []
    RESPONSE_MATCH_IDS = requests.get(MATCHESID_DATA_URL + player_puuid + MATCHESID_SUFFIX)
    if RESPONSE_MATCH_IDS.status_code == 200: 
        for match in RESPONSE_MATCH_IDS.json():
            if match in matches or match in oldMatches:
                pass
            else:
                matches.append(match)
                currentMatches.append(match)
        return currentMatches
    else:
        print("cos poszlo nie tak:")
        print(MATCHESID_DATA_URL + player_puuid + MATCHESID_SUFFIX)
        print(RESPONSE_MATCH_IDS.status_code)

def getMatchData(match):
    RESPONSE_MATCH = requests.get(MATCH_DATA_URL + match + API_SUFFIX)
    if RESPONSE_MATCH.status_code == 200: 
        return RESPONSE_MATCH.json()
    else:
        print("Podczas analizy meczu dostalismy status code: " + str(RESPONSE_MATCH.status_code) + ".")
        return 0
    return

def analyzeMatch(match, isAutomatic):
    results = []
    tempPlayers = []
    matchedPlayers = []

    #for avg rank
    summoner_ids = []

    for participant in match['info']['participants']:
        playerName = participant['riotIdGameName']
        placement = participant['placement']
        tempPlayers.append([playerName, placement])
        SUMMONER_ID = requests.get(SUMMONER_API_URL + participant['puuid'] + API_SUFFIX)
        if SUMMONER_ID.status_code == 200:
            summoner_ids.append(SUMMONER_ID.json()['id'])
    tempPlayers = sorted(tempPlayers, key=itemgetter(1)) 

    for player in tempPlayers:
        matchedPlayers.append(player[0])

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


    gameDuration = match['info']['game_length']
    gameDuration = math.ceil(gameDuration / 60)
    
    results.append(gameType)
    results.append(setCoreName)

    #avg rank
    avg = 0
    howManyRanks = 0
    for id in summoner_ids:
        rankBody = requests.get(SUMMONER_RANK_URL + id + API_SUFFIX)
        if rankBody.status_code == 200:
            for object in rankBody.json():
                if object['queueType'] == "RANKED_TFT":
                    tier = object['tier']
                    rank = object['rank']
                    currRank = getRankByString(tier, rank)
                    avg = avg + currRank
                    howManyRanks = howManyRanks + 1

    if(howManyRanks > 0):
        results.append("AVG rank: " + getRankByNumber(math.ceil(avg / howManyRanks)) )
    results.append("Gierka trwala : " + str(gameDuration) + " w minutach.")
    
    if isAutomatic == True:
        parsedFile = open("./riot/alreadyParsedTFT.txt","a")
        parsedFile.write(str(match['metadata']['match_id']) + "\n")
        parsedFile.close()


    #date = time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime()
    #print(formatted_time)
    date = int(match['info']['game_datetime'])
    return date, results, matchedPlayers

#print(getUserMatchHistory("IEPOyh5KUhgy5fU-6k9PwzEUB8p3G-rgcoNwKwmSA007LBcapaqCPcaYU78N0EbpQa_HiPZnMTZn_g"))

#print(getMatchData("EUN1_3732796685"))