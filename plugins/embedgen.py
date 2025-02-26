import random
from discord import Embed, Colour, File
import time
from os import environ
from datetime import datetime, timedelta

POINTS_ICON_URL = "https://i.gifer.com/7cJ2.gif"#"https://static.thenounproject.com/png/3883695-200.png"
CASINO_ICON_URL = "https://cdn3.emoji.gg/emojis/2666-casino-chip.png"
GAMBA_GIF_URL = "https://images.emojiterra.com/google/noto-emoji/animated-emoji/1f3b0.gif"
BOT_GIF_ADDRESS = "https://cdn3.emoji.gg/emojis/48134-bmodancing.gif"
GAMBA_ANOTHER_GIF_URL = "https://cdn3.emoji.gg/emojis/3884-gamba.gif"
WIN_ICON_URL = "https://cdn.discordapp.com/emojis/804525960345944146.webp?size=96&quality=lossless"
LOSE_ICON_URL = "https://cdn3.emoji.gg/emojis/PepeHands.png"
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
PIZZA_ICON_URL = "https://cdn3.emoji.gg/emojis/16965-cutepizza.png"

GAMBA_RANDOM_ICON_ARRAY = ["https://cdn3.emoji.gg/emojis/5897-peepo-gamba.gif",
                           "https://cdn3.emoji.gg/emojis/3135-pepegamble.gif",
                           "https://cdn3.emoji.gg/emojis/3955-gamba-addict.gif"]

BIRTHDAY_RANDOM_ICON_ARRAY = [ "https://cdn3.emoji.gg/emojis/83280-confettipopper.gif",
                                "https://cdn3.emoji.gg/emojis/82548-balloons.gif"]

SIGN_ICON_ARRAY = {
    "baran": "https://cdn3.emoji.gg/emojis/42434-aries.png",
    "byk": "https://cdn3.emoji.gg/emojis/44512-taurus.png",
    "bliznieta": "https://cdn3.emoji.gg/emojis/42244-gemini.png",
    "rak": "https://cdn3.emoji.gg/emojis/87993-cancer.png",
    "lew": "https://cdn3.emoji.gg/emojis/85770-leo.png",
    "panna": "https://cdn3.emoji.gg/emojis/47057-virgo.png",
    "waga": "https://cdn3.emoji.gg/emojis/12487-libra.png",
    "skorpion": "https://cdn3.emoji.gg/emojis/6245-scorpio.png",
    "strzelec": "https://cdn3.emoji.gg/emojis/68830-sagittarius.png",
    "koziorozec": "https://cdn3.emoji.gg/emojis/27440-capricorn.png",
    "wodnik": "https://cdn3.emoji.gg/emojis/53835-aquarius.png",
    "ryby": "https://cdn3.emoji.gg/emojis/9982-pisces.png"
}

PHOTO_REFERENCE_URL = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference="
API_KEY="&key=" + environ["GOOGLE_MAPS_API_KEY"]

PEPE_BIRTHDAY_EMOTE = "<:pepebirthday:1127216158974677084>"
BIRTHDAY_PHRASES = ["Wszystkiego najlepszego!",
                    "Wooohoo!",
                    "Sto lat, sto lat!",
                    "Starosc nie radosc!",
                    "Juz tylko rok blizej do smierci!"
                    ]
PARTY_FACE_ICON = "https://cdn3.emoji.gg/emojis/72795-b-partying-face.png"

def generateEmbedFromTFTMatch(results,players,matchID, date):
    #title of embed - ranked/normal - set
    topTitle = results[0] + " - " + results[1]

    #we random icons for now (left - up corner)
    embedIcon = random.choice(ICON_ARRAY)
    endColour = Colour.blue()

    #main title and embed data 
    embed = Embed(title = str("Nowa partia z P1H w TFT!"), description = None, colour = endColour )
    embed.set_author(name = topTitle, icon_url = embedIcon)
    embed.set_thumbnail(url = TFT_ICON)

    playerList = ""
    iterator = 0
    for player in players:
        #if its one of our players - we want to underline and bold him
        #if player in importantPeople:
        #    player = "__**" + player + "**__"
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
    endColour = Colour.red()

    if(results[-2] == "win"):
        endGameStatus = "EZ WIN"
        endGameIcon = WIN_ICON_URL
        endColour = Colour.green()
        
    embed = Embed(title = str(playerList + " zagrali sobie ARAMka!"), description = str(results[-1]), colour = endColour )
    embed.set_author(name = endGameStatus, icon_url = endGameIcon)
    embed.set_thumbnail(url = TFT_ICON)
    for result in results[:-2]:
        embed.add_field(name = "", value = result, inline = False)

    embed.set_footer(text = str(matchID), icon_url = FOOTER_ICON)
    return embed

def generateEmbedFromRestaurant(restaurant):
    embedIcon = random.choice(ICON_ARRAY)
    endColour = Colour.blue()
    
    #print(restaurant['photos']['photo_reference'])
    #print(PHOTO_REFERENCE_URL + str(restaurant['photos'][0]['photo_reference']) + API_KEY)
    #print(restaurant['photos'][0]['photo_reference'])
    #main title and embed data 
    embed = Embed(title = restaurant['name'], description = restaurant['vicinity'], colour = endColour )
    embed.set_author(name = "Restauracja wybrana!", icon_url = restaurant['icon'])
    #if restaurant['photos']:
    #embed.set_thumbnail(url = requests.get(PHOTO_REFERENCE_URL + str(restaurant['photos'][0]['photo_reference']) + API_KEY, allow_redirects = False).headers['location'])
    return embed

