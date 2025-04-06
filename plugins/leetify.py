import requests
import urllib.request
import bz2
import os
import shutil
import plugins.pizzadatabase as db

class Leetify:
    p1h_steamids = [
        "76561198034650343", # najwiekszyfanvirtusow
        "76561198022220729", # chrzanik444
        "76561198154621984", # jeezie
        "76561198002416756", # balor
        "76561198038116118", # bartolo 
        "76561199251416044", # mlody_szybki100cm
        "76561198164809479", # Scytyk
        "76561198030007267", # makaron
    ]

    def _get_player_recent_matches(self, player_id):
        r = requests.get(f"https://api.cs-prod.leetify.com/api/profile/id/{str(player_id)}")
        if r.status_code == 200:
            d = r.json()
            return d["games"]
        return []
    
    def get_new_matches(self):
        matches = []
        for id in self.p1h_steamids:
            matches = self._get_player_recent_matches(id)
            
            for m in matches:
                if db.retrieveLeetifyMatch(m["gameId"]) is None and \
                    m["gameId"] not in matches:
                    matches.append(m["gameId"])
            
        return matches

    def get_match_mvp(self, match_data):
        mvp = { "player_id": "", "rating": -100 }

        for player in match_data["playerStats"]:
            if player["leetifyRating"] > mvp["rating"]:
                mvp = {
                    "player_id": player["steam64Id"],
                    "rating": player["leetifyRating"]
                }

        return mvp
    
    def get_mvp_if_p1h_player(self, match_data):
        mvp = self.get_match_mvp(match_data)

        if mvp["player_id"] in self.p1h_steamids:
            return mvp["player_id"]
        
        return None
       
