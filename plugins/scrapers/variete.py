from urllib.parse import urlparse, parse_qs
import urllib3
from bs4 import BeautifulSoup
import traceback
from datetime import datetime

from plugins.scrapers.scraper import Scraper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Variete(Scraper):
    EVENT_DATES_PATH = "/api/repertoire?startDate={startDate}&endDate={endDate}"

    def __init__(self, url):
        super().__init__(url)

    def _get_events_and_dates(self):
        try:
            events = {}
            current_month = datetime.now().month
            current_year = datetime.now().year

            path = self.EVENT_DATES_PATH.format(startDate=f"{current_year}/{current_month}/1", endDate=f"{current_year+1}/{current_month}/31")
            response = self.session.get(self.url + path, headers=self.HEADERS, verify=False)
            response.raise_for_status()

            
            print(f"Scraping {self.url + path}...")

            data = response.json()

            for event in data:
                if not ("title" in event and "rendered" in event["title"]) \
                    or not ("date" in event):
                    continue

                title = event["title"]["rendered"]
                date_str = event["date"]
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                year = date.year
                month = date.month

                if title not in events:
                    events[title] = {
                        "title": title,
                        "id": "0",
                        "dates": []
                    }

                events[title]["dates"].append({
                    "text": date_str,
                    "year": year,
                    "month": month
                })

            return list(events.values())
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            traceback.print_exc()
            return []

    def scrape(self):
        self.events = self._get_events_and_dates()
        
        return self.events
