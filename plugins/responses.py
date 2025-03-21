import random
import plugins.weather as weather
import plugins.horoscope as horoskop
import plugins.pizzadatabase as db
import plugins.embedgen as embedgen
import plugins.pubfinder as pubfinder
import plugins.points as points
import plugins.gifgenerator as gif
import plugins.birthday as birthday
import plugins.ai as ai
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import asyncio
from datetime import datetime
import re
from discord import Embed, Colour, ui, ButtonStyle, Interaction, NotFound

MAX_SLOT_AMOUNT = 5000

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

#view in discord for roullette - it will have 3 buttons that You might click - blue/green/red - badly written atm, as we duplicate code 3 times
class ruletaView(ui.View):
    def __init__(self):
        super().__init__(timeout = 180)
        self.activeUsers = []
        self.playingUsers = []
        self.sent_messages = []
        self.message = None
        self.amount = 50
        self.id = 0

    @ui.button(label="Blue", style=ButtonStyle.primary)
    async def option1(self, interaction: Interaction, button: ui.Button):
        author_id = interaction.user.id
        user = db.retrieveUser('discord_id',str(author_id))
        msg = ""
        if user:
            if int(user['points']) < int(self.amount):
                msg = "Masz za malo pizzopunktow. Wymagane - " + str(self.amount) + ", ty masz: " + str(user['points']) + "!"
            else:
                choice = "Blue"
                if self.playingUsers:
                    newUser = True
                    for user in self.playingUsers:
                        if user[0] == author_id:
                            user[1] = choice
                            newUser = False
                            msg = "Zmieniles zaklad na niebieski!"
                    if newUser:
                        msg = "Postawiles pizzopunkty na niebieski (-50 ppkt)!"
                        self.playingUsers.append([author_id, choice])
                        points.addPoints(str(author_id), int(-1 * self.amount))
                else:
                    msg = "Postawiles pizzopunkty na niebieski (-50 ppkt)!"
                    self.playingUsers.append([author_id, choice])
                    points.addPoints(str(author_id), int(-1 * self.amount))
            msg = msg + " [ruletka #" + str(self.id) + "]"
            message = await interaction.response.send_message(msg, ephemeral=True)
            self.sent_messages.append(message)

    @ui.button(label="Red", style=ButtonStyle.danger)
    async def option2(self, interaction: Interaction, button: ui.Button):
        author_id = interaction.user.id
        user = db.retrieveUser('discord_id',str(author_id))
        msg = ""
        if user:
            if int(user['points']) < int(self.amount):
                msg = "Masz za malo pizzopunktow. Wymagane - " + str(self.amount) + ", ty masz: " + str(user['points']) + "!"
            else:
                choice = "Red"
                if self.playingUsers:
                    newUser = True
                    for user in self.playingUsers:
                        if user[0] == author_id:
                            user[1] = choice
                            newUser = False
                            msg = "Zmieniles zaklad na czerwony!"
                    if newUser:
                        msg = "Postawiles pizzopunkty na czerwony (-50 ppkt)!"
                        self.playingUsers.append([author_id, choice])
                        points.addPoints(str(author_id), int(-1 * self.amount))
                else:
                    msg = "Postawiles pizzopunkty na czerwony (-50 ppkt)!"
                    self.playingUsers.append([author_id, choice])
                    points.addPoints(str(author_id), int(-1 * self.amount))
            msg = msg + " [ruletka #" + str(self.id) + "]"
            message = await interaction.response.send_message(msg, ephemeral=True)
            self.sent_messages.append(message)

    @ui.button(label="Green", style=ButtonStyle.success)
    async def option3(self, interaction: Interaction, button: ui.Button):
        author_id = interaction.user.id
        user = db.retrieveUser('discord_id',str(author_id))
        msg = ""
        if user:
            if int(user['points']) < int(self.amount):
                msg = "Masz za malo pizzopunktow. Wymagane - " + str(self.amount) + ", ty masz: " + str(user['points']) + "!"
            else:
                choice = "Green"
                if self.playingUsers:
                    newUser = True
                    for user in self.playingUsers:
                        if user[0] == author_id:
                            user[1] = choice
                            newUser = False
                            msg = "Zmieniles zaklad na zielony!"
                    if newUser:
                        msg = "Postawiles pizzopunkty na zielony (-50 ppkt)!"
                        self.playingUsers.append([author_id, choice])
                        points.addPoints(str(author_id), int(-1 * self.amount))
                else:
                    msg = "Postawiles pizzopunkty na zielony (-50 ppkt)!"
                    self.playingUsers.append([author_id, choice])
                    points.addPoints(str(author_id), int(-1 * self.amount))
            msg = msg + " [ruletka #" + str(self.id) + "]"
            message = await interaction.response.send_message(msg, ephemeral=True)
            self.sent_messages.append(message)
    
    async def start(self, channel):  
        self.id = db.addRouletteEntry()
        self.message = await channel.send(view=self, embed = embedgen.generateRuletaChoices(self.id))

    async def on_timeout(self):
        if self.sent_messages:
                for message in self.sent_messages:
                    if message:
                        try:
                            await message.delete() 
                        except NotFound:
                            pass

        #delete original message with buttons
        if self.message:
            channel = self.message.channel
            try:
                await self.message.delete()
            except NotFound:
                print("[INFO] wiadomosc juz jest usunieta - ruletaview")

        if self.playingUsers:
            parsedPeople = []
            fileName = "assets/gif/ruleta" + str(self.id) + ".gif"
            winner = gif.generate_spinning_wheel_with_pointer(fileName)
            msg = ""
            for pair in self.playingUsers:
                user = db.retrieveUser('discord_id',str(pair[0]))
                if user:
                    msg = msg + str(user['name'] + " postawil na: " + str(pair[1]) + "!\n")

            await channel.send(embed = embedgen.generateRuletaPlayers(msg, self.id))
            embed, file = embedgen.generateRuletaWheel(self.id, fileName)
            message = await channel.send(embed = embed, file = file)
            await asyncio.sleep(15)

            #delete wheel? for now - no
            #await message.delete()
            
            userIds = []
            msg = ""
            for pair in self.playingUsers:
                user = db.retrieveUser('discord_id',str(pair[0]))
                if user:
                    earnings = 0
                    if pair[1] == winner:
                        if winner == "Green":
                            earnings = self.amount * 25
                        else:
                            earnings = self.amount * 2
                        points.addPoints(str(user['discord_id']), earnings)
                        #msg = msg + ""
                        parsedPeople.append([user['name'], pair[1], str(earnings)])
                    else:
                        parsedPeople.append([user['name'], pair[1], "-" + str(self.amount)])
                    userIds.append(user['discord_id'])

            db.updateRouletteEntry(self.id, winner)
            db.addRoulettePlayer(self.id, userIds)
            await channel.send(embed = embedgen.generateRuletaResults(parsedPeople, winner, self.id))               
        
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
    return embedgen.generateSlotsAnimation(id, output_path, earnings, user)

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
        points.addPoints(str(user['discord_id']), 2000)
    return returnEmbed, returnText

