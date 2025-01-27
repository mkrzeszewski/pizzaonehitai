import requests
import datetime

matches = []
oldMatches = []
riotAPIfile = open ("./sharedpath/riot-api-key","r")
parsedFile = open("./sharedpath/alreadyParsed.txt","r+")
oldMatches = parsedFile.read().splitlines()
parsedFile.close()


API_KEY = riotAPIfile.read().replace('\n','')
riotAPIfile.close()
API_SUFFIX = "?api_key=" + API_KEY
SUMMONERS_DATA_URL = "https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"
MATCHESID_DATA_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" #IEPOyh5KUhgy5fU-6k9PwzEUB8p3G-rgcoNwKwmSA007LBcapaqCPcaYU78N0EbpQa_HiPZnMTZn_g"
MATCH_DATA_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/"
URLS = []
playersFile = open("./sharedpath/riot-players.txt","r")
#playerList = playersFile.read().splitlines()

#USERLIST = {"P1H Rolab","AlphaKubek","Jeezie666","SMIRTFONEK","TipJoker","Wklej","CLG Pablo","Deαn","FatherInLaw","Kamil100CM","Minzzzy"}
USERLIST = playersFile.read().splitlines()
playersFile.close()

def analyzeMatch(match, isAutomatic):
    playersInMatch = ""
    ciekawostki = []
    smallestKda = 10000.0
    highestKda = -1.0
    smallestKdaGame = 10000.0
    highestKdaGame = -1.0
    smallestKdaName = ""
    highestKdaName = ""
    weWon = True
    wasSurrender = False
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
                        ciekawostki.append(player['summonerName'] + " w tym meczu wykręcił penta killa postacią: " + player['championName'] + ".")

                    if player['deaths'] >= impressiveDeaths:
                        ciekawostki.append(player['summonerName'] + " zaliczył w tym meczu " + str(player['deaths']) + " wywrotek.")
                    if player['kills'] == 0:
                        ciekawostki.append(player['summonerName'] + " nie zabił nikogo.")
                    if player['challenges']['teamDamagePercentage'] >= 0.60:
                        ciekawostki.append("Ło cie baben - " + player['summonerName'] + " nabił " + str(round(player['challenges']['teamDamagePercentage'],2) * 100) + "%" + "dmg całego teamu.")
                    if player['challenges']['kda'] < smallestKda:
                        smallestKda = player['challenges']['kda']
                        smallestKdaName = player['summonerName']
                    if player['challenges']['kda'] > highestKda:
                        highestKda = player['challenges']['kda']
                        highestKdaName = player['summonerName']

                    wasSurrender = player['gameEndedInSurrender']
                    weWon = player['win']

                    #ciekowistki osobiste
                    if player['summonerName'] == "P1H Rolab" and player['championName'] == "Kennen":
                        ciekawostki.append("Mati grał kennenem i rzucał małym małym shurikenem")
                    if player['summonerName'] == "AlphaKubek" and player['championName'] == "Heimerdinger":
                        ciekawostki.append("Maliniaka znowu atakowały brokuły.")
                    if player['summonerName'] == "AlphaKubek" and player['championName'] == "Vladimir":
                        ciekawostki.append("Maliniak z wodogłowiem odwiedził salony.")
                    if player['summonerName'] == "Tip Joker" and player['championName'] == "Caitlyn" and player['challenges']['mythicItemUsed'] == 6691:
                        ciekawostki.append("Tomek znowu trolluje kolegom mecz Caitlyn z Duskbladem. Klasyka.")

                if player['challenges']['kda'] < smallestKdaGame:
                    smallestKdaGame = player['challenges']['kda']
                if player['challenges']['kda'] > highestKdaGame:
                    highestKdaGame = player['challenges']['kda']
    except:
        print(match)
            
    
    #jakies ciekawostki po przeliczeniu
    ciekawostki.append(smallestKdaName + " przykurwił najsłabsze kda: " + str(round(smallestKda,2)) + " (najgorsze w całej grze: " + str(round(smallestKdaGame,2)) + ").\nNajlepsze KDA zajebał: " +highestKdaName+ " : " + str(round(highestKda,2)) + " (najlepsze w całej grze: " + str(round(highestKdaGame,2)) + ").")           
    if wasSurrender == True and weWon == True:
        ciekawostki.append("Przeciwnicy to cipy i się poddały.")
    if wasSurrender == True and weWon == False:
        ciekawostki.append("Chłopakom siadła psycha i zajebali surrendera.")
    if weWon == True:
        ciekawostki.append("win")
    else:
        ciekawostki.append("lose") 
    ciekawostki.append("Gierka trwała : " + gameDuration + ".")

    if isAutomatic == True:
        parsedFile = open("./sharedpath/alreadyParsed.txt","a")
        parsedFile.write(str(match['metadata']['matchId']) + "\n")
        parsedFile.close()

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
            final_matches.append(response_match.json())
        else:
            print("Podczas analizy meczu dostalismy status code: " + str(response_match.status_code) + ".")
        
    for match in final_matches:
        return analyzeMatch(match)
        # if(len(ourPlayers) >= 2):
        #     return ciekawostki, ourPlayers
