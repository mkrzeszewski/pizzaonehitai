import discord
import plugins.responses as responses
from discord.ext import tasks
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import time
import os
import plugins.embedgen as embedgen
import asyncio
import datetime
import plugins.birthday as birthday
import plugins.points as points

VOICE_CHANNEL_IDS = [
    1166761619351687258, #TFT ENJOYERS
    837732320017645582, #HOBBISTYCZNI HAZARDZISCI
    995377960431394969, #ANDROIDOWCY
    1154849700021796955, #JABLKARZE
    1342821212023160842, #HOROSKOP
    1200083080371765308 #EVENTOWY CHANNEL - 10x points if possible
]

#1032698616910983168 - league of debils
#1172911430601822238 - gruby-test

DEFAULT_CHANNEL = 1172911430601822238 #GRUBY-TEST
if os.environ["PROD_STATUS"] == "PRODUCTION":
    DEFAULT_CHANNEL = 1032698616910983168 #GRUBY-TEST

async def sendEmbedToChannel(interaction, embed, is_private=False):
    if is_private:
        await interaction.author.send(embed=embed)
    else:
        await interaction.channel.send(embed=embed)

        
async def sendMessage(message, user_message, is_private):
    try:
        response = ""
        embed, response, view, file = responses.handleResponse(user_message, message.author.id)
        if embed == None:
            await message.author.send(response) if is_private else await message.channel.send(response)
        else:
            await message.author.send(embed = embed, view = view, file = file) if is_private else await message.channel.send(embed = embed, view = view, file = file)   
    except Exception as e:
        print(e)

def runDiscordBot():
    TOKEN = os.environ["DC_TOKEN"]

    intents_temp = discord.Intents.default()
    intents_temp.message_content = True
    bot = discord.Client(intents = intents_temp)

    @bot.event
    async def on_ready():
        #bot.add_view(embedgen.ruletaView())
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=os.environ["PROD_STATUS"]))
        print("[INFO] " + f'{bot.user} is now running!')

        if not analyzeMatchHistoryTFT.is_running():
            analyzeMatchHistoryTFT.start() 
        
        if not sendBirthdayInfo.is_running():
            sendBirthdayInfo.start() 

        if not checkChannelActivityAndAwardPoints.is_running():
            checkChannelActivityAndAwardPoints.start() 
        
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        userMessage = str(message.content)
        if userMessage[0] == '!':
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
            if matchesToAnalyze:
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
            print ("[INFO] " + currData + " - Nie ma czego analizowac..")
        else:
            for match in matchesToAnalyze:
                print (currData + " - Analiza meczu: " + str(match))
                matchData = leagueapi.getMatchData(match)
                if matchData == 0:
                    pass
                else:

                    
                    channel = bot.get_channel(os.environ["DISCORD_CHANNEL_TFT"])
                    results, players = leagueapi.analyzeMatch(matchData, True)
                    if len(results) > 0 and len(players) > 1:
                        await channel.send(embed=embedgen.generateEmbedFromLeagueMatch(results,players,matchData['metadata']['matchId']))
                    else:
                        print ("ktos gral solo - match : " + str(matchData['metadata']['matchId']))
        leagueapi.matches = []

    @tasks.loop(minutes = 10.0)
    async def checkChannelActivityAndAwardPoints():
        amount = 5
        for id in VOICE_CHANNEL_IDS:
            channel = bot.get_channel(id)
            members = channel.members
            for member in members:
                points.addPoints(str(member.id), amount)
        return None
    
    bot.run(TOKEN)