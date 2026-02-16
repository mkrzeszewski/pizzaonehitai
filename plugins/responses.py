import random
import plugins.weather as weather
import plugins.horoscope as horoskop
import plugins.pizzadatabase as db
import plugins.embedgen as embedgen
from plugins.embedgen import StocksGen, UtilityEmbedGen, BaseEmbedGen, HoroscopeEmbedGen, HeistEmbedGen, GambleEmbedGen
import plugins.pubfinder as pubfinder
import plugins.points as points
import plugins.gifgenerator as gif
import plugins.birthday as birthday
import plugins.ai as ai
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import plugins.stocks as stocks
import asyncio
from datetime import datetime
import re
from discord import Embed, Colour, ui, ButtonStyle, Interaction, NotFound, File, Member, User

#to be moved to slots.py?
MAX_SLOT_AMOUNT = 5000

#when user is tagged in dc, i.e. @roLab this is the re to check for that ID
TAG_PATTERN = re.compile(r'<@!?(\d+)>')

#for keyword mapping
ROUTING_TABLE = {}
securityResponse = "<:police:1343736194546274394> Nie masz prawa do uzywania tej komendy. Incydent bezpieczenstwa zostal zgloszony."
restaurantKeywords = ["restauracja", "bar", "znajdzbar", "gdziejemy", "jemy"]
helpKeyword = ["help", "?", "??", "pomoc", "tutorial", "kurwapomocy", "test"]
begKeyword = ["wyzebraj", "zebraj", "dejno", "prosze", "grubasiedawajpunkty", "kurwodawajpunkty", "kierowniku", "beg"]
aiKeyword = ["ai", "chatgpt", "gemini"]
horoskopKeyword = ["horoskop", "zodiak", "mojznak", "fortuna", "starszapani"]
quoteKeyword = ["quote", "cytat", "zanotuj", "cytuje"]
rewardKeyword = ["rewards", "nagrody", "prizes", "pocopunkty", "wydaj", "wymien"]
achievementKeyword = ["achievements", "achievement", "achivements", "osiagniecia", "puchary", "gwiazdy"]
slotsKeyword = ["slots", "slot", "automaty", "zakrec", "jeszczeraz"]
heistKeyword = ["joinheist", "dolacz", "wjezdzam" , "jazda"]
transferKeyword = ["transfer", "masz", "tip", "trzymaj", "maszbiedaku"]
escapeKeyword = ["wykup", "free", "wypuscmnie", "dzwoniepopapuge", "chceadwokata", "letmeout"]
freeKeyword = ["wypusc", "uwolnij", "lethimout"]
arrestKeyword = ["arrest", "aresztuj", "dopierdla", "wyrok", "zamknij"]
stocksKeyword = ["stocks", "stonks", "invest", "gielda", "rynek", "stoki", "wykres"]
sellStockKeyword = ["sellstock", "sell", "sprzedaj", "sellstocks", "out"]
buyStockKeyword = ["buystock", "purchasestock", "buy", "kup", "inwestuj", "invest"]

#embed classes section
_defaultEmbedGen = BaseEmbedGen()
_stockEmbedGen = StocksGen()
_utilityEmbedGen = UtilityEmbedGen()
_horoscopeEmbedGen = HoroscopeEmbedGen()
_heistEmbedGen = HeistEmbedGen()
_gambleEmbedGen = GambleEmbedGen()

