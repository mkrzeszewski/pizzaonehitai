import requests
from datetime import datetime, timedelta
import plugins.pizzadatabase as db
from bs4 import BeautifulSoup
import random

FLORIDA_MAN_URL = "https://floridamanbirthday.org/"
BRITANNICA_URL = "https://www.britannica.com/on-this-day/"
def transform_date(date_str):
    try:
        month, day = map(int, date_str.split('-'))
        # Format as "month-day" (lowercase month name)
        return f"{datetime(1900, month, day).strftime('%B').lower()}-{day}"
    except ValueError:
        return f"Invalid date: {date_str}"

def getBirthdayPeople():
    #connect to mongodb database and get proper database
    
    #get todays date - format it accordingly to <MONTH>-<DAY> - 31st of January would be 1-31
    current_time = datetime.now() + timedelta(hours=1)

    users = db.retrieveUsers('birthday', str(current_time.month) + "-" + str(current_time.day))

    #if it exists; return list, else return None
    birthdayBoys = []
    if users:
        for user in users:
            birthdayBoys.append(user)
    else:
        return None
    return birthdayBoys

def getFloridaMan(bday):
    URL = FLORIDA_MAN_URL + transform_date(bday)
    response = requests.get(URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        #print(soup)
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        if paragraphs:
            for paragraph in paragraphs:
                if "Florida" in paragraph or "florida" in paragraph:
                    return paragraph


def getWhatHappenedOnThatDay(bday):
    URL = BRITANNICA_URL + transform_date(bday)
    response = requests.get(URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        #print(soup)
        searchclass = "card-body font-serif"
        container = soup.find_all(class_=searchclass)
        if container:
            return container[random.randint(0, len(container) - 1)].get_text(separator = " ", strip = True)
