import plugins.pizzadatabase as db
import plugins.scrapers.scraper as scrapers
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SYSTEMS = [
    {
        "name":"iksoris",
        "handler": scrapers.Iksoris
    },
    {
        "name":"roma",
        "handler": scrapers.Roma
    },
    {
        "name":"variete",
        "handler": scrapers.Variete
    },
    {
        "name":"gdynia",
        "handler": scrapers.Gdynia
    },
    {
        "name":"poznan",
        "handler": scrapers.Poznan
    },
    {
        "name":"wroclaw",
        "handler": scrapers.Wroclaw
    }
]

def checkNewEvents():
    try:
        TEATRS = db.retrieveAllTheatres()
        for t in TEATRS:
            system = [e for e in SYSTEMS if e["name"] == t["system"]][0]["handler"]

            i = system(t["url"])
            wydarzenia_on_site = i.scrape()
            i.filter_events()

            for w in wydarzenia_on_site:
                if len(w["dates"]) == 0:
                    continue

                w["teatr"] = t["name"]
                wydarzenie_in_db = db.retrieveEventsFromTheatre(t['name'], w['title'])
                new_dates = []

                if len(wydarzenie_in_db) == 0:
                    new_dates = w["dates"]
                else:
                    new_dates = i.compare_dates(wydarzenie_in_db[0])

                if len(new_dates) > 0:
                    db.updateEvent(w['title'], w['teatr'], w)
                    
                    msg = f"Nowe terminy na **{w["title"]}** w {w["teatr"]}:\n"
                    for d in new_dates:
                        msg += f"- {d["text"]}\n"
                    print(msg)
    except Exception as e:
        print(e)
# def getAllEventsIksoris(url):
#     try:
#         # Fetch the web content
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}  # Some sites require user-agent
#         response = requests.get(url, headers=headers, verify=False)
#         response.raise_for_status()  # Raise an error for bad status codes
#         # Parse the HTML content
#         soup = BeautifulSoup(response.text, 'html.parser')
#         # Find all <a> tags and extract href attributes
#         events = []
#         for h2_tag in soup.find_all('h2', ["h5","text-primary"]):
#            events.append(h2_tag.get_text())
#         return events
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching {url}: {e}")
#         return []

# def checkNewEvents():
#     returnText = ""
#     theatreEvents = []
#     theatres = db.retrieveAllTheatres()
#     for theatre in theatres:
#         eventsOnSite = []
#         newEvents = []
#         if theatre['system'] == "iksoris":
#             eventsOnSite = getAllEventsIksoris(theatre['url'])
#         # elif theatre['system'] == "roma":
#         #     x = 1
#         # elif theatre['system'] == "xxx":
#         #     x = 1

#         eventsInDb = db.retrieveEventsFromTheatre(theatre['name'])
#         for event in eventsInDb:
#             if event['name'] not in eventsOnSite:
#                 db.removeEvent('name',event['name'])
        
#         for event in eventsOnSite:
#             if not db.retrieveEventFromTheatre(theatre['name'], event):
#                 newEvents.append(event)
#                 db.addEvent(event, theatre['name'])

#         if len(newEvents) > 0:
#             returnText += "Nowe wydarzenie na stronie " + str(theatre['name']) + ".\n"
#             returnText += "\n - ".join(newEvents)
#             theatreEvents.append([theatre, newEvents])
#     return theatreEvents