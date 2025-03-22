import random
from discord import Embed, Colour, File
import time
from os import environ
from datetime import datetime, timedelta
import requests
import plugins.points as points
import plugins.pizzadatabase as db
import plugins.ai as ai

CRIMINAL_ICON_URL = "https://static.wikia.nocookie.net/villainsfanon/images/2/2f/Evil_Pepe.jpg"
PEPE_PRISON_URL = "https://i.pinimg.com/736x/21/5a/95/215a95772a3aa17024df7d010513ee88.jpg"
PEPE_PUCHAR_URL = "https://static.vecteezy.com/system/resources/thumbnails/027/517/375/small_2x/pixel-art-champoin-golden-cup-icon-png.png"
PEPE_COIN_URL = "https://s2.coinmarketcap.com/static/img/coins/200x200/24835.png"
POINTS_ICON_URL = "https://i.gifer.com/7cJ2.gif"#"https://static.thenounproject.com/png/3883695-200.png"
CASINO_ICON_URL = "https://cdn3.emoji.gg/emojis/2666-casino-chip.png"
PEPE_LAWYER_URL = "https://pbs.twimg.com/media/FwAU5HMXsAEIXdI.jpg"
GAMBA_GIF_URL = "https://images.emojiterra.com/google/noto-emoji/animated-emoji/1f3b0.gif"
MONOPOLY_GUY_URL = "https://e7.pngegg.com/pngimages/663/406/png-clipart-monopoly-party-prison-board-game-others-miscellaneous-game-thumbnail.png"
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

BARTOLO_KEY = environ["BARTOLO_KEY"]

GRATULACJE = ["mlodziezowy i smieszny","jak bandzior","dostojny i wykwintny","niczym 2 letnie dziecko"]