#this is main body of this module - it performs manual if check depending on my widzimisie
async def handleResponse(userMessage, author, dcbot = None) -> str:
    reloadCommands()
    returnEmbed, returnView, returnFile, returnText = None, None, None, ""
    userAvatarURL = ""
    message = userMessage[1:]
    commands = message.split(" ")
    user = db.retrieveUser('discord_id', str(author))
    if user == None:
        returnText = "User o ID: " + str(author) + " nie znajduje sie w bazie danych. Uderz do roLab."
        return returnEmbed, returnText, returnView, returnFile
    else:
        tempUser = await dcbot.fetch_user(int(user['discord_id']))
        userAvatarURL = tempUser.avatar.url if tempUser.avatar else tempUser.default_avatar.url

    random.seed(datetime.now().timestamp())
    #esnure it matches the command even if its in lower
    commands[0] = str(commands[0].lower())

    trigger = userMessage[1:].split()[0].lower() # "tip"
    args = userMessage.split()[1:]               # ["@roLab", "500"]
    
    route = ROUTING_TABLE.get(trigger)
    if not route:
        return None, f"Nie znam komendy: {trigger}", None, None
    if user['arrested'] and commands[0] in escapeKeyword:
        if int(user['points']) < 300:
            returnText = "Masz za malo pizzopunktow! Minimalna ilosc do zaplaty to 300! Obecnie masz " + str(user['points']) + "!"
        else:
            if int(user['points']) >= 300 and int(user['points']) < 600:
                cost = -300
            else:
                cost = int(int(user['points']) * -0.5)
            points.addPoints(user['discord_id'], cost)
            returnEmbed = embedgen.generateFreedUser(user, int(cost * -1))
            db.freeUser('discord_id',user['discord_id'])
        return returnEmbed, returnText, returnView, returnFile
    elif user['arrested']:
        returnEmbed = embedgen.generateUserArrestedInfo(user)
        return returnEmbed, returnText, returnView, returnFile
    elif not user['arrested'] and commands[0] in escapeKeyword:
        returnText = "Nie jestes obecnie aresztowany."
    
    if route:
        module = route['module']
        action = route['action']
        if module == "stocks":
            return await handleStocksModule(action, args, user, dcbot, userAvatarURL)
        elif module == "utility":
            return await handleUtilityModule(action, args, user, dcbot, userAvatarURL)
        elif module == "economy":
            return await handleGambleModule(action, args, user, dcbot, userAvatarURL)
        elif module == "ai":
            return await handleAIModule(action, args, user, dcbot, userAvatarURL)
        elif module == "heist":
            return await handleHeistModule(action, args, user, dcbot, userAvatarURL)
        elif module == "admin":
            return await handleAdminModule(action, args, user, dcbot, userAvatarURL)
            

    ######################################### wszystko ponizej - do kosza
    #komendy wielokomendowe
    # if len(commands) > 1:
    #     #analyze league of legends match - need proper ID, example: EUN1_3498132354
    #     if commands[0] == "analyzelol":
    #         if re.search(r'euw1_\d+|eun1_\d+',commands[1]):
    #             results, players = leagueapi.analyzeMatch(leagueapi.getMatchData(str(commands[1])), False)
    #             if len(results) > 0 :
    #                 returnEmbed = embedgen.generateEmbedFromLeagueMatch(results,players,commands[1])
    #             else:
    #                 print(results)
    #         else:
    #             returnText = "kolego, podaj poprawny ID, np: EUN1_3498132354"

    #     #analyze TFT match - need proper ID, example: EUN1_3742603881
    #     elif commands[0] == "analyzetft":
    #         if re.search(r'euw1_\d+|eun1_\d+',commands[1]):
    #             date, results, players = tftapi.analyzeMatch(tftapi.getMatchData(str(commands[1])), False)
    #             if len(results) > 0 :
    #                 returnEmbed = embedgen.generateEmbedFromTFTMatch(results,players,commands[1], date)
    #         else:
    #             returnText = "kolego, podaj poprawny ID, np: EUN1_3742603881"

    #     #find proper pub to meet together (NEEDS WORK)
    #     elif commands[0] in restaurantKeywords:
    #         if len(commands) == 2:
    #             if str(commands[1]).isdigit():
    #                 embed_buttons = usersChooseView(db.retrieveAllUsers(), int(str(commands[1])))
    #                 returnView = embed_buttons.generate_view()
    #                 returnEmbed = embed_buttons.generate_embed()#embedgen.generateEmbedFromRestaurant(pubfinder.chooseRestaurant(),["rolab", "bartus", "fifi"])

    #     elif commands[0] in aiKeyword:
    #         query = message[3:]
    #         db.insertAIHistory(str(author), query)
    #         text = ""
    #         returnEmbed = embedgen.generateAIResponse(query, ai.chatWithAI(query))

    #     elif commands[0] in heistKeyword:
    #         if len(commands) == 2:
    #             if db.isHeistAvailable():
    #                 if str(commands[1]).isdigit():
    #                     curr = int(user['points'])
    #                     amount = int(str(commands[1]))
    #                     if curr >= amount and amount >= 200:
    #                         if (db.isUserPartOfCurrentHeist(user['name'])):
    #                             returnText = "Jestes juz czlonkiem aktualnego napadu!"
    #                         else:
    #                             db.appendHeistMember(user['name'], amount)
    #                             points.addPoints(str(author), -1 * amount)
    #                             returnText = "Pomyslnie dolaczyles do napadu!"
    #                     else:
    #                         returnText = "Masz za malo pizzopunktow - obecnie posiadasz: " + str(user['points']) + "! Min: 200 PPKT."
    #                 else:
    #                     returnText = "Musisz obstawic liczbe naturalna (dodatnia!)"
    #             else:
    #                 returnText = "Obecnie nie mozesz dolaczyc do napadu!"

    #     elif commands[0] in slotsKeyword:
    #         if len(commands) == 2:
    #             if str(commands[1]).isdigit():
    #                 curr = int(user['points'])
    #                 amount = int(str(commands[1]))
    #                 if amount > 5000:
    #                     returnText = "Maksymalna wysokosc zakladu w slotsach to : " + str(MAX_SLOT_AMOUNT) + "."
    #                 else:
    #                     if curr >= amount and amount >= 5:
    #                         returnEmbed, returnFile = generateSlots(amount, user)
    #                     else:
    #                         returnText = "Za malo pizzopunktow (min to 5!) - obecnie posiadasz: " + str(user['points']) + "!"
    #             else:
    #                 returnText = "Musisz obstawic liczbe naturalna (dodatnia!)"

    #     elif commands[0] == "gamble" or commands[0] == "gamba" or commands[0] == "yolo":
    #         if len(commands) == 2:
    #             if str(commands[1]) or str(commands[1]) == "all":
    #                 amount = 0
    #                 if str(commands[1]).isdigit():
    #                     amount = int(str(commands[1]))
    #                 curr = int(user['points'])
    #                 if str(commands[1]) == "all":
    #                     amount = curr
    #                 min = int(curr * 0.1)
    #                 if curr >= amount and amount >= int(curr * 0.1) and amount >= 25:
    #                     result = random.randint(1,2)
    #                     if result == 1:
    #                         curr = curr + amount
    #                         returnText = "Nice! +" + str(amount) + " pizzapkt! (obecnie masz : " + str(curr) + ") <:ez:1343529006162772028>"
    #                     else:
    #                         curr = curr - amount
    #                         returnText = "Oops.. -" + str(amount) + " pizzapkt! (obecnie masz : " + str(curr) + ") <:pepecopium:1094185065925333012>"
    #                     db.updateUser('discord_id', str(author), 'points', curr)
    #                 else:
    #                     returnText = "Za malo pizzopunktow (minimalna ilosc na gre to 10% (lub 25 gdy jestes biedakiem) pizzopunktow!) - obecnie posiadasz: " + str(user['points']) + "!"
    #             else:
    #                 returnText = "Musisz obstawic liczbe naturalna (dodatnia!)"

    #     elif commands[0] == "setpoints" or commands[0] == "set":
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             if len(commands) == 3:
    #                 if str(commands[2]).isdigit():
    #                     returnText = db.updateUser('discord_id', str(commands[1]), 'points', int(commands[2]))
    #                 else:
    #                     returnText = "ERROR: ostatnia wartosc to musi byc int!"
    #             else:
    #                 returnText = "Niepoprawnie uzyta komenda. Uzyj np !set 326259887007072257 20"
    #         else:
    #             returnText = securityResponse

    #     elif commands[0] in arrestKeyword:
    #         if user['role'] == "owner":# or user['role'] == "admin":
    #             if len(commands) == 2:
    #                 if str(commands[1]).isdigit():
    #                     if db.arrestUser('discord_id', str(commands[1])):
    #                         returnText = "Pomyslnie zaaresztowano " + str(commands[1]) + "."
    #                     else:
    #                         returnText = "Nieznany user : " + str(commands[1]) + "."
    #                 else:
    #                     if db.arrestUser('name', str(commands[1])):
    #                         returnText = "Pomyslnie zaaresztowano " + str(commands[1]) + "."
    #                     else:
    #                         returnText = "Nieznany user : " + str(commands[1]) + "."
    #             else:
    #                 returnText = "Niepoprawnie uzyta komenda. Uzyj np !arrest 326259887007072257"
    #         else:
    #             returnText = securityResponse

    #     elif commands[0] in freeKeyword:
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             if len(commands) == 2:
    #                 arrested_user = userFromPattern(commands[1])
    #                 if arrested_user:
    #                     if db.freeUser('discord_id', str(arrested_user['discord_id'])):
    #                         returnText = "Pomyslnie wypuszczono " + str(commands[1]) + "."
    #                 else:
    #                     returnText = "Nieznany user : " + str(commands[1]) + "."
    #             else:
    #                 returnText = "Niepoprawnie uzyta komenda. Uzyj np !uwolnij 326259887007072257"
    #         else:
    #             returnText = securityResponse

    #     elif commands[0] in transferKeyword:
    #         if len(commands) == 3:
    #             if str(commands[2]).isdigit():
    #                 if(int(commands[2]) <= int(user['points'])):
    #                     dest_user = userFromPattern(commands[1])
    #                     if dest_user:
    #                         if dest_user != user:
    #                             points.transferPoints(str(author), dest_user['discord_id'], int(commands[2]))
    #                             returnText = "Pomyslnie przetransferowano " + str(commands[2]) + " pizzopunktow do uzytkownika " + dest_user['name'] + "."
    #                         else:
    #                             returnText = "Nie mozesz przelac Sobie punktow!"
    #                     else:
    #                         returnText = "Nieznany user : " + str(commands[1]) + "."
    #                 else:
    #                     returnText = "Mozesz dac tylko tyle ile masz!"
    #             else:
    #                 returnText = "ERROR: ostatnia wartosc to musi byc int!"
    #         else:
    #             returnText = "Niepoprawnie uzyta komenda. Uzyj np !tip Mati 20"

    #     elif commands[0] == "add":
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             if len(commands) == 3:
    #                 if str(commands[2]).isdigit():
    #                     dest_user = userFromPattern(commands[1])
    #                     if dest_user:
    #                         points.addPoints(dest_user['discord_id'], int(commands[2]))
    #                         returnText = "Pomyslnie dodano " + str(commands[2]) + " pizzopunktow do uzytkownika " + dest_user['name'] + "."
    #                     else:
    #                         returnText = "Nieznany user : " + str(commands[1]) + "."
    #                 else:
    #                     returnText = "ERROR: ostatnia wartosc to musi byc int!"
    #             else:
    #                 returnText = "Niepoprawnie uzyta komenda. Uzyj np !add Bartolo 20"
    #         else:
    #             returnText = securityResponse

    #     elif commands[0] == "instructai":
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             if len(commands) > 1:
    #                 db.insertAIInstruction(message[12:])
    #                 ai.resetModel()
    #         else:
    #             returnText = securityResponse


    #     elif commands[0] == "setriotkey":
    #         if user['role'] == "owner":# or user['role'] == "admin": and len(commands) == 2:
    #             tftapi.setAPIKey(commands[1])
    #             returnText = "API Key successfuly replaced"

    #     elif commands[0] == "testmessage":
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             print(commands)
    #             print(message)
    #             returnText = message

    #     elif commands[0] == "birthdaytest":
    #         if user['role'] == "owner":# or user['role'] == "admin": and len(commands) == 2:
    #             user = userFromPattern(commands[1])
    #             if user:
    #                 returnEmbed, returnText = getBirthdayStuff(str(commands[1]))
    #             else:
    #                 returnText = "nie znaleziona usera o ID = " + str(commands[1])

    #     elif commands[0] == "top":
    #         if len(commands) == 2:
    #             if str(commands[1]).isdigit():
    #                 amount = int(str(commands[1]))
    #                 users = points.getTop(amount)
    #                 if users:
    #                     returnEmbed = embedgen.generateTopPointsEmbed(users, amount)

    #     elif commands[0] == "topstocks":
    #         if len(commands) == 2:
    #             if str(commands[1]).isdigit():
    #                 if int(str(commands[1])) > 1:
    #                     amount = int(str(commands[1]))
    #                     _stocks = db.retrieveTopStocks(amount)
    #                     if _stocks:
    #                         returnEmbed = embedgen.generateStocksOverview(_stocks)
    #                     else:
    #                         returnText = "Currently there's no stock value."

    #     elif commands[0] == "bottomstocks":
    #         if len(commands) == 2:
    #             if str(commands[1]).isdigit():
    #                 if int(str(commands[1])) > 1:
    #                     amount = int(str(commands[1]))
    #                     _stocks = db.retrieveBottomStocks(amount)
    #                     if _stocks:
    #                         returnEmbed = embedgen.generateBottomStocks(_stocks)
    #                     else:
    #                         returnText = "Currently there's no stock value."

    #     elif commands[0] == "bottom":
    #         if len(commands) == 2:
    #             if str(commands[1]).isdigit():
    #                 amount = int(str(commands[1]))
    #                 users = points.getBottom(amount)
    #                 if users:
    #                     returnEmbed = embedgen.generateBottomPointsEmbed(users, amount)

    #     elif commands[0] == "roll":
    #         if len(commands) == 2:
    #             returnText = "Losujemy: 1 - " + commands[1] + " -> " + str(random.randint(1,int(commands[1])))
    #         elif len(commands) == 3:
    #             returnText = "Losujemy: " + commands[1] + " - " + commands[2] + " -> " + str(random.randint(int(commands[1]),int(commands[2])))

    #     elif commands[0] == "enabletask" or commands[0] == "enable":
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             if len(commands) > 1:
    #                 taskName = str(commands[1])
    #                 task = db.retrieveTask('name', taskName)
    #                 if task:
    #                     db.enableTask(str(commands[1]))
    #                     returnText = "Enabled task \"" + taskName + "\"."
    #                 else:
    #                     returnText = "No task found = \"" + taskName + "\"."
    #         else:
    #             returnText = securityResponse
        
    #     elif commands[0] == "disabletask" or commands[0] == "disable":
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             if len(commands) > 1:
    #                 taskName = str(commands[1])
    #                 task = db.retrieveTask('name', taskName)
    #                 if task:
    #                     db.disableTask(str(commands[1]))
    #                     returnText = "Disabled task \"" + taskName + "\"."
    #                 else:
    #                     returnText = "No task found = \"" + taskName + "\"."
    #         else:
    #             returnText = securityResponse

    #     elif commands[0] in buyStockKeyword:
    #         if len(commands) > 2:
    #             stockSymbol = str(commands[1]).upper()
    #             amount = int(commands[2])
    #             stock = db.retrieveStock('symbol',stockSymbol)
    #             if amount > 0:
    #                 if user and stock:
    #                     success, msg = stocks.purchaseStocks(user['name'], stockSymbol, amount)
    #                     if success:
    #                         returnEmbed = embedgen.generateUserStockPurchase(user, stock, msg)
    #                     else:
    #                         returnText = msg
    #                 else:
    #                     returnText = "Stock " + str(stockSymbol) + " not found."
    #             else:
    #                 returnText = "Nie mozesz sprzedac negatywnych ilosci akcji"
    #         else:
    #             returnText = "Prosze podac symbol oraz ilosc akcji ktore chcesz kupic! Np. !purchasestock MMM 5.\nW celu zweryfikowania jakie akcje sa na rynku - !stonks"

    #     elif commands[0] in sellStockKeyword:
    #         if len(commands) > 2:
    #             stockSymbol = str(commands[1]).upper()
    #             amount = int(commands[2])
    #             stock = db.retrieveStock('symbol',stockSymbol)
    #             if amount > 0:
    #                 if stock:
    #                     success, msg = stocks.sellStocks(user['name'], stockSymbol, amount)
    #                     if success:
    #                         returnEmbed = embedgen.generateUserStockSale(user, stock, msg)
    #                     else:
    #                         returnText = msg
    #                 else:
    #                     returnText = "Stock " + str(stockSymbol) + " not found."
    #             else:
    #                 returnText = "Nie mozesz sprzedac negatywnych ilosci akcji"
    #         else:
    #             returnText = "Prosze podac symbol oraz ilosc akcji ktore chcesz kupic! Np. !sellstock MMM 5.\nW celu zweryfikowania jakie akcje sa na rynku - !stonks\nPamietaj, ze przy sprzedazy pobierane jest 10% podatku!"

    #     elif commands[0] == "portfolio" or commands[0] == "flex":
    #         user = userFromPattern(commands[1])
    #         if user:
    #             flexUser = await dcbot.fetch_user(int(user['discord_id']))
    #             flexAvatar = flexUser.avatar.url if flexUser.avatar else flexUser.default_avatar.url
    #             returnEmbed = embedgen.generateUserPortfolioEmbed(user, flexAvatar)
    #         else:
    #             returnText = "User " + str(commands[1]) + "not found."
    # else:

    #     #if its a singular commmand - transform message to lower.
    #     message = message.lower()
    #     if message == 'whoami' or message == 'kimjestem' or message == 'ktoja':
    #         returnText =  db.retrieveUser('discord_id', str(author))['name']

    #     if message == "points":
    #         if user:
    #             returnText = user['name'] + " - masz: " + str(user['points']) + " pizzapoints."

    #     if message == 'roll':
    #         returnText =  str(random.randint(1,6))

    #     if message == 'embed':
    #         returnText =  "embed_test"

    #     if message == 'ai':
    #         returnText =  "zapytaj o cos, np !ai daj przepis na nalesniki!"

    #     if message in escapeKeyword:
    #         returnText = "Nie jest obecnie aresztowany!"

    #     if message == "ktosiedzi":
    #         returnEmbed = embedgen.generateArrestedUsersInfo(db.retrieveArrestedUsers())

    #     if message in slotsKeyword:
    #         if user:
    #             curr = int(user['points'])
    #             amount = 5
    #             if curr >= amount and amount > 0:
    #                 returnEmbed, returnFile = generateSlots(amount, user)
    #             else:
    #                 returnText = "Za malo pizzopunktow - obecnie posiadasz: " + str(user['points']) + "!"

    #     if message == 'zacopunkty':
    #         returnText =  "Punkty mozna dostac za udzial w eventach, przebywaniu na voice chat, przy pomocy hazardu lub na widzimisie glownego admina."

    #     if message in rewardKeyword:
    #         returnEmbed = embedgen.generateRewards(db.retrieveRewards())

    #     if message in achievementKeyword:
    #         returnEmbed = embedgen.generateAchievements(db.retrieveAchievements())

    #     if message == 'resetai':
    #         returnText = securityResponse
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             ai.resetModel()
    #             returnText =  "AI zostal przywrocony do stanu pierwotnego."

    #     if message == "pogoda":
    #         returnText =  weather.getLodzWeather()

    #     if message in begKeyword:
    #         curr = int(user['points'])
    #         if curr < 100:
    #             if db.isBegAvailable():
    #                 db.updateUser('discord_id', str(author), 'points', 100)
    #                 db.createBegEntry(str(author))
    #                 returnText = "Ustawiono 100 ppkt dla " + user['name'] + ". Globalny cooldown - 10 min."
    #                 #isBegAvailable = False
    #             else:
    #                 begPerson = db.getBegPerson()
    #                 if begPerson:
    #                     returnText = "Cooldown! Sprobuj ponownie pozniej. Ostatnia szansa wykorzystana przez: " + str(begPerson['name']) + "."
    #         else:
    #             returnText = "Masz powyzej 100 ppkt. Opcja dostepna tylko dla najbiedniejszych z biednych."

    #     if message == "top5" or message == "top":
    #         amount = 5
    #         users = points.getTop(amount)
    #         if users:
    #             returnEmbed = embedgen.generateTopPointsEmbed(users, amount)
        
    #     if message == "bottom5" or message == "bottom":
    #         amount = 5
    #         users = points.getBottom(amount)
    #         if users:
    #             returnEmbed = embedgen.generateBottomPointsEmbed(users, amount)
        
    #     if message == "heistinfo" or message == "currentheist" or message == "napad":
    #         currHeist = db.retrieveHeistInfo()
    #         if currHeist:
    #             returnEmbed = embedgen.generateHeistInfo(currHeist['level'], currHeist['heist_name'],currHeist['when_starts'],currHeist['members'])

    #     if message in horoskopKeyword:
    #         name = db.retrieveUser('discord_id', str(author))['name']
    #         sign, text = horoskop.getHoroscopeForUser(user)
    #         returnEmbed = embedgen.generateEmbedFromHoroscope(text, sign, name)

    #     if message in restaurantKeywords:
    #         embed_buttons = usersChooseView(db.retrieveAllUsers(), 500)
    #         returnView = embed_buttons.generate_view()
    #         returnEmbed = embed_buttons.generate_embed()

    #     if message in helpKeyword:
    #         returnEmbed = _utilityEmbedGen.main_help()

    #     if message == "fullstonks" or message == "fullstocks" or message == "stocksoverview":
    #         _stocks = list(db.retrieveAllStocks())
    #         if len(_stocks) > 0:
    #             returnEmbed = embedgen.generateStocksOverview(_stocks)
    #         else:
    #             returnText = "Currently there's no stock value"
        
    #     if message == 'generatestocks':
    #         returnText = securityResponse
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             returnText = str(stocks.generateStocks())

    #     if message == 'generatetrends':
    #         returnText = securityResponse
    #         if user['role'] == "owner":# or user['role'] == "admin"::
    #             stocks.simulateTrends()
    #             returnText = "Przeprowadzono generacje trendow dla stockow."

    #     if message in stocksKeyword:
    #         _stocks = list(db.retrieveTopStocks(100))
    #         if len(_stocks) > 0:
    #             returnEmbed = embedgen.generateFullStonks(_stocks)

    #     if message == "cashout" or message == "imout":
    #         success, msg = stocks.cashout(user['name'])
    #         if success:
    #             returnEmbed = embedgen.generateUserStockCashout(user, msg)
    #         else:
    #             returnText = msg

    #     if message == "portfolio" or message == "flex" or message == "mystocks" or message == "mystonks":
    #         returnEmbed = embedgen.generateUserPortfolioEmbed(user, userAvatarURL)

    #     if message == "testbankrupcy":
    #         _stock = db.retrieveStock('ceo',user['name'])
    #         if _stock:
    #             returnEmbed = embedgen.generateBankrupcy(_stock, userAvatarURL)
        
    #     if message == "stockupdate" or message == "stockrundown":
    #         msg = stocks.informOnStocksUpdate()
    #         returnEmbed = embedgen.generateStocksRundown(msg)

    #     if message in buyStockKeyword:
    #         returnText = "Prosze podac symbol oraz ilosc akcji ktore chcesz kupic! Np. !buy MMM 5.\nW celu zweryfikowania jakie akcje sa na rynku - !stonks"

    #     if message in sellStockKeyword:
    #         returnText = returnText = "Prosze podac symbol oraz ilosc akcji ktore chcesz kupic! Np. !sell MMM 5.\nW celu zweryfikowania jakie akcje sa na rynku - !stonks\nPamietaj, ze przy sprzedazy pobierane jest 10% podatku!"

    return returnEmbed, returnText, returnView, returnFile

