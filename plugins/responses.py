import random
import plugins.weather as weather
import plugins.horoscope as horoskop
import plugins.pizzadatabase as db
import plugins.embedgen as embedgen
import plugins.pubfinder as pubfinder
import plugins.points as points
import plugins.gifgenerator as gif
import riot.riotleagueapi as leagueapi
import riot.riottftapi as tftapi
import asyncio

import re
from discord import Embed, Colour, ui, ButtonStyle, Interaction, NotFound

restaurantKeywords = ["restauracja", "bar", "znajdzbar", "gdziejemy", "jemy"]
helpKeyword = ["help", "?", "??", "pomoc", "tutorial", "kurwapomocy", "test"]

class ruletaView(ui.View):
    def __init__(self):
        super().__init__(timeout = 120)
        self.playingUsers = []
        self.sent_messages = []
        self.message = None
        self.amount = 50

    async def treatMessage(self, choice, text, interaction):
        author_id = interaction.user.id
        user = db.retrieveUser('discord_id',author_id)
        if user:
            if int(user['points']) < int(self.amount):
                message = await interaction.response.send_message("Masz za malo pizzopunktow. Wymagane - " + str(self.amount) + ", ty masz: " + str(user['points']) + "!", ephemeral=True)
        else:
            message = await interaction.response.send_message(text, ephemeral=True)
            self.sent_messages.append(message)
            if self.playingUsers:
                for user in self.playingUsers:
                    if user[0] == author_id:
                        user[1] = choice
            else:
                self.playingUsers.append([author_id, choice])


    @ui.button(label="Blue", style=ButtonStyle.primary)
    async def option1(self, interaction: Interaction, button: ui.Button):
        author_id = interaction.user.id
        user = db.retrieveUser('discord_id',author_id)
        if user:
            if int(user['points']) < int(self.amount):
                message = await interaction.response.send_message("Masz za malo pizzopunktow. Wymagane - " + str(self.amount) + ", ty masz: " + str(user['points']) + "!", ephemeral=True)
        else:
            choice = "Blue"
            message = await interaction.response.send_message("Postawiles pizzopunkty na Niebieskie!", ephemeral=True)
            self.sent_messages.append(message)
            if self.playingUsers:
                for user in self.playingUsers:
                    if user[0] == author_id:
                        user[1] = choice
            else:
                self.playingUsers.append([author_id, choice])

    @ui.button(label="Red", style=ButtonStyle.danger)
    async def option2(self, interaction: Interaction, button: ui.Button):
        author_id = interaction.user.id
        user = db.retrieveUser('discord_id',author_id)
        if user:
            if int(user['points']) < int(self.amount):
                message = await interaction.response.send_message("Masz za malo pizzopunktow. Wymagane - " + str(self.amount) + ", ty masz: " + str(user['points']) + "!", ephemeral=True)
        else:
            choice = "Red"
            message = await interaction.response.send_message("Postawiles pizzopunkty na czerwone!", ephemeral=True)
            self.sent_messages.append(message)
            if self.playingUsers:
                for user in self.playingUsers:
                    if user[0] == author_id:
                        user[1] = choice
            else:
                self.playingUsers.append([author_id, choice])

    @ui.button(label="Green", style=ButtonStyle.success)
    async def option3(self, interaction: Interaction, button: ui.Button):
        author_id = interaction.user.id
        user = db.retrieveUser('discord_id',author_id)
        if user:
            if int(user['points']) < int(self.amount):
                message = await interaction.response.send_message("Masz za malo pizzopunktow. Wymagane - " + str(self.amount) + ", ty masz: " + str(user['points']) + "!", ephemeral=True)
        else:
            choice = "Green"
            message = await interaction.response.send_message("Postawiles pizzopunkty na zielone!", ephemeral=True)
            self.sent_messages.append(message)
            if self.playingUsers:
                for user in self.playingUsers:
                    if user[0] == author_id:
                        user[1] = choice
            else:
                self.playingUsers.append([author_id, choice])
    
    async def send(self, channel, embed = None):  
        self.message = await channel.send(view=self, embed = embed)

    async def on_timeout(self):
        if self.sent_messages:
                for message in self.sent_messages:
                    if message:
                        try:
                            await message.delete() 
                        except NotFound:
                            pass

        if self.message:
            channel = self.message.channel
            try:
                await self.message.delete()
            except NotFound:
                print("[INFO] wiadomosc juz jest usunieta - ruletaview")

        if self.playingUsers:
            parsedPeople = []
            winner = gif.generate_spinning_wheel_with_pointer("assets/gif/ruleta.gif")
            await channel.send("Oto gracze tej rulety:")
            for pair in self.playingUsers:
                user = db.retrieveUser('discord_id',str(pair[0]))
                if user:
                    earnings = 0
                    if pair[1] == winner:
                        if winner == "Green":
                            earnings = self.amount * 20
                        else:
                            earnings = self.amount * 2
                    else:
                        earnings -= self.amount
                    msg = str(user['name'] + " postawil na: " + str(pair[1]) + "!")
                    points.addPoints(pair[0], earnings)
                    parsedPeople.append([user['name'], pair[1], earnings])
                    await channel.send(msg)

            embed, file = embedgen.generateRuletaWheel()
            message = await channel.send(embed = embed, file = file)
            await asyncio.sleep(15)
            #await message.delete()
            await channel.send(embed = embedgen.generateRuletaResults(parsedPeople, winner)) 
        else:
            print("Nikt nie skusil sie na partyjke ruletki")    
        

