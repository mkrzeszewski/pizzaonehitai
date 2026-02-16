import plugins.pizzadatabase as db
import plugins.scrapers as scrapers
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
        returnArray = []
        

        #events = [{"teatr", [{"event", [data1, data2]}, {"event", [data1,data2]}]}, {teatr2 ...}]
        for t in TEATRS:
            eventArray = []
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
                    db.updateEvent(w['teatr'], w['title'], w)
                    
                    msg = f"Nowe terminy na **{w["title"]}** w {w["teatr"]}:\n"
                    eventArray.append([w["title"], new_dates])
                    for d in new_dates:
                        msg += f"- {d["text"]}\n"
                    print(msg)
            if eventArray:
                returnArray.append([t['name'], eventArray])
        return returnArray
    except Exception as e:
        print(e)