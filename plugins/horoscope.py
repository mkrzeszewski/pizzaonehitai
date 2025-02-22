


import requests
from bs4 import BeautifulSoup
import plugins.pizzadatabase as db
HOROSKOP_URL = "https://horoskop.wp.pl/horoskop/horoskop-dzienny/"

horoscope_dates = {
        "koziorozec": [(1, 1), (1, 19)],
        "wodnik": [(1, 20), (2, 18)],
        "ryby": [(2, 19), (3, 20)],
        "baran": [(3, 21), (4, 19)],
        "byk": [(4, 20), (5, 20)],
        "bliznieta": [(5, 21), (6, 20)],
        "rak": [(6, 21), (7, 22)],
        "lew": [(7, 23), (8, 22)],
        "panna": [(8, 23), (9, 22)],
        "waga": [(9, 23), (10, 22)],
        "skorpion": [(10, 23), (11, 21)],
        "strzelec": [(11, 22), (12, 21)],
        "koziorozec": [(12, 22), (12, 31)]
    }

def getHoroscopeName(month_day: str) -> str:
    try:
        month, day = map(int, month_day.split("-"))
    except ValueError:
        return "Invalid date format. Use 'MM-DD'."
    for sign, (start, end) in horoscope_dates.items():
        start_month, start_day = start
        end_month, end_day = end
        if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            return sign

    return "Invalid date."


def getHoroscopeForUser(key, value):
    sign = getHoroscopeName(db.retrieveUser(key,value)['birthday'])
    response = requests.get(HOROSKOP_URL + sign)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        container_id = "horoskop_opis"  # Replace with the actual ID
        container = soup.find(id=container_id)
        if container:
            paragraphs = [p.get_text(strip=True) for p in container.find_all("p")]
            if paragraphs:
                return sign, paragraphs[0]
            else:
                print("[ERROR] - cos poszlo nie tak podczas pobierania z znaku zodiaku..")
        else:
            print(f"Element with ID '{container_id}' not found.")