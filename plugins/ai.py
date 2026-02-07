import google.generativeai as genai
import plugins.pizzadatabase as db
import json
from os import environ

GOOGLE_AI_API_KEY = environ["GOOGLE_GEMINI_API_KEY"]
MAX_LENGTH = 1500
genai.configure(api_key=GOOGLE_AI_API_KEY)

#wide use chat for p1h
initialInstructions = db.retrieveAllAIInstructions()
instructionString = ""
for record in initialInstructions:
    instructionString += record['instruction'] + "\n"
if instructionString.strip():
    model = genai.GenerativeModel(
        "models/gemini-2.0-flash", system_instruction = instructionString
    )
else:
    model = genai.GenerativeModel("models/gemini-2.0-flash")
chat = model.start_chat()

#ai for heist generation in heist.py
with open("config/heist-instructions.json", "r", encoding="utf-8") as file:
    heistInstruction = json.load(file)
heistModel = genai.GenerativeModel(
    "models/gemini-2.0-flash", system_instruction = heistInstruction
)
heistChat = heistModel.start_chat()

#ai for stock generation
with open("config/stocks-instructions.json", "r", encoding="utf-8") as file:
    stockInstruction = json.load(file)
stockModel = genai.GenerativeModel(
    "models/gemini-2.0-flash", system_instruction = stockInstruction
)
stockChat = stockModel.start_chat()

def chatWithAI(message):
    return chat.send_message(message).text

def askAI(message):
    return model.generate_content(message).text

def resetModel():
    global model, chat
    model = genai.GenerativeModel("models/gemini-2.0-flash", system_instruction = instructionString)
    chat = model.start_chat()

def generateHeist(message):
    return heistModel.generate_content(message).text

def generateStocks(message):
    return stockModel.generate_content(message).text