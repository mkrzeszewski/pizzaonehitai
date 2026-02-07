from urllib.parse import urlparse, parse_qs
import urllib3
from bs4 import BeautifulSoup
import traceback
from datetime import datetime

from plugins.scrapers.scraper import Scraper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Gdynia(Scraper):
    EVENT_DATES_PATH = "/pl/repertuar.html"
    def __init__(self, url):
        super().__init__(url)
    def _get_events_and_dates(self):
        try:
            events = {}
            response = self.session.get(self.url + self.EVENT_DATES_PATH, headers=self.HEADERS, verify=False)
            response.raise_for_status()

            print(f"Scraping {self.url + self.EVENT_DATES_PATH}...")

            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("div", class_="row spektakl_row kalendarium_row")

            for row in rows:
                day = row.get("data-day")
                month = row.get("data-month")
                year = row.get("data-year")
                
                details = row.find("div", class_="col-sm-8 col-md-7 spektakl_szczegoly")
                if details:
                    name_div = details.find("div", class_="h2")
                    hour_div = details.find("div", class_="h6")
                    
                    if name_div and hour_div:
                        event_name = name_div.get_text(strip=True)
                        hour = hour_div.get_text(strip=True).split(" /")[0]

                        if event_name not in events:
                            events[event_name] = {
                                "title": event_name,
                                "id": "0",
                                "dates": []
                            }

                        events[event_name]["dates"].append({
                            "text": f"{year}-{month}-{day} {hour}",
                            "year": int(year),
                            "month": int(month)
                        })

            return list(events.values())
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            traceback.print_exc()
            return []

    def scrape(self):
        self.events = self._get_events_and_dates()
        return self.events
