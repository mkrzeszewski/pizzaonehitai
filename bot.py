import discord
import responses
from discord.ext import tasks
import plugins.weather as weather
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import re
import json
import random
import time
import os

WIN_ICON_URL = "https://cdn.discordapp.com/emojis/804525960345944146.webp?size=96&quality=lossless" #"https://elocentral.com/wp-content/uploads/2021/03/105050041_626416314631979_3504539849394714483_o-2.png"
LOSE_ICON_URL = "https://cdn3.emoji.gg/emojis/PepeHands.png" #"https://www.pngkey.com/png/full/713-7131234_image-rights-to-riot-games.png"
LOL_ICON = "https://raw.githubusercontent.com/github/explore/b088bf18ff2af3f2216294ffb10f5a07eb55aa31/topics/league-of-legends/league-of-legends.png"
TFT_ICON = "https://images.seeklogo.com/logo-png/48/2/teamfight-tactics-logo-png_seeklogo-487286.png"
FOOTER_ICON = "https://cdn3.emoji.gg/emojis/8003-jinxdealwithit.png"
FOOTER_TFT_ICON = "https://emoji.discadia.com/emojis/86126f3e-361e-4306-9c3f-c359ed8c50c0.png"

ENFORCER_ICON ="https://cdn.metatft.com/file/metatft/traits/squad.png"
REBEL_ICON = "https://cdn.metatft.com/file/metatft/traits/rebel.png"

ICON_ARRAY = ["https://cdn.metatft.com/file/metatft/traits/rebel.png", 
              "https://cdn.metatft.com/file/metatft/traits/warband.png", 
              "https://cdn.metatft.com/file/metatft/traits/squad.png", 
              "https://cdn.metatft.com/file/metatft/traits/crime.png"]

playersFile = open("./sharedpath/riot-players.txt","r")
USERLIST = playersFile.read().splitlines()
playersFile.close()

importantPeople = []
for user in USERLIST:
    importantPeople.append(user.split('#')[0])

print("[INFO]" + "People that will have their stats shown:")
print(importantPeople)

async def sendMessage(message, user_message, is_private):
    try:
        response = responses.handleResponse(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def generateEmbedFromTFTMatch(results,players,matchID, date):

    #title of embed - ranked/normal - set
    topTitle = results[0] + " - " + results[1]

    #we random icons for now (left - up corner)
    embedIcon = random.choice(ICON_ARRAY)
    endColour = discord.Colour.blue()

    #main title and embed data 
    embed = discord.Embed(title = str("Nowa partia z P1H w TFT!"), description = None, colour = endColour )
    embed.set_author(name = topTitle, icon_url = embedIcon)
    embed.set_thumbnail(url = TFT_ICON)

    playerList = ""
    iterator = 0
    for player in players:
        #if its one of our players - we want to underline and bold him
        if player in importantPeople:
            player = "__**" + player + "**__"
        iterator += 1
        playerList = playerList + str (iterator) + ". " + player + "\n"

    #list players (strin playerList consist newlines)
    embed.add_field(name = "__Gracze w lobby:__", value = (playerList), inline = False)
    
    #we delete info of ranked/normal and set - no longer needed in later part
    del results[0]
    del results[0]

    # CAN BE DONE BETTER - this field is to split player section and trivia section
    embed.add_field(name = "Interesting stuff: ", value = "=======================================", inline = False)

    #trivia print (given form analyze match method)
    for result in results:
        embed.add_field(name = "", value = result, inline = False)

    #footer with match ID + date
    formatted_time = time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(date)))
    embed.set_footer(text = str(matchID) + "                                                                            " + str(formatted_time), icon_url = FOOTER_TFT_ICON)

    #print(datetime.datetime.fromtimestamp(date))
    return embed

def generateEmbedFromLeagueMatch(results,players,matchID):
    playerList = ""
    for player in players:
        playerList = playerList + player + ", "
    playerList = playerList[:-2]
    print (str("Chłopaki: " + playerList + " zagrali sobie ARAMka!"))
    print(results[:-1])
    
    endGameStatus = "Kolejna przegrana.."
    endGameIcon = LOSE_ICON_URL
    endColour = discord.Colour.red()

    if(results[-2] == "win"):
        endGameStatus = "EZ WIN"
        endGameIcon = WIN_ICON_URL
        endColour = discord.Colour.green()
        
    embed = discord.Embed(title = str(playerList + " zagrali sobie ARAMka!"), description = str(results[-1]), colour = endColour )
    embed.set_author(name = endGameStatus, icon_url = endGameIcon)
    embed.set_thumbnail(url = TFT_ICON)
    for result in results[:-2]:
        embed.add_field(name = "", value = result, inline = False)

    embed.set_footer(text = str(matchID), icon_url = FOOTER_ICON)
    return embed

