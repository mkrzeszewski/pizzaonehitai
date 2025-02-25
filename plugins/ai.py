from google import genai
from os import environ

GOOGLE_AI_API_KEY = environ["GOOGLE_GEMINI_API_KEY"]
client = genai.Client(api_key=GOOGLE_AI_API_KEY)
MAX_LENGTH = 2000

def getResponse(message):

    message += "\n Also ensure the response is rather short, no longer than 1000 characters"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=message)
    
    return response.text[:MAX_LENGTH] 

def getResponse(message):

    message += "\n Also ensure the response is rather short, no longer than 1000 characters"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=message)
    
    return response.text[:MAX_LENGTH] 