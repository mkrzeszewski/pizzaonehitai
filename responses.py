import random

def handleResponse(usrMessage) -> str:
    message = usrMessage.lower()

    if message == 'bingo':
        return 'chuj ci na ryj!!!'
    
    if message == 'roll':
        return str(random.randint(1,6))

    return (usrMessage + " hahaha (nieorzumiem o chuj Ci chodzi)")