def generateEmbedFromHoroscope(text, sign, name):
    embed = Embed(colour = Colour.purple())
    embed.set_author(name = "Horoskop na dzis - dla Ciebie, " + str(name) + "!", icon_url = SIGN_ICON_ARRAY[sign])
    embed.add_field(name = str(sign).capitalize(), value = text)
    embed.set_footer(text = "source : https://horoskop.wp.pl/horoskop/horoskop-dzienny/")
    return embed

def generateHelpEmbed():
    embed = Embed(colour = Colour.yellow())
    embed.set_author(name = "Tutorial uzywania bota:", icon_url = "https://cdn.7tv.app/emote/01GR7R0H9G000FEKDNHQTECH62/2x.avif")
    embed.set_thumbnail(url = "https://cdn.7tv.app/emote/01G4ZTECKR0002P97QQ94BDSP4/4x.avif")
    listOfCommands = "!help - to okno.\n"
    listOfCommands += "!analyzetft <match_id> - analiza meczu TFT.\n"
    listOfCommands += "!analyzelol <match_id> - analiza meczu LOL'a.\n"
    listOfCommands += "!points - wyswietla aktualna liczbe punktow.\n"
    listOfCommands += "!top X - wyswietla top X posiadaczy punktow.\n"
    listOfCommands += "!horoskop - zwraca horoskop na dzis!\n"
    listOfCommands += "!ai <pytanie> - zadaj pytanie AI!\n"
    embed.add_field(name = "Komendy:", value = listOfCommands)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateTopPointsEmbed(users, amount):
    stringList = ""
    increment = 0
    for user in users:
        increment = increment + 1
        stringList = stringList + str(increment) + ") " + user['name'] + " - " + str(user['points']) + " ppkt.\n"

    embed = Embed(title = "pizzopunkty na DC Pizza One Hit!", colour = Colour.og_blurple())
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_thumbnail(url = POINTS_ICON_URL)
    embed.add_field(name = "__Top " + str(amount) + ":__", value = (stringList), inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateRuletaWheel(id = 0, gif_path = "assets/gif/ruleta.gif"):
    embed = Embed(title="Ruletka ID: #" + str(id), description="A zwycieza...", color=Colour.darker_grey())

    file = File(gif_path, filename = gif_path.split("/")[-1])
    embed.set_image(url="attachment://"+ gif_path.split("/")[-1])

    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed, file

def generateRuletaResults(players, winner, id = 0):
    color = Colour.dark_blue()
    text = "niebieski"
    if winner == "Red":
        color = Colour.dark_red()
        text = "czerwony"
    elif winner == "Green":
        color = Colour.dark_green()
        text = "zielony"
        
    embed = Embed(title="Ruleta Pizza One Hit #" + str(id), description="Wygrywa... " + str(text) + "!", color=color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    listOfPlayers = ""
    for player in players:
        sign = ""
        if int(player[2]) > 0:
            sign = "+"
        listOfPlayers = listOfPlayers + str(player[0]) + ": "+ str(sign) + str(player[2]) + "ppkt.\n"
    embed.add_field(name = "Bilans: ", value = listOfPlayers)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateRuletaChoices(id = 0):
    formatted_time = (datetime.now() + timedelta(hours=1, minutes=4)).strftime('%H:%M:%S')
    embed = Embed(title="Ruleta Pizza One Hit #" + str(id), description="Czas na gre do: " + str(formatted_time), color=Colour.darker_grey())
    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.add_field(name = "Koszt - 50 PPKT", value = "!niebieski = x2!\n!czerwony = x2! \n !zielony = x25!")
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateRuletaPlayers(players, id = 0):
    embed = Embed(title="Ruleta Pizza One Hit #" + str(id), description="", color=Colour.darker_grey())
    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.add_field(name = "Oto zawodnicy:", value = players)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateAIResponse(input, response):
    embed = Embed(title="Twoje pytanie: ", description=str(input), color=Colour.darker_grey())
    embed.add_field(name = "Odpowiedz: ", value = response)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateBirthdayEmbed(user, facts, wrozba):
    embed = Embed(title="Dzis sa twoje urodziny, " + user['name'] + "!", description = PEPE_BIRTHDAY_EMOTE + " " + BIRTHDAY_PHRASES[random.randint(0,len(BIRTHDAY_PHRASES) - 1)], color=Colour.pink())
    embed.set_author(name = "Pizza One Hit AI", icon_url = BIRTHDAY_RANDOM_ICON_ARRAY[random.randint(0,len(BIRTHDAY_RANDOM_ICON_ARRAY) - 1)])

    body = ""
    if facts:
        for fact in facts:
            body = body + str(fact) + "\n"
    embed.add_field(name = "Ciekawostki: ", value = body)
    embed.add_field(name = "Wrozba: ", value = wrozba)
    embed.set_footer(text = "Do twojego konta zostalo przypisane 2000 ppkt!", icon_url = PARTY_FACE_ICON)
    return embed

def generateWinnerEmbed(user, userAvatarURL):
    embed = Embed(title="Gratulacje, " + user['name'] + "!", description="Wygrales dzienne losowanie!", color=Colour.dark_green())
    embed.set_thumbnail(url = userAvatarURL)
    embed.add_field(name = "Do twojego konta przypisalismy 200 pkt + 10% twojej dotychczasowej wartosci!", value="Woohoo!")
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateLoserEmbed(user, userAvatarURL):
    embed = Embed(title="Ojojoj, " + user['name'] + "...", description="Jestes dzisiejszym przegrywem..", color=Colour.dark_red())
    embed.set_thumbnail(url = userAvatarURL)
    embed.add_field(name = "Z twojego konta zostalo odebrane 200 ppkt.", value="Sprobuj sie odbic na hazard-lounge!")
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed
