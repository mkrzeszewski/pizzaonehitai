import requests

def getLodzWeather():
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = "lodz,pl"
    API_KEY = "1f4b8c61bd3abc5071c8b2e823e465cb"
    # upadting the URL
    URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?"
    FORECAST_FINAL_URL = FORECAST_URL + "q=" + CITY + "&appid=" + API_KEY + "&cnt = 60"
    # HTTP request
    response = requests.get(URL)
    if response.status_code == 200:
        # # getting data in the json format
        data = response.json()
        # # getting the main dict block
        main = data['main']
        # # getting temperature
        temperature = main['temp']
        # # getting the humidity
        # humidity = main['humidity']
        # # getting the pressure
        # pressure = main['pressure']
        # # weather report
        # report = data['weather']
        # print(f"{CITY:-^30}")
        # print(f"Temperature: {temperature}")
        # print(f"Humidity: {humidity}")
        # print(f"Pressure: {pressure}")
        # print(f"Weather Report: {report[0]['description']}")
        return "Temperaturka w Łodzi wynosi: " + str(round(temperature - 273.0, 1)) + "°c."
    else:
        return "Problem z API - status code: " + response.status_code + "."