#this is main body of this module - it performs manual if check depending on my widzimisie
def handleResponse(userMessage, author) -> str:
    random.seed(datetime.now().timestamp())
    #message = userMessage.lower()
    returnEmbed = None
    returnView = None
    returnFile = None
    returnText = "[!] - Nie znam komendy: \"" + userMessage + "\""
    message = userMessage[1:]
    commands = message.split(" ")

    #esnure it matches the command even if its in lower
    commands[0] = str(commands[0].lower())

    user = db.retrieveUser('discord_id', str(author))
    if user == None:
        returnText = "User o ID: " + str(author) + "nie znajduje sie w bazie danych. Uderz do roLab."
        return returnEmbed, returnText, returnView, returnFile   
    
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
        elif commands[0] in restaurantKeywords:
            if len(commands) == 2:
                if str(commands[1]).isdigit():
                    embed_buttons = usersChooseView(db.retrieveAllusers(), int(str(commands[1])))
                    returnView = embed_buttons.generate_view()
                    returnEmbed = embed_buttons.generate_embed()#embedgen.generateEmbedFromRestaurant(pubfinder.chooseRestaurant(),["rolab", "bartus", "fifi"])

        elif commands[0] in aiKeyword:
            user = db.retrieveUser('discord_id', str(author))
            if user:
                query = message[3:]
                db.insertAIHistory(str(author), query)
                text = ""
                returnEmbed = embedgen.generateAIResponse(query, ai.chatWithAI(query))

        elif commands[0] in heistKeyword:
            if len(commands) == 2:
                if db.isHeistAvailable():
                    if str(commands[1]).isdigit():
                        user = db.retrieveUser('discord_id', str(author))
                        if user:
                            curr = int(user['points'])
                            amount = int(str(commands[1]))
                            if curr >= amount and amount >= 200:
                                if (db.isUserPartOfCurrentHeist(user['name'])):
                                    returnText = "Jestes juz czlonkiem aktualnego napadu!"
                                else:
                                    db.appendHeistMember(user['name'], amount)
                                    points.addPoints(str(author), -1 * amount)
                                    returnText = "Pomyslnie dolaczyles do napadu!"
                            else:
                                returnText = "Masz za malo pizzopunktow - obecnie posiadasz: " + str(user['points']) + "! Min: 200 PPKT."
                    else:
                        returnText = "Musisz obstawic liczbe naturalna (dodatnia!)"
                else:
                    returnText = "Obecnie nie mozesz dolaczyc do napadu!"

        elif commands[0] in slotsKeyword:
            if len(commands) == 2:
                if str(commands[1]).isdigit():
                    user = db.retrieveUser('discord_id', str(author))
                    if user:
                        curr = int(user['points'])
                        amount = int(str(commands[1]))
                        if amount > 5000:
                            returnText = "Maksymalna wysokosc zakladu w slotsach to : " + str(MAX_SLOT_AMOUNT) + "."
                        else:
                            if curr >= amount and amount >= 5:
                                returnEmbed, returnFile = generateSlots(amount, user)
                            else:
                                returnText = "Za malo pizzopunktow (min to 5!) - obecnie posiadasz: " + str(user['points']) + "!"
                else:
                    returnText = "Musisz obstawic liczbe naturalna (dodatnia!)"

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
                        min = int(curr * 0.1)
                        if curr >= amount and amount >= int(curr * 0.1) and amount >= 25:
                            result = random.randint(1,2)
                            if result == 1:
                                curr = curr + amount
                                returnText = "Nice! +" + str(amount) + " pizzapkt! (obecnie masz : " + str(curr) + ") <:ez:1343529006162772028>"
                            else:
                                curr = curr - amount
                                returnText = "Oops.. -" + str(amount) + " pizzapkt! (obecnie masz : " + str(curr) + ") <:pepecopium:1094185065925333012>"
                            db.updateUser('discord_id', str(author), 'points', curr)
                        else:
                            returnText = "Za malo pizzopunktow (minimalna ilosc na gre to 10% (lub 25 gdy jestes biedakiem) pizzopunktow!) - obecnie posiadasz: " + str(user['points']) + "!"
                else:
                    returnText = "Musisz obstawic liczbe naturalna (dodatnia!)"

        elif commands[0] == "setpoints" or commands[0] == "set":
            if int(author) == 326259887007072257:
                if len(commands) == 3:
                    if str(commands[2]).isdigit():
                        returnText = db.updateUser('discord_id', str(commands[1]), 'points', int(commands[2]))
                    else:
                        returnText = "ERROR: ostatnia wartosc to musi byc int!"
                else:
                    returnText = "Niepoprawnie uzyta komenda. Uzyj np !set 326259887007072257 20"
            else:
                returnText = securityResponse

        elif commands[0] in arrestKeyword:
            if int(author) == 326259887007072257:
                if len(commands) == 2:
                    if str(commands[1]).isdigit():
                        if db.arrestUser('discord_id', str(commands[1])):
                            returnText = "Pomyslnie zaaresztowano " + str(commands[1]) + "."
                        else:
                            returnText = "Nieznany user : " + str(commands[1]) + "."
                    else:
                        if db.arrestUser('name', str(commands[1])):
                            returnText = "Pomyslnie zaaresztowano " + str(commands[1]) + "."
                        else:
                            returnText = "Nieznany user : " + str(commands[1]) + "."
                else:
                    returnText = "Niepoprawnie uzyta komenda. Uzyj np !arrest 326259887007072257"
            else:
                returnText = securityResponse

        elif commands[0] in freeKeyword:
            if int(author) == 326259887007072257:
                if len(commands) == 2:
                    if str(commands[1]).isdigit():
                        arrested_user = db.retrieveUser('discord_id', str(commands[1]))
                    else:
                        arrested_user = db.retrieveUser('name', str(commands[1]))
                    if db.freeUser('discord_id', str(arrested_user['discord_id'])):
                        returnText = "Pomyslnie wypuszczono " + str(commands[1]) + "."
                    else:
                        returnText = "Nieznany user : " + str(commands[1]) + "."
                else:
                    returnText = "Niepoprawnie uzyta komenda. Uzyj np !uwolnij 326259887007072257"
            else:
                returnText = securityResponse

        elif commands[0] in transferKeyword:
            if len(commands) == 3:
                if str(commands[2]).isdigit():
                    if(int(commands[2]) <= int(user['points'])):
                        if str(commands[1]).isdigit():
                            dest_user = db.retrieveUser('discord_id', commands[1])
                        else:
                            dest_user = db.retrieveUser('name', commands[1])
                        if dest_user:
                            if dest_user != user:
                                points.transferPoints(str(author), dest_user['discord_id'], int(commands[2]))
                                returnText = "Pomyslnie przetransferowano " + str(commands[2]) + " pizzopunktow do uzytkownika " + dest_user['name'] + "."
                            else:
                                returnText = "Nie mozesz przelac Sobie punktow!"
                        else:
                            returnText = "Nieznany user : " + str(commands[1]) + "."
                    else:
                        returnText = "Mozesz dac tylko tyle ile masz!"
                else:
                    returnText = "ERROR: ostatnia wartosc to musi byc int!"
            else:
                returnText = "Niepoprawnie uzyta komenda. Uzyj np !tip Mati 20"

        elif commands[0] == "add":
            if int(author) == 326259887007072257:
                if len(commands) == 3:
                    if str(commands[2]).isdigit():
                        if str(commands[1]).isdigit():
                            dest_user = db.retrieveUser('discord_id', commands[1])
                        else:
                            dest_user = db.retrieveUser('name', commands[1])
                        if dest_user:
                            points.addPoints(dest_user['discord_id'], int(commands[2]))
                            returnText = "Pomyslnie dodano " + str(commands[2]) + " pizzopunktow do uzytkownika " + dest_user['name'] + "."
                        else:
                            returnText = "Nieznany user : " + str(commands[1]) + "."
                    else:
                        returnText = "ERROR: ostatnia wartosc to musi byc int!"
                else:
                    returnText = "Niepoprawnie uzyta komenda. Uzyj np !add Bartolo 20"
            else:
                returnText = securityResponse

        elif commands[0] == "instructai":
            if int(author) == 326259887007072257:
                if len(commands) > 1:
                    user = db.retrieveUser('discord_id', str(author))
                    db.insertAIInstruction(message[12:])
                    ai.resetModel()
            else:
                returnText = securityResponse


        elif commands[0] == "setriotkey":
            if int(author) == 326259887007072257 and len(commands) == 2:
                tftapi.setAPIKey(commands[1])
                returnText = "API Key successfuly replaced"

        elif commands[0] == "birthdaytest":
            if int(author) == 326259887007072257 and len(commands) == 2:
                returnEmbed, returnText = getBirthdayStuff(str(commands[1]))

        elif commands[0] == "top":
            if len(commands) == 2:
                if str(commands[1]).isdigit():
                    amount = int(str(commands[1]))
                    users = points.getTop(amount)
                    if users:
                        returnEmbed = embedgen.generateTopPointsEmbed(users, amount)

        elif commands[0] == "bottom":
            if len(commands) == 2:
                if str(commands[1]).isdigit():
                    amount = int(str(commands[1]))
                    users = points.getBottom(amount)
                    if users:
                        returnEmbed = embedgen.generateBottomPointsEmbed(users, amount)

        elif commands[0] == "roll":
            if len(commands) == 2:
                returnText = "Losujemy: 1 - " + commands[1] + " -> " + str(random.randint(1,int(commands[1])))
            elif len(commands) == 3:
                returnText = "Losujemy: " + commands[1] + " - " + commands[2] + " -> " + str(random.randint(int(commands[1]),int(commands[2])))
    else:

        #if its a singular commmand - transform message to lower.
        message = message.lower()
        if message == 'whoami' or message == 'kimjestem' or message == 'ktoja':
            returnText =  db.retrieveUser('discord_id', str(author))['name']

        if message == "points":
            user = db.retrieveUser('discord_id', str(author))
            if user:
                returnText = user['name'] + " - masz: " + str(user['points']) + " pizzapoints."

        if message == 'roll':
            returnText =  str(random.randint(1,6))

        if message == 'embed':
            returnText =  "embed_test"

        if message == 'ai':
            returnText =  "zapytaj o cos, np !ai daj przepis na nalesniki!"

        if message in escapeKeyword:
            returnText = "Nie jest obecnie aresztowany!"

        if message == "ktosiedzi":
            returnEmbed = embedgen.generateArrestedUsersInfo(db.retrieveArrestedUsers())

        if message in slotsKeyword:
            user = db.retrieveUser('discord_id', str(author))
            if user:
                curr = int(user['points'])
                amount = 5
                if curr >= amount and amount > 0:
                    returnEmbed, returnFile = generateSlots(amount, user)
                else:
                    returnText = "Za malo pizzopunktow - obecnie posiadasz: " + str(user['points']) + "!"

        if message == 'zacopunkty':
            returnText =  "Punkty mozna dostac za udzial w eventach, przebywaniu na voice chat, przy pomocy hazardu lub na widzimisie glownego admina."

        if message in rewardKeyword:
            returnEmbed = embedgen.generateRewards(db.retrieveRewards())

        if message in achievementKeyword:
            returnEmbed = embedgen.generateAchievements(db.retrieveAchievements())

        if message == 'resetai':
            returnText = securityResponse
            if int(author) == 326259887007072257:
                ai.resetModel()
                returnText =  "AI zostal przywrocony do stanu pierwotnego."

        if message == "pogoda":
            returnText =  weather.getLodzWeather()

        if message in begKeyword:
            user = db.retrieveUser('discord_id', str(author))
            if user:
                curr = int(user['points'])
                if curr < 100:
                    if db.isBegAvailable():
                        db.updateUser('discord_id', str(author), 'points', 100)
                        db.createBegEntry(str(author))
                        returnText = "Ustawiono 100 ppkt dla " + user['name'] + ". Globalny cooldown - 10 min."
                        #isBegAvailable = False
                    else:
                        begPerson = db.getBegPerson()
                        if begPerson:
                            returnText = "Cooldown! Sprobuj ponownie pozniej. Ostatnia szansa wykorzystana przez: " + str(begPerson['name']) + "."
                else:
                    returnText = "Masz powyzej 100 ppkt. Opcja dostepna tylko dla najbiedniejszych z biednych."

        if message == "top5" or message == "top":
            amount = 5
            users = points.getTop(amount)
            if users:
                returnEmbed = embedgen.generateTopPointsEmbed(users, amount)
        
        if message == "bottom5" or message == "bottom":
            amount = 5
            users = points.getBottom(amount)
            if users:
                returnEmbed = embedgen.generateBottomPointsEmbed(users, amount)
        
        if message == "heistinfo" or message == "currentheist" or message == "napad":
            currHeist = db.retrieveHeistInfo()
            if currHeist:
                returnEmbed = embedgen.generateHeistInfo(currHeist['level'], currHeist['heist_name'],currHeist['when_starts'],currHeist['members'])

        if message in horoskopKeyword:
            name = db.retrieveUser('discord_id', str(author))['name']
            sign, text = horoskop.getHoroscopeForUser('discord_id', str(author))
            returnEmbed = embedgen.generateEmbedFromHoroscope(text, sign, name)

        if message in restaurantKeywords:
            embed_buttons = usersChooseView(db.retrieveAllusers(), 500)
            returnView = embed_buttons.generate_view()
            returnEmbed = embed_buttons.generate_embed()

        if message in helpKeyword:
            returnEmbed = embedgen.generateHelpEmbed()

    return returnEmbed, returnText, returnView, returnFile