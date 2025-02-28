import google.generativeai as genai
from os import environ
import plugins.pizzadatabase as db

GOOGLE_AI_API_KEY = environ["GOOGLE_GEMINI_API_KEY"]

genai.configure(api_key=GOOGLE_AI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.0-flash", system_instruction="")
chat = model.start_chat()

def resetModel():
    initialInstructions = db.retrieveAllAIInstructions()
    instructionString = ""
    for record in initialInstructions:
        instructionString += record['instruction'] + "\n"
    global model, chat
    model = genai.GenerativeModel("models/gemini-2.0-flash", system_instruction = instructionString)
    chat = model.start_chat()

def chatwithAI(message):
    return chat.send_message(message).text

def askAI(message):
    return model.generate_content(message).text

resetModel()