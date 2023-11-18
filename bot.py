import discord
import responses
import requests
from discord.ext import tasks

async def sendMessage(message, user_message, is_private):
    try:
        response = responses.handleResponse(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

async def sendWeather():
    #1172911430601822238 - gruby-test channnel
    #1032698616910983168 - league of debils
    #test
    pass

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

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        userMessage = str(message.content)
        if userMessage[0] == '!':
            userMessage = userMessage[1:]
            await sendMessage(message, userMessage, is_private=False)

    index = 0

    @tasks.loop(hours = 1.0)
    async def sendWeather():
        channel = client.get_channel(1172911430601822238)
        #await channel.send('test')
        
        BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
        CITY = "lodz,pl"
        API_KEY = "1f4b8c61bd3abc5071c8b2e823e465cb"
        # upadting the URL
        URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
        FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?"
        FORECAST_FINAL_URL = FORECAST_URL + "q=" + CITY + "&appid=" + API_KEY + "&cnt = 60"
        # HTTP request
        response = requests.get(URL)
        if response.status_code == 200:
            # # getting data in the json format
            data = response.json()
            # # getting the main dict block
            main = data['main']
            # # getting temperature
            temperature = main['temp']
            # # getting the humidity
            # humidity = main['humidity']
            # # getting the pressure
            # pressure = main['pressure']
            # # weather report
            # report = data['weather']
            # print(f"{CITY:-^30}")
            # print(f"Temperature: {temperature}")
            # print(f"Humidity: {humidity}")
            # print(f"Pressure: {pressure}")
            # print(f"Weather Report: {report[0]['description']}")
            if temperature >= 273.0:
                #await channel.send("Temperaturka w Łodzi wynosi: "+ str(round(temperature - 273.0, 1)) +"°c. L4D2 już blisko!")
                print("zimno")
            else:
                print("cieplo")
                #await channel.send("@everyone TO NIE SA CWICZENIA, CZAS NA LEFT 4 DEAD 2 - TEMPERATURA W LODZI TO : "+ str(round(temperature - 273.0, 1)) + "°c.")

        else:
            print(response.status_code)

    client.run(TOKEN)