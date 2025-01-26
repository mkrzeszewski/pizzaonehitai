import requests
import json
defaultContent = {"players": []}
puuidFile = open("./riot/puuid-list.json","r+")
puuidFile.truncate(0)
json.dump(defaultContent, puuidFile, indent = 4)
puuidFile.close()

riotAPIfile = open ("./riot/riot-api-key","r")
API_KEY = riotAPIfile.read().replace('\n','')
API_SUFFIX = "?api_key=" + API_KEY

playersFile = open("./riot/riot-players.txt","r")
USERLIST = playersFile.read().splitlines()
playersFile.close()

headers = {
    "authority": "www.google.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "X-Riot-Token": API_KEY
}

def generatePUUIDfile():
    for user in USERLIST:
        USERNAME = user.split('#')[0]
        TAG = user.split('#')[1]
        ACCOUNT_API_URL = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + USERNAME + '/' + TAG + API_SUFFIX
        
        PLAYER_DATA = requests.get(ACCOUNT_API_URL, headers=headers)
        if PLAYER_DATA.status_code == 200: 
            puuidFile = open("./riot/puuid-list.json","r+")
            currentJsonBody = json.load(puuidFile)
            SUMMONER_API_URL = "https://eun1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/"
            SUMMONER_ID = requests.get(SUMMONER_API_URL + PLAYER_DATA.json()['puuid'] + API_SUFFIX, headers=headers)

            jsonBody = {"puuid":PLAYER_DATA.json()['puuid'], "summoner_id": SUMMONER_ID.json()['id'], "tag":TAG, "riotid": USERNAME}
            currentJsonBody['players'].append(jsonBody)
            puuidFile.seek(0)
            json.dump(currentJsonBody,puuidFile, indent = 4)
            puuidFile.close()
            print("done!")
        else:
            print("error - " + str(PLAYER_DATA.status_code) + ".")
            print("request URL:")
            print(ACCOUNT_API_URL)
    return


generatePUUIDfile()