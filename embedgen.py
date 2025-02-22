import random
from discord import Embed, Colour
import time
import requests
from os import environ

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

PHOTO_REFERENCE_URL = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference="
API_KEY="&key=" + environ["GOOGLE_MAPS_API_KEY"]

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

def generateEmbedFromRestaurant(restaurant, userlist):
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