def runDiscordBot():
    TOKEN = os.environ["DC_TOKEN"]
    intents_temp = discord.Intents.default()
    intents_temp.message_content = True
    client = discord.Client(intents = intents_temp)

    @client.event
    async def on_ready():
        print("[INFO]" + f'{client.user} is now running!')
        #sendWeather.start()
        #analyzeMatchHistoryLeague.start()
        analyzeMatchHistoryTFT.start()
        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        userMessage = str(message.content)
        if userMessage[0] == '!':
            userMessage = userMessage[1:]
            commands = userMessage.split(" ")
            if len(commands) > 1:
                if commands[0] == "analyze":
                    if re.search(r'EUW1_\d+|EUN1_\d+',commands[1]):
                        results, players = leagueapi.analyzeMatch(leagueapi.getMatchData(str(commands[1])), False)
                        if len(results) > 0 :
                            await message.channel.send(embed=generateEmbedFromLeagueMatch(results,players,commands[1]))
                        else:
                            print(results)
                    else:
                        await message.channel.send("kolego, podaj poprawny ID, np: EUN1_3498132354")
                elif commands[0] == "analyzetft":
                    if re.search(r'EUW1_\d+|EUN1_\d+',commands[1]):
                        date, results, players = tftapi.analyzeMatch(tftapi.getMatchData(str(commands[1])), False)
                        if len(results) > 0 :
                            await message.channel.send(embed=generateEmbedFromTFTMatch(results,players,commands[1], date))
                    else:
                        await message.channel.send("kolego, podaj poprawny ID, np: EUN1_3498132354")
            else:
                await sendMessage(message, userMessage, is_private=False)

    @tasks.loop(hours = 1.0)
    async def sendWeather():
        #channel = client.get_channel(1172911430601822238)
        print (weather.getLodzWeather())

    @tasks.loop(minutes = 5.0)
    async def analyzeMatchHistoryTFT():
        currData = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        playersData = []
        with open('./sharedpath/puuid-list.json','r') as playerFile:
            playersData = json.load(playerFile)
        matchesToAnalyze = []
        parsedFile = open("./sharedpath/alreadyParsedTFT.txt","r+")
        oldMatches = parsedFile.read().splitlines()
        parsedFile.close()
        for player in playersData['players']:
            tempMatches = tftapi.getUserMatchHistory(player['puuid'])

            #this is quick-fix for an exception and should be handled properly later on
            if tempMatches == 0:
                return
            
            for match in tempMatches:
                if match in oldMatches:
                    pass
                else:
                    matchesToAnalyze.append(match)   

        if len(matchesToAnalyze) == 0:
            print ("[INFO]" + currData + " - Nie ma obecnie meczy TFT do analizy.")
        else:
            for match in matchesToAnalyze:
                matchData = tftapi.getMatchData(match)

                if matchData == 0:
                    pass
                else:
                    #1032698616910983168 - league of debils
                    #1172911430601822238 - gruby-test
                    channel = client.get_channel(1032698616910983168)
                    date, results, players = tftapi.analyzeMatch(matchData, True)
                    await channel.send(embed=generateEmbedFromTFTMatch(results,players,matchData['metadata']['match_id'], date))

        tftapi.matches = []

    @tasks.loop(minutes = 5.0)
    async def analyzeMatchHistoryLeague():
        currData = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        playerList = []
        playersFile = open("./sharedpath/riot-players.txt","r")
        playerList = playersFile.read().splitlines()
        playersFile.close()
        matchesToAnalyze = []
        for player in playerList:
            tempMatches = leagueapi.getUserMatchHistory(player)
            
            for match in tempMatches:
                
                matchesToAnalyze.append(match)
        if len(matchesToAnalyze) == 0:
            print ("[INFO]" + currData + " - Nie ma czego analizowac..")
        else:
            for match in matchesToAnalyze:
                print (currData + " - Analiza meczu: " + str(match))
                matchData = leagueapi.getMatchData(match)
                if matchData == 0:
                    pass
                else:
                    #1032698616910983168 - league of debils
                    #1172911430601822238 - gruby-test
                    channel = client.get_channel(1032698616910983168)
                    results, players = leagueapi.analyzeMatch(matchData, True)
                    if len(results) > 0 and len(players) > 1:
                        await channel.send(embed=generateEmbedFromLeagueMatch(results,players,matchData['metadata']['matchId']))
                    else:
                        print ("ktos gral solo - match : " + str(matchData['metadata']['matchId']))
        leagueapi.matches = []

    client.run(TOKEN)
