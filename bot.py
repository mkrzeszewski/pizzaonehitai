import discord
import responses
from discord.ext import tasks
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import re
import time
import os
import embedgen
import asyncio
import datetime
import plugins.birthday as birthday

async def sendMessage(message, user_message, is_private):
    try:
        response = responses.handleResponse(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def runDiscordBot():
    TOKEN = os.environ["DC_TOKEN"]
    intents_temp = discord.Intents.default()
    intents_temp.message_content = True
    bot = discord.Client(intents = intents_temp)

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=os.environ["PROD_STATUS"]))
        print("[INFO]" + f'{bot.user} is now running!')

        if not analyzeMatchHistoryTFT.is_running():
            analyzeMatchHistoryTFT.start() 
        
        if not sendBirthdayInfo.is_running():
            sendBirthdayInfo.start() 
        
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
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
                            await message.channel.send(embed=embedgen.generateEmbedFromLeagueMatch(results,players,commands[1]))
                        else:
                            print(results)
                    else:
                        await message.channel.send("kolego, podaj poprawny ID, np: EUN1_3498132354")
                elif commands[0] == "analyzetft":
                    if re.search(r'EUW1_\d+|EUN1_\d+',commands[1]):
                        date, results, players = tftapi.analyzeMatch(tftapi.getMatchData(str(commands[1])), False)
                        if len(results) > 0 :
                            await message.channel.send(embed=embedgen.generateEmbedFromTFTMatch(results,players,commands[1], date))
                    else:
                        await message.channel.send("kolego, podaj poprawny ID, np: EUN1_3498132354")
            else:
                await sendMessage(message, userMessage, is_private=False)

    @tasks.loop(hours = 1.0)
    async def sendWeather():
        print (responses.getWeather())

    async def waitUntil(target_time):
        #wait until specified time to start loop for DC bot
        now = datetime.datetime.now()
        target_datetime = datetime.datetime.combine(now.date(), target_time)

        # If the time has already passed today, schedule for tomorrow
        if now > target_datetime:
            target_datetime += datetime.timedelta(days = 1)

        await asyncio.sleep((target_datetime - now).total_seconds())

    @tasks.loop(hours = 24.0)
    async def sendBirthdayInfo():
        birthdayBoys = birthday.getBirthdayPeople()
        if birthdayBoys != None:
            for boy in birthdayBoys:
                print (boy['username'])
        else:
            print ("[INFO] Noone has birthday today..")

    @sendBirthdayInfo.before_loop
    async def beforeBirthdayTask():
        #ensure its 8AM - the bot will send messages ONCE every 24H - this task should only happen ONCE.
        await waitUntil(datetime.time(8, 0))
        
    @tasks.loop(minutes = 5.0)
    async def analyzeMatchHistoryTFT():
        channel = bot.get_channel(1172911430601822238)
        status_code = tftapi.isAPIDown()
        if status_code:
            print("[ERROR] API is unreachable - status code " + str(status_code))
        else:
            matchesToAnalyze = tftapi.getMatchesToAnalyze()
            if matchesToAnalyze != None:
                for match in matchesToAnalyze:
                    matchData = tftapi.getMatchData(match)
                    if matchData == 0:
                        pass
                    else:
                        date, results, players = tftapi.analyzeMatch(matchData, True)
                        await channel.send(embed=embedgen.generateEmbedFromTFTMatch(results,players,matchData['metadata']['match_id'], date))
        return 0

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
                    channel = bot.get_channel(os.environ["DISCORD_CHANNEL_TFT"])
                    results, players = leagueapi.analyzeMatch(matchData, True)
                    if len(results) > 0 and len(players) > 1:
                        await channel.send(embed=embedgen.generateEmbedFromLeagueMatch(results,players,matchData['metadata']['matchId']))
                    else:
                        print ("ktos gral solo - match : " + str(matchData['metadata']['matchId']))
        leagueapi.matches = []

    bot.run(TOKEN)