def split_text(text: str, max_length: int = 1000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

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
    embed = Embed(colour = Colour.purple(), title = str(sign).capitalize(), description = text)
    embed.set_author(name = "Horoskop na dzis - dla Ciebie, " + str(name) + "!", icon_url = SIGN_ICON_ARRAY[sign])
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

def generateBottomPointsEmbed(users, amount):
    stringList = ""
    increment = 0
    allUsersLen = len(db.retrieveAllusers())
    for user in users:
        increment = allUsersLen - increment + 1
        stringList = stringList + str(increment) + ") " + user['name'] + " - " + str(user['points']) + " ppkt.\n"

    embed = Embed(title = "pizzopunkty na DC Pizza One Hit!", colour = Colour.og_blurple())
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_thumbnail(url = POINTS_ICON_URL)
    embed.add_field(name = "__Bottom " + str(amount) + ":__", value = (stringList), inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateRuletaWheel(id = 0, gif_path = "assets/gif/ruleta.gif"):
    embed = Embed(title="Ruleta #" + str(id), description="A zwycieza...", color=Colour.darker_grey())

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
        
    embed = Embed(title="Ruleta #" + str(id), description="Wygrywa... " + str(text) + "!", color=color)
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
    embed = Embed(title="Ruleta #" + str(id), description="Czas na gre do: " + str(formatted_time), color=Colour.darker_grey())
    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.add_field(name = "Koszt - 50 PPKT", value = "!niebieski = x2!\n!czerwony = x2! \n !zielony = x25!")
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateRuletaPlayers(players, id = 0):
    embed = Embed(title="Ruleta #" + str(id), description="", color=Colour.darker_grey())
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
    embed.add_field(name = "Ciekawostki: ", value = body, inline = False)
    embed.add_field(name = "Wrozba: ", value = wrozba, inline = False)
    embed.set_footer(text = "Do twojego konta zostalo przypisane 2000 pizzopkt!", icon_url = PARTY_FACE_ICON)
    return embed

def generateWinnerEmbed(user, userAvatarURL):
    embed = Embed(title="Gratulacje, " + user['name'] + "!", description=ai.askAI("Pogratuluj uzytkownikowi: \""+ user['name'] + "\" wygranej w dziennej loterii pizzopunktow w sposob "+random.choice(GRATULACJE)+"."), color=Colour.dark_green())
    embed.set_thumbnail(url = userAvatarURL)
    embed.add_field(name = "Do twojego konta przypisalismy 200 pkt + 10% twojej dotychczasowej ilosci pizzopunktow!", value="Woohoo!", inline = False)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateLoserEmbed(user, userAvatarURL):
    embed = Embed(title="Ojojoj, " + user['name'] + "...", description="Jestes dzisiejszym przegrywem..", color=Colour.dark_red())
    embed.set_thumbnail(url = userAvatarURL)
    embed.add_field(name = "Z twojego konta zostalo odebrane 10% ppkt.", value="Sprobuj sie odbic na hazard-lounge!", inline = False)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def uploadDoBartola(gif_path):
    try:
        headers = {
            "Authorization":BARTOLO_KEY
        }

        fc = None
        with open(gif_path, "rb") as f:
            fc = f.read()

        files = {
            "file":fc
        }
        response = requests.post('https://slots.smnfbb.com/upload', headers=headers, files=files)

        if response.status_code == 200:
            points.addPoints(db.retrieveUser('name', "Bartolo")['discord_id'], 10) # prowizja 
            return response.json()["url"]
        else:
            points.addPoints(db.retrieveUser('name', "Bartolo")['discord_id'], -1000) # kara
            return None
    except Exception as e:
        return None


def generateSlotsAnimation(id = 0, gif_path = "assets/gif/slots.gif", amount = 0, user = None):
    description = "Gratulacje, " + user['name'] + "!"
    color = Colour.dark_green()
    infoString = " - wygrales " + str(amount) + " pizzopunktow!"
    if amount < 0:
        description = "Oops.."
        color = Colour.dark_red()
        infoString = " - przegrales " + str(amount * -1) + " pizzopunktow.."
    embed = Embed(title="Slotsy #" + str(id), description=description, color=color)

    file = File(gif_path, filename = gif_path.split("/")[-1])
    embed.set_image(url="attachment://"+ gif_path.split("/")[-1])

    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.add_field(name = "Bilans gry:", value= user['name'] + infoString)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed, file

def generateUnknownUser(discord_id):
    embed = Embed(title="Nieznany uzytkownik" + str(discord_id), description="Uzytkownik o podanym ID nie istnieje w bazie!", color=Colour.red)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateHeistInvite(level, heist_name, message, time, id = 0):
    
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title="Nowy napad grupowy!", description="Czas na dolaczenie: " + str(time) + ".", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)

    embed.set_thumbnail(url = CRIMINAL_ICON_URL)
    embed.add_field(name = heist_name, value=message, inline = False)

    embed.add_field(name = "Aby dolaczyc napisz **!joinheist <KWOTA>**", value = "Twoj wklad ma wplyw na wysokosc potencjalnej nagrody!", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateHeistIntro(level, heist_name, message, id = 0):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title=heist_name, description=message, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)

    embed.set_thumbnail(url = CRIMINAL_ICON_URL)
    embed.add_field(name = "", value = "Trwaja przygotowania do napadu! Za jakis czas dowiecie sie, jak sprawdziliscie sie w swoich rolach!", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateHeistBody(level, heist_name, message, id = 0):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title=heist_name, description=message, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)

    embed.set_thumbnail(url = CRIMINAL_ICON_URL)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateHeistEnding(level, heist_name, message, id = 0):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title=heist_name, description=message, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)

    embed.set_thumbnail(url = CRIMINAL_ICON_URL)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateHeistInfo(level, heist_name, time, members):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title="Obecnie zbieramy ekipe na :", description=heist_name, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    description = ""
    for user in members:
        description += "* " + user[0] + "\n"
    embed.set_thumbnail(url = CRIMINAL_ICON_URL)
    if description != "":
        embed.add_field(name = "Obecna ekipa sklada sie z:", value=description, inline = False)
    else:
        embed.add_field(name = "Obecnie nie ma chetnych na ten napad. Mozesz byc pierwszy!", value=description, inline = False)

    embed.add_field(name = "Aby dolaczyc napisz **!joinheist <KWOTA>**", value = "Czas na dolaczenie do: " + str(time) + ".", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed
  
def generateHeistCanceled(heist_name):
    color = Colour.dark_orange()
    embed = Embed(title="Napad zostaje anulowany z powodu braku wystarczajacych uczestnikow! (min 2):", description=heist_name, color = color)
    embed.set_thumbnail(url = CRIMINAL_ICON_URL)
    embed.add_field(name = "Sprobujcie szczescia w nastepnym napadzie..", value="Punkty zostaly zwrocone.", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed
def generatePrisonRelease(users):
    color = Colour.dark_orange()
    description = ""
    for user in users:
        description += "* " + user['name'] + "\n"
    embed = Embed(title="Czlonkowie Pizza One Hit opuszczaja wiezienie!", description=description, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_thumbnail(url = PEPE_PRISON_URL)
    embed.add_field(name = "Mozecie ponownie korzystac z komend na DC!", value="", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateUserArrestedInfo(user):
    color = Colour.dark_gray()
    embed = Embed(title="Niestety, jestes aresztowany!", description="Nie mozesz korzystac z funkcjonalnosci bota.. Zostaniesz wypuszczony o 7 rano.", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_thumbnail(url = PEPE_PRISON_URL)
    pointsInfo = "Obecnie posiadasz "
    if user:
        pointsInfo += str(user['points']) + " ppkt.\nUzyj komendy **!wykup** aby wyjsc z wiezienia."
    embed.add_field(name = "Mozesz sie wykupic za 50% wartosci swoich punktow! (minimum 300)", value=pointsInfo, inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateFreedUser(user, cost):
    color = Colour.dark_green()
    embed = Embed(title="Witamy na wolnosci, " + user['name'] + "!", description="Po uiszczeniu oplaty w wysokosci "+str(cost)+" twoj prawnik Cie wyciagnal!", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_thumbnail(url = PEPE_LAWYER_URL)
    embed.add_field(name = "Mozesz ponownie korzystac z komend na DC!", value="", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateArrestedUsersInfo(users):
    color = Colour.dark_gray()
    description = ""
    for user in users:
        description += "* " + user['name'] + "\n"
    embed = Embed(title="Oto obecni zaaresztowani zloczyncy:", description=description, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    embed.set_thumbnail(url = PEPE_PRISON_URL)
    embed.add_field(name = "", value="Wyslijcie im paczki na swieta..", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateRewards(rewards):
    color = Colour.dark_green()
    embed = Embed(title="Nagrody na serwerze Pizza One Hit", description="Aby wykupic nagrode, napisz do roLab na PRIV.", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    description = ""
    for reward in rewards:
        description += "* " + str(reward['text']) + " - " + str(reward['cost']) + "\n"
    embed.set_thumbnail(url = PEPE_COIN_URL)
    embed.add_field(name = "Oto dostepne nagrody:", value=description, inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed

def generateAchievements(achievements):
    color = Colour.gold()
    embed = Embed(title="Osiagniecia na serwerze Pizza One Hit", description="Najwieksi z najwiekszych!", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = BOT_GIF_ADDRESS)
    description = ""
    for achievement in achievements:
        who = achievement['user']
        if who == "":
            who = "[TU MOZESZ BYC TY!]"
        description += "* " + str(achievement['achievement']) + " - " + str(who) + "\n" + str(achievement['description']) + "\n\n"
    embed.set_thumbnail(url = PEPE_PUCHAR_URL)
    embed.add_field(name = "Oto obecne osiagniecia:", value=description, inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = PIZZA_ICON_URL)
    return embed