######################################### wszystko wyzej - do kosza

###################Utility

#view in discord to choose which users in discord You want to include in query - at the moment used for pubfinder plugin
class usersChooseView:
    def __init__(self, users, radius):
        self.users = users
        self.selectedUsers = []
        self.sent_messages = []
        self.radius = radius

    def generate_embed(self):
        embed = Embed(title="Wybor uzytkownik", description="Wybierz uzytkownikow, dla ktorych obliczyc mamy do ktorej knajpy sie udac!:", color=Colour.blue())
        return embed

    def generate_view(self):
        """Dynamically creates a view with buttons based on users."""
        view = ui.View()
        for user in self.users:
            button = ui.Button(label=user['name'], style=ButtonStyle.primary)
            button.callback = self.create_callback(user)
            view.add_item(button)

        button = ui.Button(label="OK", style=ButtonStyle.success)
        button.callback = self.create_finish_callback()
        view.add_item(button)

        return view

    def create_callback(self, user):
        async def callback(interaction: Interaction):
            await interaction.response.defer()
            message = await interaction.followup.send(f"You selected {user['name']}.")
            self.sent_messages.append(message)
            self.selectedUsers.append(user)
        return callback
    
    def create_finish_callback(self):
        async def callback(interaction: Interaction):
            if self.sent_messages:
                for message in self.sent_messages:
                    if message:
                        try:
                            await message.delete() 
                        except NotFound:
                            pass
            userListString = " ".join([user['name'] for user in self.selectedUsers])
            await interaction.message.delete()
            await interaction.channel.send(f"Wybrane osoby: {userListString}.")
            await interaction.channel.send(embed = embedgen.generateEmbedFromRestaurant(pubfinder.chooseRestaurant(self.selectedUsers, radius = self.radius)))
        return callback
