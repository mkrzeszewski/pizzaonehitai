from urllib.parse import urlparse, parse_qs
import urllib3
from bs4 import BeautifulSoup
import traceback
from datetime import datetime
from plugins.scrapers.scraper import Scraper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Iksoris(Scraper):
    ALL_EVENTS_PATH = "/rezerwacja/wydarzenie.html"
    EVENT_DATES_PATH = "/index/ajax.html?month={month}&year={year}&idw={idw}&ajax=pobierzKalendarz"

    def __init__(self, url):
        super().__init__(url)

    def _get_events(self):
        try:
            response = self.session.get(self.url + self.ALL_EVENTS_PATH, headers=self.HEADERS, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            events = []
            for a_tag in soup.find_all('a', attrs={"class": "btn btn-primary text-uppercase w-100"}):
                parsed_url = urlparse(a_tag["href"])
                query_params = parse_qs(parsed_url.query)
                events.append({
                    "title": a_tag.get('title').replace("Wybierz ","",1), 
                    "id": query_params["idw"][0],
                    "dates": []
                })
            
            return events
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            traceback.print_exc()
            return []

    def _get_dates_for_month(self, event, year, month):
        try:
            path = self.EVENT_DATES_PATH.format(month=month, year=year, idw=event)
            response = self.session.get(self.url + path, headers=self.HEADERS, verify=False)
            response.raise_for_status()

            data = response.json()

            if data["brakTerminow"] == True:
                return []

            html = data["kalendarzHtml"]
            soup = BeautifulSoup(html, 'html.parser')

            dates = []
            if len(soup.find_all('p', class_=["card-text","text-muted","mb-1"])) > 0:
                elements = soup.find_all('p', class_=["card-text","text-muted","mb-1"])
                for p_tag in elements:
                    dates.append({
                        "text": p_tag.text.strip(),
                        "year": year,
                        "month": month
                    })
            elif len(soup.find_all("button", class_="dzien-z-terminami")) > 0:
                elements = soup.find_all("button", class_="dzien-z-terminami")
                for btn in elements:
                    dates.append({
                        "text": btn["data-day"].strip(),
                        "year": year,
                        "month": month
                    })
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            traceback.print_exc()
            return []

        return dates

    def _get_dates(self, event):
        dates = []
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

                tmp_dates = self._get_dates_for_month(event["id"], year, month)
                dates.extend(tmp_dates)

        return dates
    
    def scrape(self):
        self.events = self._get_events()
        for event in self.events:
            dates = self._get_dates(event)
            event["dates"] = dates

        return self.events