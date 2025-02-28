# import google.generativeai as genai
# from os import environ
# import plugins.pizzadatabase as db

# GOOGLE_AI_API_KEY = environ["GOOGLE_GEMINI_API_KEY"]

# genai.configure(api_key=GOOGLE_AI_API_KEY)

# model = genai.GenerativeModel("models/gemini-2.0-flash", system_instruction="")
# chat = model.start_chat()

# def resetModel():
#     initialInstructions = db.retrieveAllAIInstructions()
#     instructionString = ""
#     for record in initialInstructions:
#         instructionString += record['instruction'] + "\n"
#     global model, chat
#     model = genai.GenerativeModel("models/gemini-2.0-flash", system_instruction = instructionString)
#     chat = model.start_chat()

# def chatwithAI(message):
#     return chat.send_message(message).text

# def askAI(message):
#     return model.generate_content(message).text

# resetModel()

from google import genai
from os import environ
import plugins.pizzadatabase as db

GOOGLE_AI_API_KEY = environ["GOOGLE_GEMINI_API_KEY"]
client = genai.Client(api_key=GOOGLE_AI_API_KEY)
chat = client.chats.create(model="gemini-2.0-flash")
initialInstructions = db.retrieveAllAIInstructions()
for record in initialInstructions:
    chat.send_message(record['instruction'])

MAX_LENGTH = 1500

def chatWithAI(message):
    return chat.send_message(message).text

def getResponse(message):
    message += "\n Also ensure the response is rather short, no longer than 1000 characters"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=message)
    return response.text[:MAX_LENGTH] 

def askAI(message):
    message += "\n Also ensure the response is rather short, no longer than 1000 characters"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=message)
    return response.text[:MAX_LENGTH] 