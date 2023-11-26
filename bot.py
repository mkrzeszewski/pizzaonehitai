import discord
import responses
from discord.ext import tasks
import weather
import riotapi

WIN_ICON_URL = "https://cdn.discordapp.com/emojis/804525960345944146.webp?size=96&quality=lossless" #"https://elocentral.com/wp-content/uploads/2021/03/105050041_626416314631979_3504539849394714483_o-2.png"
LOSE_ICON_URL = "https://cdn3.emoji.gg/emojis/PepeHands.png" #"https://www.pngkey.com/png/full/713-7131234_image-rights-to-riot-games.png"
LOL_ICON = "https://raw.githubusercontent.com/github/explore/b088bf18ff2af3f2216294ffb10f5a07eb55aa31/topics/league-of-legends/league-of-legends.png"
FOOTER_ICON = "https://cdn3.emoji.gg/emojis/3149-jinx-evil.png"

async def sendMessage(message, user_message, is_private):
    try:
        response = responses.handleResponse(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def generateEmbedFromMatch(results,players,matchID):
        playerList = ""
        for player in players:
            playerList = playerList + player + ", "
        playerList = playerList[:-2]
        print (str("Chłopaki: " + playerList + " zagrali sobie ARAMka!"))
        print(results[:-1])
        
        endGameStatus = "Kolejna przegrana.."
        endGameIcon = LOSE_ICON_URL
        endColour = discord.Colour.red()

        if(results[-2] == "win"):
            endGameStatus = "EZ WIN"
            endGameIcon = WIN_ICON_URL
            endColour = discord.Colour.green()
            
        embed = discord.Embed(title = str(playerList + " zagrali sobie ARAMka!"), description = str(results[-1]), colour = endColour )
        embed.set_author(name = endGameStatus, icon_url = endGameIcon)
        embed.set_thumbnail(url = LOL_ICON)
        for result in results[:-2]:
            embed.add_field(name = "", value = result, inline = False)

        embed.set_footer(text = str(matchID), icon_url = FOOTER_ICON)
        return embed
def runDiscordBot():
    #to do: parse file location
    TOKEN = '#INSERT YOUR TOKEN HERE'
    with open('token.tkn') as inputToken:
        TOKEN=inputToken.read()
    
    intents_temp = discord.Intents.default()
    intents_temp.message_content = True
    client = discord.Client(intents = intents_temp)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        sendWeather.start()
        analyzeMatchHistory.start()
        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        userMessage = str(message.content)
        if userMessage[0] == '!':
            userMessage = userMessage[1:]
            commands = userMessage.split(" ")
            if len(commands) > 1:
                if commands[0] == "analyze":
                    results, players = riotapi.analyzeMatch(riotapi.getMatchData(str(commands[1])), False)
                    if len(results) > 0 :
                        await message.channel.send(embed=generateEmbedFromMatch(results,players,commands[1]))
                    else:
                        print("something's wrong")
            else:
                await sendMessage(message, userMessage, is_private=False)

    @tasks.loop(hours = 1.0)
    async def sendWeather():
        #channel = client.get_channel(1172911430601822238)
        print (weather.getLodzWeather())

    @tasks.loop(minutes = 5.0)
    async def analyzeMatchHistory():
        playerList = []
        playersFile = open("lol-players.txt","r")
        playerList = playersFile.read().splitlines()
        playersFile.close()
        matchesToAnalyze = []
        for player in playerList:
            tempMatches = riotapi.getUserMatchHistory(player)
            for match in tempMatches:
                matchesToAnalyze.append(match)
        if len(matchesToAnalyze) == 0:
            print ("Nie ma czego analizowac..")
        else:
            for match in matchesToAnalyze:
                print ("Analiza meczu: " + str(match))
                matchData = riotapi.getMatchData(match)
                if matchData == 0:
                    pass
                else:
                    channel = client.get_channel(1172911430601822238)
                    results, players = riotapi.analyzeMatch(matchData, True)
                    if len(results) > 0 and len(players) > 1:
                        await channel.send(embed=generateEmbedFromMatch(results,players,matchData['metadata']['matchId']))
                    else:
                        print ("ktos gral solo - match : " + str(matchData['metadata']['matchId']))
        print("koniec")
        riotapi.matches = []
    client.run(TOKEN)