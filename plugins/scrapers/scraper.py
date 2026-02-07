from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from abc import ABC, abstractmethod
from plugins.scrapers.gdynia import Gdynia
from plugins.scrapers.iksoris import Iksoris
from plugins.scrapers.poznan import Poznan
from plugins.scrapers.roma import Roma
from plugins.scrapers.scraper import Scraper
from plugins.scrapers.variete import Variete
from plugins.scrapers.wroclaw import Wroclaw


class Scraper(ABC):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}

    def __init__(self, url):
        self.url = url
        self.events = None
        self._create_session()

    def _create_session(self):
        retry_strategy = Retry(
            total=5,               # total number of retries
            backoff_factor=5,      # delay factor: 1 -> 1s, 2 -> 2s, exponential
            status_forcelist=[429, 500, 502, 503, 504],  # which HTTP codes to retry
            allowed_methods=["GET", "POST"]  # methods to retry
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def compare_dates(self, event):
        current_month = datetime.now().month
        current_year = datetime.now().year
        filtered_dates = []
        new_dates = []
        dates = event["dates"]
        curr_event = [e for e in self.events if e["title"] == event["title"]][0]

        for d in dates:
            if d["year"] <= current_year and d["month"] < current_month:
                continue

            filtered_dates.append(d)

        if (len(curr_event["dates"]) - len(filtered_dates)) >= 0:
            for ed in curr_event["dates"]:
                if len([e for e in filtered_dates if e == ed]) == 0:
                    new_dates.append(ed)

        return new_dates

    def filter_events(self):
        current_month = datetime.now().month
        current_year = datetime.now().year

        for event in self.events:
            filtered_dates = []
            for date in event["dates"]:
                if date["year"] < current_year:
                    continue
                if date["year"] == current_year and date["month"] < current_month:
                    continue

                filtered_dates.append(date)
            
            event["dates"] = filtered_dates

        return self.events

    @abstractmethod
    def scrape(self):
        """
        Zwraca wydarzenia w formacie
        [
            {
                "title":"tytul",
                "id":"id",
                "dates":[
                    {
                        "text": "15 Luty 2026",
                        "year": 2026,
                        "month": 2
                    }
                ]
            }
        ]

        """
        pass