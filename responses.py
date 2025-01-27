import random
import plugins.weather as weather

def handleResponse(usrMessage) -> str:
    message = usrMessage.lower()

    if message == 'bingo':
        return 'bingo'
    if message == 'roll':
        return str(random.randint(1,6))
    if message == 'embed':
        return "embed_test"
    if message == "pogoda":
        return weather.getLodzWeather()
    
    return (usrMessage + " hahaha (nie rozumiem o chuj Ci chodzi)")