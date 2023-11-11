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
    
    intents_temp = discord.Intents.default()
    client = discord.Client(intents = intents_temp)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        print (message.author)

        userMessage = str(message.content)
        print(userMessage)
        if userMessage[0] == '?':
            userMessage = userMessage[1:]
            await sendMessage(message, userMessage, is_private=False)

    client.run(TOKEN)