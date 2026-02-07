from urllib.parse import urlparse, parse_qs
import urllib3
from bs4 import BeautifulSoup
import traceback
from datetime import datetime

from plugins.scrapers.scraper import Scraper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Roma(Scraper):
    ALL_EVENTS_PATH = "/"
    EVENT_DATES_PATH = "/index/ajax.html?ajax=getKalendarzHtml&m={month}&y={year}"

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
            path = self.EVENT_DATES_PATH.format(month=month, year=year)
            response = self.session.get(self.url + path, headers=self.HEADERS, verify=False)
            response.raise_for_status()
            
            print(f"Scraping {self.url + path}...")

            data = response.json()

            if data["count"] == 0:
                return []

            html = data["data"]
            soup = BeautifulSoup(html, 'html.parser')

            events = {}
            if len(soup.find_all('td', attrs={"data-dzien_data": True})) > 0:
                elements = soup.find_all('td', attrs={"data-dzien_data": True})
                for td_tag in elements:
                    dzien_data = td_tag.get("data-dzien_data")
                    data_title = td_tag.get("data-title")

                    soup = BeautifulSoup(data_title, "html.parser")

                    rows = soup.find_all("tr")

                    for row in rows:
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            text = cells[1].get_text(strip=True)
                            hour, name = text.split(" ", 1)

                            if name not in events:
                                events[name] = {
                                    "title": name,
                                    "id": "0",
                                    "dates": []
                                }

                            events[name]["dates"].append({
                                "text": f"{dzien_data} {hour}",
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
