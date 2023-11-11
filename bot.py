import discord
import responses

async def sendMessage(message, user_message, is_private):
    try:
        response = responses.handleResponse(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def runDiscordBot():
    #to do: parse file location
    TOKEN = '#INSERT YOUR TOKEN HERE'
    with open('token.tkn') as inputToken:
        TOKEN=inputToken.read()
    
    client = discord.Client(intents = discord.Intents.default())

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        print("jakas wiadomosc")
        if message.author == client.user:
            return
        print(message.content)

    client.run(TOKEN)