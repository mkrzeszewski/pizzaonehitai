import plugins.pizzadatabase as db
import requests
from bs4 import BeautifulSoup

def getAllEventsIksoris(url):
    try:
        # Fetch the web content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}  # Some sites require user-agent
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all <a> tags and extract href attributes
        events = []
        for h2_tag in soup.find_all('h2', ["h5","text-primary"]):
           events.append(h2_tag.get_text())
        
        print(events)
        return events

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def checkNewEvents():
    returnText = ""
    theatreEvents = []
    theatres = db.retrieveAllTheatres()
    for theatre in theatres:
        eventsOnSite = []
        if theatre['system'] == "iksoris":
            eventsOnSite = getAllEventsIksoris(theatre['url'])
            print("iksoris")
        elif theatre['system'] == "roma":
            print("ROMA")
        elif theatre['system'] == "xxx":
            print("xxx")

        eventsInDb = db.retrieveAllEvents()
        newEvents = []
        
        for event in eventsInDb:
            if event['name'] not in eventsOnSite:
                db.removeEvent('name',event['name'])
        
        for event in eventsOnSite:
            eventsInDb = list(db.retrieveEventNamesFromTheatre(theatre['name'], event))
            if len(eventsInDb) == 0:
                newEvents.append(event)
                db.addEvent(event, theatre['name'])

        if len(newEvents) > 0:
            returnText += "Nowe wydarzenie na stronie " + str(theatre['name']) + ".\n"
            returnText += "\n - ".join(newEvents)
            theatreEvents.append([theatre,newEvents])

    print(theatreEvents)
    return theatreEvents