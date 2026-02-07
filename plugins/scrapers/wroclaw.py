from urllib.parse import urlparse, parse_qs
import urllib3
from bs4 import BeautifulSoup
import traceback
from datetime import datetime
import re

from plugins.scrapers.scraper import Scraper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Wroclaw(Scraper):
    EVENT_DATES_PATH = "/termin.html?date_termin={date_termin}"
    
    def __init__(self, url):
        super().__init__(url)

    def _get_events_and_dates(self):
        try:
            events = {}
            current_month = datetime.now().month
            current_year = datetime.now().year
            c = 0

            for year in range(current_year,current_year+2):
                if year > current_year:
                    current_month = 1
                
                for month in range(current_month,13):
                    c += 1
                    if c > 12: # 12 msc w przod
                        break

                    tmp_events = self._get_events_and_dates_for_month(year, month)
                    for event in tmp_events:
                        if event["title"] not in events:
                            events[event["title"]] = event
                        else:
                            events[event["title"]]["dates"].extend(event["dates"])

            return list(events.values())
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            traceback.print_exc()
            return []

    def _get_events_and_dates_for_month(self, year, month):
        try:
            path = self.EVENT_DATES_PATH.format(date_termin=f"{year}-{month}-1")
            response = self.session.get(self.url + path, headers=self.HEADERS, verify=False)
            response.raise_for_status()
            
            print(f"Scraping {self.url + path}...")

            soup = BeautifulSoup(response.text, "html.parser")

            events = {}
            tmp_events = []
            current_date = None

            for tr in soup.find_all("tr"):
                if "term" in tr.get("class", []):
                    # Extract the date from the "term" row
                    date_text = tr.get_text(strip=True)
                    match = re.search(r"\d{2}-\d{2}", date_text)
                    if match:
                        current_date = match.group(0)
                    
                elif "b" in tr.get("class", []):
                    # Event rows
                    if current_date:
                        name_tag = tr.find("a", class_="txt")
                        name = name_tag.get_text(strip=True) if name_tag else "N/A"
                        tmp_events.append((name, current_date))

            for name, date in tmp_events:
                if name not in events:
                    events[name] = {
                        "title": name,
                        "id": "0",
                        "dates": []
                    }

                events[name]["dates"].append({
                    "text": f"{date}-{year}",
                    "year": year,
                    "month": month
                })
            
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            traceback.print_exc()
            return []

        return list(events.values())

    def scrape(self):
        self.events = self._get_events_and_dates()
        
        return self.events
