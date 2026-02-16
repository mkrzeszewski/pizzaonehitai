import discord
import plugins.responses as responses
from discord.ext import tasks
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import os
import plugins.embedgen as embedgen
import asyncio
from datetime import datetime, timedelta, time
import plugins.birthday as birthday
import plugins.points as points
import plugins.heist as heist
import plugins.pizzadatabase as db
import plugins.stocks as stocks
import plugins.theatres as theatres
from plugins.embedgen import TheatreEmbedGen, HeistEmbedGen

target_stock_time = time(hour=7, minute=0)
user_cooldowns = {}
manual_triggered = False
VOICE_CHANNEL_IDS = [
#    1166761619351687258, #TFT ENJOYERS
#    837732320017645582 #HOBBISTYCZNI HAZARDZISCI
#    995377960431394969, #ANDROIDOWCY
#    1154849700021796955, #JABLKARZE
#    1342821212023160842, #HOROSKOP
#    1200083080371765308 #EVENTOWY CHANNEL - 10x points if possible
]

#1032698616910983168 - league of debils
#1172911430601822238 - gruby-test

GAMBA_CHANNEL_ID = 1172911430601822238
DEFAULT_TFT_CHANNEL = 1172911430601822238 #GRUBY-TEST
DEFAULT_BDAY_CHANNEL = 1172911430601822238
DEFAULT_HEIST_CHANNEL = 1172911430601822238
DEFAULT_THEATRES_CHANNEL = 1422322104237297754
if os.environ["PROD_STATUS"] == "PRODUCTION":
    DEFAULT_TFT_CHANNEL = 1032698616910983168 #LEAGUEOFDEBILS
    DEFAULT_BDAY_CHANNEL = 993905203084529865 #OGOLNY
    GAMBA_CHANNEL_ID = 1343278156265685092
    DEFAULT_HEIST_CHANNEL = 1345732567776890890

TOKEN = os.environ["DC_TOKEN"]
intents_temp = discord.Intents.default()
intents_temp.message_content = True
bot = discord.Client(intents = intents_temp)

_theatreEmbedGen = TheatreEmbedGen()

async def sendEmbedToChannel(interaction, embed, is_private=False):
    if is_private:
        await interaction.author.send(embed=embed)
    else:
        await interaction.channel.send(embed=embed)

async def triggerHeist(channel):
    currHeist = db.retrieveHeistInfo()
    # Symulacja zwraca akty
    started, acts = heist.heistSimulation(currHeist['heist_name'], int(currHeist['potential_loot']), int(currHeist['success_chance']))
    
    if started:
        for act in acts[:-1]:
            await asyncio.sleep(300)
            # Używamy nowej metody z klasy heistGen
            await channel.send(embed=responses._heistEmbedGen.simulation_step(currHeist['level'], currHeist['heist_name'], act))
        
        # Finalizacja (parsowanie JSON z ostatniego aktu)
        result_json = acts[-1].strip().lstrip('```json\n').rstrip('```')
        heist.finalizeHeist(result_json)
    else:
        await channel.send(embed=responses._heistEmbedGen.canceled(currHeist['heist_name']))
        heist.finalizeHeist(None)
        
async def sendMessage(message, user_message, is_private):
    try:
        response = ""
        embed, response, view, file = await responses.handleResponse(user_message, message.author.id, bot)
        if embed == None:
            await message.author.send(response) if is_private else await message.channel.send(response)
        else:
            await message.author.send(embed = embed, view = view, file = file) if is_private else await message.channel.send(embed = embed, view = view, file = file)   
    except Exception as e:
        print(e)

