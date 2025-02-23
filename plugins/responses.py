import random
import plugins.weather as weather
import plugins.horoscope as horoskop
import plugins.pizzadatabase as db
import plugins.embedgen as embedgen
import plugins.pubfinder as pubfinder
import plugins.points as points
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import re

def getWeather():
    return weather.getLodzWeather()

def handleResponse(userMessage, author) -> str:
    message = userMessage.lower()
    returnEmbed = None
    returnView = None
    returnText = "[!] - Nie znam komendy: \"" + userMessage + "\""
    message = message[1:]
    commands = message.split(" ")

    #komendy wielokomendowe
    if len(commands) > 1:

        #analyze league of legends match - need proper ID, example: EUN1_3498132354
        if commands[0] == "analyzelol":
            if re.search(r'euw1_\d+|eun1_\d+',commands[1]):
                results, players = leagueapi.analyzeMatch(leagueapi.getMatchData(str(commands[1])), False)
                if len(results) > 0 :
                    returnEmbed = embedgen.generateEmbedFromLeagueMatch(results,players,commands[1])
                else:
                    print(results)
            else:
                returnText = "kolego, podaj poprawny ID, np: EUN1_3498132354"

        #analyze TFT match - need proper ID, example: EUN1_3742603881
        elif commands[0] == "analyzetft":
            if re.search(r'euw1_\d+|eun1_\d+',commands[1]):
                date, results, players = tftapi.analyzeMatch(tftapi.getMatchData(str(commands[1])), False)
                if len(results) > 0 :
                    returnEmbed = embedgen.generateEmbedFromTFTMatch(results,players,commands[1], date)
            else:
                returnText = "kolego, podaj poprawny ID, np: EUN1_3742603881"

        #find proper pub to meet together (NEEDS WORK)
        elif commands[0] == "znajdzbar":
            returnEmbed = embedgen.generateEmbedFromRestaurant(pubfinder.chooseRestaurant(),["rolab", "bartus", "fifi"])

        elif commands[0] == "gamble" or commands[0] == "gamba" or commands[0] == "yolo":
            if len(commands) == 2:
                if str(commands[1]) or str(commands[1]) == "all":
                    amount = 0
                    if str(commands[1]).isdigit():
                        amount = int(str(commands[1]))
                    user = db.retrieveUser('discord_id', str(author))
                    if user:
                        curr = int(user['points'])
                        if str(commands[1]) == "all":
                            amount = curr
                        if curr >= amount:
                            result = random.randint(1,2)
                            if result == 1:
                                curr = curr + amount
                                returnText = "You've won!"
                            else:
                                curr = curr - amount
                                returnText = "You've Lost!"
                            db.updateUser(str(author), 'points', curr)
                        else:
                            returnText = "You can't bet more than You have; your current points: " + str(user['points']) + "!"
                else:
                    returnText = "You have to pass a positive number!"

        elif commands[0] == "setpoints" or commands[0] == "set" or commands[0] == "points":
            if int(author) == 326259887007072257:
                if len(commands) == 3:
                    if str(commands[2]).isdigit():
                        returnText = db.updateUser(str(commands[1]), 'points', int(commands[2]))
                    else:
                        returnText = "ERROR: ostatnia wartosc to musi byc int!"
                else:
                    returnText = "Niepoprawnie uzyta komenda. Uzyj np !set Mati 20"
            else:
                returnText = "Nie masz prawa do uzywania tej komendy. Ten incydent zostanie zgloszony."


        elif commands[0] == "top":
            if len(commands) == 2:
                if str(commands[1]).isdigit():
                    amount = int(str(commands[1]))
                    users = points.getTop(amount)
                    if users:
                        returnEmbed = embedgen.generateTopPointsEmbed(users, amount)

        elif commands[0] == "roll":
            if len(commands) == 2:
                returnText = "Rolling between 1 - " + commands[1] + " -> " + str(random.randint(1,int(commands[1])))
            elif len(commands) == 3:
                returnText = "Rolling between " + commands[1] + " - " + commands[2] + " -> " + str(random.randint(int(commands[1]),int(commands[2])))
    else:
        if message == 'whoami':
            returnText =  db.retrieveUser('discord_id', str(author))['name']

        if message == "points":
            user = db.retrieveUser('discord_id', str(author))
            if user:
                returnText = user['name'] + " - masz: " + str(user['points']) + " pizzapoints."

        if message == 'roll':
            returnText =  str(random.randint(1,6))

        if message == 'embed':
            returnText =  "embed_test"

        if message == "pogoda":
            returnText =  weather.getLodzWeather()

        if message == "top5" or message == "top":
            amount = 5
            users = points.getTop(amount)
            if users:
                returnEmbed = embedgen.generateTopPointsEmbed(users, amount)
        
        if message == "horoskop" or message == "zodiak" or message == "mojhoroskop":
            name = db.retrieveUser('discord_id', str(author))['name']
            sign, text = horoskop.getHoroscopeForUser('discord_id', str(author))
            returnEmbed = embedgen.generateEmbedFromHoroscope(text, sign, name)

        if message == "ruleta":
            returnEmbed = embedgen.generateRuleta()



        if message == "help" or message == "?" or message == "??" or message == "pomoc" or message == "tutorial":
            returnEmbed = embedgen.generateHelpEmbed()

    return returnEmbed, returnText, returnView