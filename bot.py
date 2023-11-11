import discord
import responses

async def sendMessage(message, user_message, is_private):
    try:
        response = responses.handleResponse(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def runDiscordBot():
    TOKEN = '#INSERT YOUR TOKEN HERE'
    client = discord.Client()

    @client.event
    async def onReady():
        print(f'{client.user} is now running!')

    client.run(TOKEN)