def runDiscordBot():
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
        now = datetime.now() + timedelta(hours=1)
        target_datetime = datetime.combine(now.date(), target_time)
        if now > target_datetime:
            target_datetime += timedelta(days = 1)

        await asyncio.sleep((target_datetime - now).total_seconds())

    #theatre section
    @tasks.loop(time=target_stock_time)
    async def theatreCheck():
        channel = bot.get_channel(DEFAULT_THEATRES_CHANNEL)
        parsedTheatres = theatres.checkNewEvents()
        if parsedTheatres:
            for theatre in parsedTheatres:
                for event in theatre[1]:
                    await channel.send(embed = _theatreEmbedGen.theatre_event_list(theatre[0], event[0], event[1]))

    @tasks.loop(hours=4)
    async def manageHeist():
        channel = bot.get_channel(DEFAULT_HEIST_CHANNEL)
        if not channel:
            print("[ERROR] Nie znaleziono kanału dla napadów!")
            return
        if not db.isHeistOngoing():
            heist.generateHeist()
            currHeist = db.retrieveHeistInfo()
            intro_text = heist.generateHeistIntro(currHeist['heist_name'])
            embed = responses._heistEmbedGen.invite(
                level=currHeist['level'], 
                heist_name=currHeist['heist_name'], 
                intro_msg=intro_text, 
                time_limit=currHeist['when_starts']
            )
            await channel.send(embed=embed)
        else:
            currHeist = db.retrieveHeistInfo()
            embed = responses._heistEmbedGen.info(
                level=currHeist['level'], 
                heist_name=currHeist['heist_name'], 
                time_limit=currHeist['when_starts'], 
                members=currHeist['members']
            )
            await channel.send(embed=embed)
        currHeist = db.retrieveHeistInfo()
        
        try:
            start_time_dt = datetime.strptime(currHeist['when_starts'], "%H:%M:%S").time()
            
            print(f"[HEIST] Oczekiwanie na start napadu '{currHeist['heist_name']}' o godzinie {start_time_dt}")
            await waitUntil(start_time_dt)
            await triggerHeist(channel)
        except ValueError as e:
            print(f"[ERROR] Błędny format czasu w bazie danych: {currHeist['when_starts']}. Błąd: {e}")

    @tasks.loop(hours = 24.0)
    async def freePeopleFromPrison():
        freedUsers = db.freeAllUsers()
        if freedUsers:
            channel = bot.get_channel(DEFAULT_HEIST_CHANNEL)
            await channel.send(embed = embedgen.generatePrisonRelease(freedUsers))

    #stock section
    @tasks.loop(hours = 1.0)
    async def simulateStockTrends():
        stocks.simulateTrends()

    @tasks.loop(hours = 3.0)
    async def sendStocksRundown():
        msg = stocks.informOnStocksUpdate()
        channel = bot.get_channel(GAMBA_CHANNEL_ID)
        await channel.send(embedgen.generateStocksRundown(msg))

    @tasks.loop(minutes = 10.0)
    async def updateStockPrices():
        bankrupts = stocks.updatePrices()
        if bankrupts:
            channel = bot.get_channel(GAMBA_CHANNEL_ID)
            for bankrupt in bankrupts:
                user = db.retrieveUser('name',bankrupt[0]['ceo'])
                if user:
                    bankruptUser = await bot.fetch_user(int(user['discord_id']))
                    bankruptAvatarURL = bankruptUser.avatar.url if bankruptUser.avatar else bankruptUser.default_avatar.url
                    await channel.send(embed = embedgen.generateBankrupcy(bankrupt[0], bankruptAvatarURL, bankrupt[1]))
    
    @tasks.loop(time=target_stock_time)
    async def generateStocks():
        if datetime.now().weekday() == 0: #monday 10 am
            stocks.generateStocks()
            channel = bot.get_channel(GAMBA_CHANNEL_ID)
            _stocks = list(db.retrieveAllStocks())
            if _stocks:
                await channel.send(embed = responses._stockEmbedGen.full_stonks(_stocks))
            else:
                print("[STOCKS] - cos poszlo nie tak przy generowaniu")

    #prison
    @freePeopleFromPrison.before_loop
    async def dailyPrisonEscape7AM():
        await waitUntil(time(7, 0))

    #daily winner
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
        await waitUntil(time(18, 0))

    #birthday
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
            print ("[INFO] " + str(datetime.now().strftime('%Y-%m-%d %H:%M')) + " - Noone has birthday today..")

    @sendBirthdayInfo.before_loop
    async def dailyBirthday8AM():
        await waitUntil(time(11, 0))

    @tasks.loop(minutes = 5.0)
    async def tasksHandling():
        if db.isTaskEnabled("stockinform"):
            if not sendStocksRundown.is_running():
                sendStocksRundown.start()
                print("[INFO] Stock rundown has been enabled!")
        else:
            if sendStocksRundown.is_running():
                sendStocksRundown.stop()
                print("[INFO] Stock rundown has been disabled..")

        if db.isTaskEnabled("tft"):
            if not analyzeMatchHistoryTFT.is_running():
                analyzeMatchHistoryTFT.start()
                print("[INFO] TFT match history analysis has been enabled!")
        else:
            if analyzeMatchHistoryTFT.is_running():
                analyzeMatchHistoryTFT.stop()
                print("[INFO] TFT match history analysis has been disabled..")
        
        if db.isTaskEnabled("birthday"):
            if not sendBirthdayInfo.is_running():
                sendBirthdayInfo.start()
                print("[INFO] Birthday handling has been enabled!")
        else:
            if sendBirthdayInfo.is_running():
                sendBirthdayInfo.stop()
                print("[INFO] Birthday handling has been disabled..")

        if db.isTaskEnabled("heist"):
            if not freePeopleFromPrison.is_running():
                freePeopleFromPrison.start()
            if not manageHeist.is_running():
                manageHeist.start()
                print("[INFO] Heist has been enabled!")
        else:
            if freePeopleFromPrison.is_running():
                freePeopleFromPrison.stop()

            if manageHeist.is_running():
                manageHeist.stop()
                print("[INFO] Heist has been disabled..")    

        if db.isTaskEnabled("dailywinner"):
            if not generateWinnerAndLoser.is_running():
                generateWinnerAndLoser.start()
                print("[INFO] Daily winner has been enabled!")
        else:
            if generateWinnerAndLoser.is_running():
                generateWinnerAndLoser.stop()
                print("[INFO] Daily loser has been disabled..")

        if db.isTaskEnabled("channelpoints"):
            if not checkChannelActivityAndAwardPoints.is_running():
                checkChannelActivityAndAwardPoints.start()
                print("[INFO] Channel activity check has been enabled!")
        else:
            if checkChannelActivityAndAwardPoints.is_running():
                checkChannelActivityAndAwardPoints.stop()
                print("[INFO] Channel activity check has been disabled..")

        if db.isTaskEnabled("stocks"):
            if not generateStocks.is_running():
                generateStocks.start()

            if not simulateStockTrends.is_running():
                simulateStockTrends.start()

            if not updateStockPrices.is_running():
                updateStockPrices.start()
                print("[INFO] Stock investment is enabled!")
        else:
            if generateStocks.is_running():
                generateStocks.stop()

            if simulateStockTrends.is_running():
                simulateStockTrends.stop()

            if updateStockPrices.is_running():
                updateStockPrices.stop()
                print("[INFO] Stock investment is disabled..")

        if db.isTaskEnabled("theatres"):
            if not theatreCheck.is_running():
                theatreCheck.start()
                print("[INFO] Theatre check is enabled!")
        else:
            if theatreCheck.is_running():
                theatreCheck.stop()
                print("[INFO] Theatre check is disabled..")
    @bot.event
    async def on_ready():
        #bot.add_view(embedgen.ruletaView())
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=os.environ["PROD_STATUS"]))
        print("[INFO] " + f'{bot.user} is now running!')
        if os.environ["PROD_STATUS"] == "PRODUCTION":
            #in this function we'll enable / disable tasks based on what we have in DB
            if not tasksHandling.is_running():
                tasksHandling.start()
            
        
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
                elapsed_time = datetime.now() - user_cooldowns[user_id]
                if elapsed_time < timedelta(seconds=cooldown_time):
                    remaining_time = timedelta(seconds=cooldown_time) - elapsed_time
                    await message.channel.send(f"⏳ {message.author.mention}, nie spamuj! Możesz użyć bota za {remaining_time.total_seconds():.2f} sekund!")
                    return
                
                
            if userMessage == "!triggerheist" and int(message.author.id) == 326259887007072257:
                if manageHeist.is_running():
                    manageHeist.stop()
                    await triggerHeist(bot.get_channel(DEFAULT_HEIST_CHANNEL))
                    await asyncio.sleep(300)
                    manageHeist.start()
                return

            user_cooldowns[user_id] = datetime.now()
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
        currData = str(datetime.now().strftime('%Y-%m-%d %H:%M'))
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