class usersChooseView:
    def __init__(self, users, radius):
        self.users = users
        self.selectedUsers = []
        self.sent_messages = []
        self.radius = radius

    def generate_embed(self):
        """Creates and returns an embed."""
        embed = Embed(title="User Selection", description="Click on a user button below:", color=Colour.blue())
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

def getWeather():
    return weather.getLodzWeather()

def handleResponse(userMessage, author) -> str:
    message = userMessage.lower()
    returnEmbed = None
    returnView = None
    returnFile = None
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
        elif commands[0] in restaurantKeywords:
            if len(commands) == 2:
                if str(commands[1]).isdigit():
                    embed_buttons = usersChooseView(db.retrieveAllusers(), int(str(commands[1])))
                    returnView = embed_buttons.generate_view()
                    returnEmbed = embed_buttons.generate_embed()#embedgen.generateEmbedFromRestaurant(pubfinder.chooseRestaurant(),["rolab", "bartus", "fifi"])

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
                        if curr >= amount and amount > 0:
                            result = random.randint(1,2)
                            if result == 1:
                                curr = curr + amount
                                returnText = "You've won " + str(amount) + " ponits! (now You have : " + str(curr) + ")"
                            else:
                                curr = curr - amount
                                returnText = "You've Lost " + str(amount) + " ponits! (now You have : " + str(curr) + ")"
                            db.updateUser('discord_id', str(author), 'points', curr)
                        else:
                            returnText = "You can't bet that; your current points: " + str(user['points']) + "!"
                else:
                    returnText = "You have to pass a positive number!"

        elif commands[0] == "setpoints" or commands[0] == "set" or commands[0] == "points":
            if int(author) == 326259887007072257:
                if len(commands) == 3:
                    if str(commands[2]).isdigit():
                        returnText = db.updateUser('discord_id', str(commands[1]), 'points', int(commands[2]))
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

        #if message == "ruleta":
            #winner = gif.generate_spinning_wheel_with_pointer("assets/gif/ruleta.gif")
            #returnEmbed, returnFile = embedgen.generateRuleta(winner)
            #returnView = ruletaView()
            #returnView = ruletaView()
            #returnEmbed = embedgen.generateRuletaChoices()

        if message in restaurantKeywords:
            embed_buttons = usersChooseView(db.retrieveAllusers(), 500)
            returnView = embed_buttons.generate_view()
            returnEmbed = embed_buttons.generate_embed()

        if message in helpKeyword:
            returnEmbed = embedgen.generateHelpEmbed()

    return returnEmbed, returnText, returnView, returnFile