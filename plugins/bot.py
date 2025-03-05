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
import plugins.heist as heist
import plugins.pizzadatabase as db
import plugins.ai as ai
user_cooldowns = {}

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

GAMBA_CHANNEL_ID = 1172911430601822238
DEFAULT_TFT_CHANNEL = 1172911430601822238 #GRUBY-TEST
DEFAULT_BDAY_CHANNEL = 1172911430601822238
DEFAULT_HEIST_CHANNEL = 1172911430601822238
if os.environ["PROD_STATUS"] == "PRODUCTION":
    DEFAULT_TFT_CHANNEL = 1032698616910983168 #LEAGUEOFDEBILS
    DEFAULT_BDAY_CHANNEL = 993905203084529865 #OGOLNY
    GAMBA_CHANNEL_ID = 1343278156265685092
    DEFAULT_HEIST_CHANNEL = 1345732567776890890

async def sendEmbedToChannel(interaction, embed, is_private=False):
    if is_private:
        await interaction.author.send(embed=embed)
    else:
        await interaction.channel.send(embed=embed)

async def triggerHeist(channel):
    currHeist = db.retrieveHeistInfo()
    started, acts = heist.heistSimulation(currHeist['heist_name'], int(currHeist['potential_loot']), int(currHeist['success_chance']))
    if started:
        for act in acts[:-1]:
            await channel.send(embed = embedgen.generateHeistBody(currHeist['level'], currHeist['heist_name'], act))
            await asyncio.sleep(300)
        heist.finalizeHeist(acts[-1].strip().lstrip('```json\n').rstrip('```'))
    else:
        await channel.send(embed = embedgen.generateHeistCanceled(currHeist['heist_name']))
        heist.finalizeHeist(None)
        
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

    @tasks.loop(hours = 1.0)
    async def sendWeather():
        print (responses.getWeather())


    @tasks.loop(minutes = 5)
    async def rouletteTask():
        channel = bot.get_channel(GAMBA_CHANNEL_ID)
        if channel:
            view = responses.ruletaView()
            await view.start(channel)

    async def waitUntil(target_time):
        now = datetime.datetime.now() + datetime.timedelta(hours=1)
        target_datetime = datetime.datetime.combine(now.date(), target_time)
        if now > target_datetime:
            target_datetime += datetime.timedelta(days = 1)

        await asyncio.sleep((target_datetime - now).total_seconds())

    @tasks.loop(hours = 4)
    async def manageHeist():
        channel = bot.get_channel(DEFAULT_HEIST_CHANNEL)
        if not db.isHeistAvailable():
            heist.generateHeist()
            currHeist = db.retrieveHeistInfo()
            await channel.send(embed = embedgen.generateHeistInvite(currHeist['level'], currHeist['heist_name'], heist.generateHeistIntro(currHeist['heist_name']), currHeist['when_starts'], currHeist['level']))
        else:
            await channel.send(embed = embedgen.generateHeistInfo(currHeist['level'], currHeist['heist_name'],currHeist['when_started'],currHeist['members']))
        currHeist = db.retrieveHeistInfo()
        
        #starts upon the time in DB
        waitUntil(datetime.datetime.strptime(currHeist['when_starts'], "%H:%M:%S").time())
        triggerHeist(channel)

    @tasks.loop(hours = 24.0)
    async def freePeopleFromPrison():
        freedUsers = db.freeAllUsers()
        if freedUsers:
            channel = bot.get_channel(DEFAULT_HEIST_CHANNEL)
            await channel.send(embed = embedgen.generatePrisonRelease(freedUsers))

    @freePeopleFromPrison.before_loop
    async def dailyPrisonEscape7AM():
        await waitUntil(datetime.time(7, 0))

    @tasks.loop(hours = 24.0)
    async def generateWinnerAndLoser():
        channel = bot.get_channel(GAMBA_CHANNEL_ID)
        winner, loser = points.generateDaily()
        if winner and loser:
            winnerUser = await bot.fetch_user(int(winner['discord_id']))
            winnerAvatarURL = winnerUser.avatar.url if winnerUser.avatar else winnerUser.default_avatar.url

            loserUser = await bot.fetch_user(int(loser['discord_id']))
            loserAvatarURL = loserUser.avatar.url if loserUser.avatar else loserUser.default_avatar.url

            await channel.send(content = winnerUser.mention, embed = embedgen.generateWinnerEmbed(winner, winnerAvatarURL))
            await channel.send(content = loserUser.mention, embed = embedgen.generateLoserEmbed(loser, loserAvatarURL))
            

    @generateWinnerAndLoser.before_loop
    async def dailyLottery6PM():
        await waitUntil(datetime.time(18, 0))

    @tasks.loop(hours = 24.0)
    async def sendBirthdayInfo():
        birthdayBoys = birthday.getBirthdayPeople()
        if birthdayBoys:
            channel = bot.get_channel(DEFAULT_BDAY_CHANNEL)
            for boy in birthdayBoys:
                user = await bot.fetch_user(boy['discord_id'])
                embed, response = responses.getBirthdayStuff(boy)
                if embed:
                    await channel.send(content = user.mention, embed = embed)
                else:
                    await channel.send(response)
        else:
            print ("[INFO] " + str(time.strftime('%Y-%m-%d %H:%M', time.gmtime())) + " - Noone has birthday today..")

    @sendBirthdayInfo.before_loop
    async def dailyBirthday8AM():
        await waitUntil(datetime.time(8, 0))

    @bot.event
    async def on_ready():
        #bot.add_view(embedgen.ruletaView())
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=os.environ["PROD_STATUS"]))
        print("[INFO] " + f'{bot.user} is now running!')
        if os.environ["PROD_STATUS"] == "PRODUCTION":
            if not analyzeMatchHistoryTFT.is_running():
                analyzeMatchHistoryTFT.start() 
            
            if not sendBirthdayInfo.is_running():
                sendBirthdayInfo.start() 

            #if not rouletteTask.is_running():
            #    rouletteTask.start() 

            if not freePeopleFromPrison.is_running():
                freePeopleFromPrison.start()

            if not manageHeist.is_running():
                manageHeist.start()

            if not generateWinnerAndLoser.is_running():
                generateWinnerAndLoser.start() 

            if not checkChannelActivityAndAwardPoints.is_running():
                checkChannelActivityAndAwardPoints.start() 
        
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        userMessage = str(message.content)
        
        # If message is empty (e.g., image, embed, sticker)
        if not userMessage:
            return
        
        if userMessage[0] == '!':
            user_id = message.author.id
            cooldown_time = 1
            if user_id in user_cooldowns:
                elapsed_time = time.time() - user_cooldowns[user_id]
                if elapsed_time < cooldown_time:
                    remaining_time = cooldown_time - elapsed_time
                    await message.channel.send(f"⏳ {message.author.mention}, nie spamuj! Mozesz uzyc bota za {remaining_time:.2f} sekund!")
                    return
            if userMessage == "!triggerheist" and message.author == 326259887007072257:
                triggerHeist(bot.get_channel(DEFAULT_HEIST_CHANNEL))

            user_cooldowns[user_id] = time.time()
            await sendMessage(message, userMessage, is_private=False)

    @tasks.loop(minutes = 5.0)
    async def analyzeMatchHistoryTFT():
        channel = bot.get_channel(DEFAULT_TFT_CHANNEL)
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
        amount = 15
        for id in VOICE_CHANNEL_IDS:
            channel = bot.get_channel(id)
            members = channel.members
            for member in members:
                if not member.voice.self_mute:
                    points.addPoints(str(member.id), amount)
        return None
    
    bot.run(TOKEN)