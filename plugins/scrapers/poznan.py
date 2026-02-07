from urllib.parse import urlparse, parse_qs
import urllib3
from bs4 import BeautifulSoup
import traceback
from datetime import datetime

from plugins.scrapers.scraper import Scraper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Poznan(Scraper):
    EVENT_DATES_PATH = "/api/shows/calendar?archive=0&per_page=10000&date_start={date_start}&date_end={date_end}"
    
    def __init__(self, url):
        super().__init__(url)

    def _get_events_and_dates(self):
        try:
            events = {}
            current_month = datetime.now().month
            current_year = datetime.now().year

            path = self.EVENT_DATES_PATH.format(date_start=f"{current_year}-{current_month}-1",date_end=f"{current_year+1}-{current_month}-1")
            response = self.session.get(self.url + path, headers=self.HEADERS, verify=False)
            response.raise_for_status()

            

            data = response.json()
            data = data["data"]

            for date in data:
                val = data[date]
                if "data" not in val:
                    continue

                for event in val["data"]:
                    if "relationships" not in event \
                        or "callendar" not in event["relationships"] \
                        or "data" not in event["relationships"]["callendar"]:
                        continue

                    event_attributes = event["attributes"]
                    callendar_data = event["relationships"]["callendar"]["data"]

                    for d in callendar_data:
                        callendar_attributes = d["attributes"]
                        dt = datetime.strptime(callendar_attributes["publication"], "%Y-%m-%d %H:%M:%S")

                        if event_attributes["title"] not in events:
                            events[event_attributes["title"]] = {
                                "title": event_attributes["title"],
                                "id": f"{d["id"]}",
                                "dates": []
                            }

                        events[event_attributes["title"]]["dates"].append({
                            "text": callendar_attributes["publication"],
                            "year": int(dt.year),
                            "month": int(dt.month)
                        })
            

            return list(events.values())
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            traceback.print_exc()
            return []

    def scrape(self):
        self.events = self._get_events_and_dates()
        
        return self.events
