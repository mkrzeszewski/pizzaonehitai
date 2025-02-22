import random
import plugins.weather as weather
import plugins.horoscope as horoskop
import plugins.pizzadatabase as db
import plugins.embedgen as embedgen
def getWeather():
    return weather.getLodzWeather()

def handleResponse(usrMessage, author) -> str:
    message = usrMessage.lower()
    returnEmbed = None
    returnText = "[!] - Nie znam komendy: \"" + usrMessage + "\""

    if message == 'whoami':
        returnText =  db.retrieveUser('discord_id', str(author))['name']

    if message == 'bingo':
        returnText =  'bingo'

    if message == 'roll':
        returnText =  str(random.randint(1,6))

    if message == 'embed':
        returnText =  "embed_test"

    if message == "pogoda":
        returnText =  weather.getLodzWeather()

    if message == "horoskop" or message == "zodiak" or message == "mojhoroskop":
        name = db.retrieveUser('discord_id', str(author))['name']
        sign, text = horoskop.getHoroscopeForUser('discord_id', str(author))
        returnEmbed = embedgen.generateEmbedFromHoroscope(text, sign, name)

    return returnEmbed, returnText