
import plugins.pizzadatabase as db
import plugins.embedgen as embedgen
import plugins.points as points
import plugins.gifgenerator as gif
import asyncio
from discord import ui, ButtonStyle, Interaction, NotFound

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