icons = ["pizza", "skull", "apple", "grill", "juicer", "bike", ""]

def simulateSlots(amount, tries, user):
    multiplier = 3
    earnings = 0
    for _ in range(tries):
        spinResult = random.choices(icons, k=3)
        count = len(set(spinResult))
        if count > 1:
            if count == 3:
                multiplier = 15
            #remove assets/gif and .png from string
            winner = winner[11:-4]
            if list(set(spinResult))[0] == "pizza":
                multiplier *= 3
            elif list(set(spinResult))[0] == "skull":
                multiplier *= -2

            earnings = int(amount * multiplier)
            points.addPoints(user['discord_id'], earnings)
            db.updateSlotEntry(id, earnings - amount)
    #in case of skulls
    if multiplier < 0:
        earnings = earnings - amount

def generateSlots(amount, user):
    multiplier = 3
    earnings = amount * -1
    points.addPoints(user['discord_id'], earnings)
    id = db.insertSlotsEntry(amount, user['discord_id'])
    output_path = "assets/gif/slot_machine" + str(id) + ".gif"
    winner, count = gif.create_slot_machine_gif(frames = 120, output_path = output_path)
    if count > 1:

        #remove assets/gif and .png from string
        winner = winner[11:-4]

        if winner == "pizza":
            multiplier *= 2
        elif winner == "skull":
            multiplier *= -2
        if count == 3:
            multiplier *= 5
            if winner == "skull":
                #game over
                multiplier *= 21372137
                #gg
        earnings = int(amount * multiplier)
        points.addPoints(user['discord_id'], earnings)
        db.updateSlotEntry(id, earnings - amount)
    #in case of skulls
    if multiplier < 0:
        earnings = earnings - amount
    return _gambleEmbedGen.generate_slots_animation(id, output_path, earnings, user)
    #return embedgen.generateSlotsAnimation(id, output_path, earnings, user)

