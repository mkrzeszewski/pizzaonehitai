import requests
import datetime

matches = []
oldMatches = []
riotAPIfile = open ("./riotAPI.txt","r")
parsedFile = open("./alreadyParsed.txt","r+")
oldMatches = parsedFile.read().splitlines()
parsedFile.close()
parsedFile = open("./alreadyParsed.txt","a")

API_KEY = riotAPIfile.read()
API_SUFFIX = "?api_key=" + API_KEY
SUMMONERS_DATA_URL = "https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"
MATCHESID_DATA_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" #IEPOyh5KUhgy5fU-6k9PwzEUB8p3G-rgcoNwKwmSA007LBcapaqCPcaYU78N0EbpQa_HiPZnMTZn_g"
MATCH_DATA_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/"
URLS = []
USERLIST = {"P1H Rolab","AlphaKubek","Jeezie666","SMIRTFONEK","TipJoker","Wklej","CLG Pablo","Deαn","FatherInLaw","Kamil100CM","Minzzzy"}


def analyzeMatch(match):
    playersInMatch = ""
    ciekawostki = []
    smallestKda = 10000.0
    smallestKdaName = ""
    weWon = True
    impressiveDeaths = 18
    gameDuration = str(0)
    pizzaPlayerAmount = 0
    ourPlayers = []
    try:
        if match['info']['gameMode'] == "ARAM":
            gameDuration = str(datetime.timedelta(seconds = match['info']['gameDuration']))
            for player in match['info']['participants']:
                if player['summonerName'] in USERLIST:
                    ourPlayers.append(player['summonerName'])
                    playersInMatch += player['summonerName'] + ", "
                    pizzaPlayerAmount = pizzaPlayerAmount + 1
                    if player['pentaKills'] > 0:
                        ciekawostki.append(player['summonerName'] + " w tym meczu przykurwił pentę postacią: " + player['championName'] + ".")

                    if player['deaths'] >= impressiveDeaths:
                        ciekawostki.append(player['summonerName'] + " zaliczył w tym meczu " + str(player['deaths']) + " wywrotek.")
                    if player['kills'] == 0:
                        ciekawostki.append(player['summonerName'] + " nie zabił nikogo.")
                    if player['challenges']['teamDamagePercentage'] >= 0.60:
                        ciekawostki.append("Ło cie baben - " + player['summonerName'] + " przykurwił " + str(round(player['challenges']['teamDamagePercentage'],2)) + "%dmg całego teamu.")
                    if player['challenges']['kda'] < smallestKda:
                        smallestKda = player['challenges']['kda']
                        smallestKdaName = player['summonerName']
                    weWon = player['win']
    except:
        print(match)
            

    #jakies ciekawostki po przeliczeniu
    ciekawostki.append(smallestKdaName + " przykurwił najsłabsze kda : " + str(round(smallestKda,2)) + ".")           
    if weWon == True:
        ciekawostki.append("win")
    else:
        ciekawostki.append("lose") 
    ciekawostki.append("Gierka trwała : " + gameDuration + ".")
    #ciekawostki.insert(0,"W tym meczu graly takie byczki z Pizza One Hit : " + playersInMatch[:-2] + "!")
    parsedFile.write(str(match['metadata']['matchId']) + "\n")
    oldMatches.append(match['metadata']['matchId'])
    return ciekawostki, ourPlayers

    


def getMatchIDs(player_puuid):
    response_matches = requests.get(MATCHESID_DATA_URL + player_puuid + "/ids" + API_SUFFIX)
    matches_ids = response_matches.json()
    return matches_ids

def getUserMatchHistory(user):
    tempMatches = []
    response_player = requests.get(SUMMONERS_DATA_URL + user + API_SUFFIX)
    player_info = response_player.json()
    player_puuid = player_info['puuid']
    matches_ids = getMatchIDs(player_puuid)
    for match in matches_ids:
        if match in matches or match in oldMatches:
            pass
        else:
            tempMatches.append(match)
            matches.append(match)
    return tempMatches

def getMatchData(match):
    response_match = requests.get(MATCH_DATA_URL + match + API_SUFFIX)
    if response_match.status_code == 200: 
        parsedFile.write(str(match) + "\n")
        return response_match.json()
    else:
        print("Podczas analizy meczu dostalismy status code: " + str(response_match.status_code) + ".")
        return 0

def analyze():
    for user in USERLIST:
        getUserMatchHistory(user)
    final_matches=[]

    for match in matches:    
        response_match = requests.get(MATCH_DATA_URL + match + API_SUFFIX)
        if response_match.status_code == 200: 
            parsedFile.write(str(match) + "\n")
            final_matches.append(response_match.json())
        else:
            print("Podczas analizy meczu dostalismy status code: " + str(response_match.status_code) + ".")
        
    for match in final_matches:
        return analyzeMatch(match)
        # if(len(ourPlayers) >= 2):
        #     return ciekawostki, ourPlayers
