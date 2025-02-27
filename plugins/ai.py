from google import genai
from os import environ

GOOGLE_AI_API_KEY = environ["GOOGLE_GEMINI_API_KEY"]
client = genai.Client(api_key=GOOGLE_AI_API_KEY)
chat = client.chats.create(model="gemini-2.0-flash")
MAX_LENGTH = 2000

def chatWithAI(message):
    response = chat.send_message_stream(message)
    returnMSG = ""
    for chunk in response:
        returnMSG += chunk.text
    return returnMSG

def getResponse(message):
    message += "\n Also ensure the response is rather short, no longer than 1000 characters"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=message)
    return response.text[:MAX_LENGTH] 

def getOneResponse(message):
    message += "\n Also ensure the response is rather short, no longer than 1000 characters"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=message)
    return response.text[:MAX_LENGTH] 