def getWeather():
    return weather.getLodzWeather()

#this takes a discord_id and generates some info about that persons birthday, also wishes him a happy birthday!
def getBirthdayStuff(user):
    returnEmbed = None
    returnText = ""
    if user:
        facts = []
        facts.append(ai.askAI("Wygeneruj smieszny, interesujacy fakt o tym, co wydarzylo sie w dniu " + birthday.transform_date(user['birthday'])))
        facts.append(ai.askAI("przetlumacz to na polski : "+birthday.getFloridaMan(user['birthday'])))
        wrozba = str(ai.askAI("Wylosuj liczbe od 1 do 10 i w zaleznosci od wylosowanej liczby - wygeneruj krotka zartobliwa wrozbe niczym z chinskich ciasteczek jak bedzie wygladal caly nastepny rok dla danej osoby (1 - katastrofalnie, najgorzej jak sie da, 10 - genialnie) Nie informuj jaka liczbe wylosowales, przeslij tylko przepowiednie."))
        returnEmbed = embedgen.generateBirthdayEmbed(user, facts, wrozba)
        points.addPoints(str(user['discord_id']), 5000)
    return returnEmbed, returnText

def userFromPattern(pattern):
    match = TAG_PATTERN.search(pattern)
    if match:
        user = db.retrieveUser('discord_id',match.group(1))
        if user:
            return user
    user = db.retrieveUser('discord_id',str(pattern))
    if user:
        return user
    
    user = db.retrieveUser('name',str(pattern))
    if user:
        return user
    return None

async def targetUser(dcbot, target):
    temp_user = userFromPattern(target)
    target_user = None
    target_avatar = None
    if temp_user:
        target_user = temp_user
        try:
            flex_user = await dcbot.fetch_user(int(target_user['discord_id']))
            target_avatar = flex_user.avatar.url if flex_user.avatar else flex_user.default_avatar.url
        except Exception:
            target_avatar = ""
    return target_user, target_avatar

def reloadCommands():
    global ROUTING_TABLE
    ROUTING_TABLE = {}
    docs = db.retrieveAllCommandsKeywords()
    for doc in docs:
        for keyword in doc['keywords']:
            # Map "tip" -> {"module": "economy", "action": "transfer"}
            ROUTING_TABLE[keyword.lower()] = {
                "module": doc['module'], 
                "action": doc['action']
            }

async def handleAdminModule(action, args, user, dcbot, avatarUrl):
    returnEmbed, returnView, returnFile, returnText = None, None, None, ""
    if user.get('role') != "owner":
        return None, securityResponse, None, None

    if not args:
        return None, f"Musisz podać użytkownika! Przykład: `!{action} @roLab`", None, None
    
    target_pattern = args[0]
    target_user_db = userFromPattern(target_pattern)

    if not target_user_db:
        return None, f"❌ Nie znaleziono użytkownika: `{target_pattern}`.", None, None
    if action == "arrest":
        if db.arrestUser('discord_id', str(target_user_db['discord_id'])):
            returnEmbed = _utilityEmbedGen.arrest_result(target_user_db, user['name'])
        else:
            returnText = f"❌ Błąd podczas aresztowania {target_user_db['name']}."

    elif action == "free_user":
        if db.freeUser('discord_id', str(target_user_db['discord_id'])):
            returnEmbed = _utilityEmbedGen.free_result(target_user_db, user['name'])
        else:
            returnText = f"❌ Błąd podczas uwalniania {target_user_db['name']}."

    return returnEmbed, returnText, returnView, returnFile

async def handleHeistModule(action, args, user, dcbot, avatarUrl):
    returnEmbed, returnView, returnFile, returnText = None, None, None, ""

    if action == "join":
        if not db.isHeistAvailable():
            return None, "🛑 Obecnie nie ma żadnego aktywnego planu napadu.", None, None

        if not args or not str(args[0]).isdigit():
            return None, "❌ Podaj kwotę! Użycie: `!heist join 500`", None, None
        
        amount = int(args[0])
        curr_points = int(user.get('points', 0))

        if amount < 200:
            return None, "❌ Minimalny wkład w napad to `200` pkt.", None, None

        if curr_points < amount:
            return None, f"❌ Nie masz tyle punktów! (Masz: `{curr_points:,}`)", None, None

        if db.isUserPartOfCurrentHeist(user['name']):
            return None, "👀 Już jesteś w ekipie na ten skok!", None, None

        db.appendHeistMember(user['name'], amount)
        points.addPoints(str(user['discord_id']), -amount)
        
        returnEmbed = _heistEmbedGen.join_success(user, amount)

    elif action == "heistinfo":
        currHeist = db.retrieveHeistInfo()
        if currHeist:
            returnEmbed = _heistEmbedGen.heist_info(
                currHeist['level'], 
                currHeist['heist_name'], 
                currHeist['when_starts'], 
                currHeist['members']
            )
        else:
            returnText = "🕵️‍♂️ Wywiad donosi, że na razie nie ma żadnego banku do obrobienia."

    return returnEmbed, returnText, returnView, returnFile

async def handleAIModule(action, args, user, dcbot, avatarUrl):
    returnEmbed, returnView, returnFile, returnText = None, None, None, ""
    if action == "resetai":
        if user.get('role') != "owner":
            ai.resetModel()
            returnText =  "👌AI zostal przywrócony do stanu pierwotnego."
        else:
            return None, securityResponse, None, None
    elif action == "chat":
        query = " ".join(args)
        db.insertAIHistory(str(user['name']), query)
        returnEmbed = embedgen.generateAIResponse(query, ai.chatWithAI(query))
    return returnEmbed, returnText, returnView, returnFile


async def handleUtilityModule(action, args, user, dcbot, avatarUrl):
    returnEmbed, returnView, returnFile, returnText = None, None, None, ""
    target_user = user
    target_avatar = avatarUrl

    if action == "help":
        returnEmbed = _utilityEmbedGen.main_help()
    elif action == "quote":
        returnText = "Funkcja cytatu poki co nie dziala."
    elif action == "setpoints":
        if user.get('role') != "owner":
            return None, securityResponse, None, None

        if len(args) < 2:
            return None, "Użycie: `!set [user] [nowa_kwota]`", None, None

        target_name = args[0]
        amount_str = args[1]

        if not amount_str.isdigit():
            return None, "Nowa wartość musi być liczbą dodatnią.", None, None

        new_amount = int(amount_str)
        dest_user = userFromPattern(target_name)
        if not dest_user:
            return None, f"Nie znaleziono użytkownika `{target_name}`.", None, None
        db.updateUser('discord_id', dest_user['discord_id'], 'points', new_amount)
        
        returnEmbed = _utilityEmbedGen.admin_set_points(dest_user, new_amount, user['name'])

    elif action == "addpoints":
        if user.get('role') != "owner":
            return None, securityResponse, None, None

        if len(args) < 2:
            return None, "Błędne użycie. Spróbuj: `!add [user] [ilość]`", None, None

        target_name = args[0]
        amount_str = args[1]

        if not amount_str.isdigit():
            return None, f"ERROR: `{amount_str}` to nie jest poprawna liczba całkowita!", None, None

        amount = int(amount_str)
        
        dest_user = userFromPattern(target_name)
        if not dest_user:
            returnText = f"Nieznany użytkownik: `{target_name}`."
            return None, returnText, None, None
        
        points.addPoints(dest_user['discord_id'], amount)
        returnEmbed = _utilityEmbedGen.admin_add_points(dest_user, amount, user['name'])
    elif action in ["enabletask", "disabletask"]:
        if user.get('role') != "owner":
            return None, securityResponse, None, None
        if not args:
            return None, f"Podaj nazwę zadania: `!{action} [nazwa_zadania]`", None, None

        task_name = args[0]
        task = db.retrieveTask('name', task_name)
        if not task:
            return None, f"🔍 Nie znaleziono zadania o nazwie: `{task_name}`.", None, None
        if action == "enabletask":
            db.enableTask(task_name)
            returnText = f"✅ Zadanie `{task_name}` zostało **włączone**."
        else:
            db.disableTask(task_name)
            returnText = f"🛑 Zadanie `{task_name}` zostało **wyłączone**."
    elif action == "whoami":
        returnEmbed = _defaultEmbedGen.neutral_msg("Dane o Tobie:", ai.askAI("Przesyłam Ci dane o użytkowniku, powiedz mu coś o nim i zarzuć mu jakąś ciekawostką." + str(user)))
    elif action == "roll":
        if args:
            if len(args) == 1:
                returnText = "Losujemy: 1 - " + args[0] + " -> " + str(random.randint(1, int(args[0])))
            elif len(args) == 2:
                returnText = "Losujemy liczbe pomiedzy " + args[1] + " - " + args[2] + " -> " + str(random.randint(int(args[0]), int(args[1])))
        else:
            returnText = "Losujemy liczbe pomiedzy 1 a 100 - > " + str(random.randint(1, 100))
    elif action == "beg":
        if int(user['points']) >= 100:
            returnText = f"❌ Masz {user['points']} pkt. To za dużo na zasiłek, ty chciwy sępie!"
            return None, returnText, None, None
        elif user['stocksOwned']:
            returnText = f"❌ Jesteś właścicielem akcji! Zapomoga jest dla najbiedniejszych, a nie inwestorów! Wstydź się!"
            return None, returnText, None, None
        if db.isBegAvailable():
            db.updateUser('discord_id', str(user['discord_id']), 'points', 100)
            db.createBegEntry(str(user['discord_id']))
            returnEmbed = _utilityEmbedGen.beggar_handout(user)
        else:
            begPerson = db.getBegPerson()
            who = begPerson['name'] if begPerson else "chuj wie"
            returnText = f"🛑 Kolejka po darmową kasę jest długa! Ostatni zasiłek wyłudził: **{who}**. Wróć za chwilę."
    elif action == "points":
        target_avatar = avatarUrl
        target_user = user
        if args:
            temp_user = userFromPattern(args[0])
            if temp_user:
                target_user = temp_user
                try:
                    flex_user = await dcbot.fetch_user(int(target_user['discord_id']))
                    target_avatar = flex_user.avatar.url if flex_user.avatar else flex_user.default_avatar.url
                except Exception:
                    target_avatar = ""
            else:
                returnText = f"Użytkownik {args[0]} nie został znaleziony w bazie."
        returnEmbed = _utilityEmbedGen.user_points(target_user, target_avatar)
    elif action in ["top", "bottom"]:
        amount = 10
        if args and args[0].isdigit():
            amount = int(args[0])
            amount = min(amount, 20)
        if action == "top":
            leader_data = points.getTop(amount)
        else:
            leader_data = points.getBottom(amount)
        if leader_data:
            returnEmbed = _utilityEmbedGen.leaderboards(leader_data, amount, action)
        else:
            returnText = "Nie udało się pobrać danych rankingu."
    elif action == "achievements":
        returnEmbed = _utilityEmbedGen.achievements(db.retrieveAchievements())
    elif action == "horoscope":
        if args:
            temp_user = userFromPattern(args[0])
            if temp_user:
                target_user = temp_user
        sign, text = horoskop.getHoroscopeForUser(target_user)
        returnEmbed = _horoscopeEmbedGen.horoscope(text, sign)
    elif action == "whoisarrested":
        returnEmbed = embedgen.generateArrestedUsersInfo(db.retrieveArrestedUsers())
    elif action == "restaurant":
        returnText = "Funkcja knajpy poki co nie dziala."
    elif action == "weather":
        returnEmbed = _defaultEmbedGen.neutral_msg("Pogoda: ", weather.getLodzWeather())

    return returnEmbed, returnText, returnView, returnFile

async def handleGambleModule(action, args, user, dcbot, avatarUrl):
    returnEmbed, returnView, returnFile, returnText = None, None, None, ""
    defaultTitle = "Ekonomia P1H"
    if action == "slots":
        MAX_SLOT_AMOUNT = 5000
        if not args:
            return None, "Podaj kwotę! Przykład: `!slots 500`", None, None

        amount_raw = args[0]
        if not amount_raw.isdigit():
            return None, "❌ Kwota musi być liczbą dodatnią!", None, None
        
        amount = int(amount_raw)
        curr_points = int(user.get('points', 0))

        # 2. Walidacja limitów i portfela
        if amount > MAX_SLOT_AMOUNT:
            return None, f"🚫 Maksymalny zakład w slotsach to `{MAX_SLOT_AMOUNT:,}` pkt.", None, None
        
        if amount < 5:
            return None, "🚫 Minimalny zakład to `5` pkt.", None, None

        if curr_points < amount:
            return None, f"❌ Nie masz tyle punktów! Twoje saldo: `{curr_points:,}` pkt.", None, None

        # 3. Wywołanie Twojej dedykowanej funkcji generującej
        # Zakładam, że generateSlots zajmuje się losowaniem, aktualizacją bazy i tworzeniem grafiki
        returnEmbed, returnFile = generateSlots(amount, user)

    elif action == "transfer":
        if len(args) < 2:
            return None, "Niepoprawnie użyta komenda. Użyj np: `!tip @roLab 20`", None, None

        target_raw = args[0]
        amount_raw = args[1]

        if not amount_raw.isdigit():
            return None, "❌ ERROR: Kwota musi być liczbą całkowitą!", None, None
        
        amount = int(amount_raw)
        user_points = int(user.get('points', 0))
        if amount <= 0:
            return None, "❌ Musisz przelać więcej niż 0!", None, None
            
        if amount > user_points:
            return None, f"❌ Możesz dać tylko tyle ile masz! (Masz: `{user_points:,}` pkt)", None, None

        dest_user = userFromPattern(target_raw)
        if not dest_user:
            return None, f"❌ Nie znam tego użytkownika: `{target_raw}`.", None, None

        if str(dest_user['discord_id']) == str(user['discord_id']):
            return None, "❌ Nie możesz przelać punktów samemu sobie! To nie inflacja.", None, None

        points.transferPoints(str(user['discord_id']), dest_user['discord_id'], amount)
        returnEmbed = _gambleEmbedGen.transfer_result(user, dest_user, amount)

    elif action == "rewards":
        return None, None, None, ""
    elif action == "gamble":
        if not args:
            return None, None, None, "Musisz podać kwotę lub `all`! Przykład: `!gamble 100`"

        curr_points = int(user.get('points', 0))
        input_val = str(args[0]).lower()

        if input_val == "all":
            amount = curr_points
        elif input_val.isdigit():
            amount = int(input_val)
        else:
            return None, None, None, "Musisz obstawić liczbę naturalną lub `all`!"
        
        min_bet = max(int(curr_points * 0.1), 25)

        if amount > curr_points:
            returnText = f"Nie masz tyle punktów! Posiadasz tylko `{curr_points:,}`."
        elif amount < min_bet and curr_points >= 25:
             returnText = f"Za mała stawka! Minimalny zakład dla Ciebie to `{min_bet:,}` pkt (10% portfela lub min. 25)."
        elif amount <= 0:
            returnText = "Chcesz grać o nic? Obstaw coś konkretnego!"
        
        else:
            result = random.randint(1, 2)
            
            if result == 1: # WYGRANA
                new_balance = curr_points + amount
                db.updateUser('discord_id', str(user['discord_id']), 'points', new_balance)
                returnEmbed = _gambleEmbedGen.gamble_result(user, amount, "win", new_balance)
            else: # PRZEGRANA
                new_balance = curr_points - amount
                db.updateUser('discord_id', str(user['discord_id']), 'points', new_balance)
                returnEmbed = _gambleEmbedGen.gamble_result(user, amount, "loss", new_balance)

    return returnEmbed, returnText, returnView, returnFile

async def handleStocksModule(action, args, user, dcbot, avatarUrl):
    returnEmbed, returnView, returnFile, returnText = None, None, None, ""
    defaultTitle = "Giełda P1H"
    stockSymbol = args[0].upper() if args else None
    _stocks = list(db.retrieveTopStocks(100))
    if not _stocks:
        return _utilityEmbedGen.error_msg(defaultTitle, "Obecnie nie ma akcji na giełdzie."), None, None, None
    
    # --- ROUTING LOGIC ---
    if action == "view":
        returnEmbed = _stockEmbedGen.overview(_stocks)
    elif action == "rundown":
        returnEmbed = _stockEmbedGen.rundown(stocks.informOnStocksUpdate())
    elif action == "portfolio":
        target_avatar = avatarUrl
        target_user = user
        if args:
            temp_user = userFromPattern(args[0])
            if temp_user:
                target_user = temp_user
                try:
                    flex_user = await dcbot.fetch_user(int(target_user['discord_id']))
                    target_avatar = flex_user.avatar.url if flex_user.avatar else flex_user.default_avatar.url
                except Exception:
                    target_avatar = ""
            else:
                returnText = f"Użytkownik {args[0]} nie został znaleziony w bazie."
        returnEmbed = _stockEmbedGen.user_portfolio(target_user, target_avatar)
    elif action == "fullview":
        returnEmbed = _stockEmbedGen.full_stonks(_stocks)
    elif action == "cashout":
        success, msg = stocks.cashout(user['name'])
        if success:
            returnEmbed = _stockEmbedGen.stock_event(user, None, msg, "cashout")
        else:
            returnEmbed = _utilityEmbedGen.error_msg(defaultTitle,msg)
    elif action in ["buy", "sell"]:
        if len(args) < 2:
            returnEmbed = _utilityEmbedGen.error_msg(defaultTitle, "Brak symbolu lub ilości.", f"!{action} [SYMBOL] [ILOŚĆ]")
        else:
            try:
                amount = int(args[1])
                stock = db.retrieveStock('symbol', stockSymbol)
                
                if amount <= 0:
                    returnEmbed = _utilityEmbedGen.error_msg(defaultTitle, "Ilość musi być większa od 0.", f"!{action} [SYMBOL] [ILOŚĆ]")
                elif not stock:
                    returnEmbed = _utilityEmbedGen.error_msg(defaultTitle, f"Spółka {stockSymbol} nie istnieje.")
                else:
                    if action == "buy":
                        success, msg = stocks.purchaseStocks(user['name'], stockSymbol, amount)
                        if success:
                            returnEmbed = _stockEmbedGen.stock_event(user, stock, msg, "buy")
                        else:
                            returnEmbed = _utilityEmbedGen.error_msg(defaultTitle, msg)
                    else:
                        success, msg = stocks.sellStocks(user['name'], stockSymbol, amount)
                        if success:
                            returnEmbed = _stockEmbedGen.stock_event(user, stock, msg, "sell")
                        else:
                            returnEmbed = _utilityEmbedGen.error_msg(defaultTitle, msg)
            
            except ValueError:
                returnEmbed = _utilityEmbedGen.error_msg(defaultTitle, "Ilość musi być liczbą całkowitą!")
    else:
        returnText = f"Nieznana akcja: {action}"

    return returnEmbed, returnText, returnView, returnFile