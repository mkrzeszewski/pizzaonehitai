import argparse
import googlemaps
import numpy as np
from os import environ
from pymongo import MongoClient

GOOGLE_API_KEY = environ["GOOGLE_MAPS_API_KEY"]

#connect to mongodb database and get proper database
CONN_URL = "mongodb://" + environ["MONGO_USERNAME"] + ":" + environ["MONGO_PASSWORD"] + "@" + environ["MONGO_ENDPOINT"]
dbclient = MongoClient(CONN_URL)
db = dbclient['discord']

def calculateGeographicMidpoint(coords):
    latitudes = np.radians([c[0] for c in coords])
    longitudes = np.radians([c[1] for c in coords])
    
    x = np.cos(latitudes) * np.cos(longitudes)
    y = np.cos(latitudes) * np.sin(longitudes)
    z = np.sin(latitudes)
    
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    z_mean = np.mean(z)
    
    central_longitude = np.arctan2(y_mean, x_mean)
    hyp = np.sqrt(x_mean**2 + y_mean**2)
    central_latitude = np.arctan2(z_mean, hyp)
    
    return np.degrees(central_latitude), np.degrees(central_longitude)

def find_restaurant(api_key, location, radius=1000):
    gmaps = googlemaps.Client(key=api_key)
    places = gmaps.places_nearby(
        location=location,
        radius=radius,
        type='restaurant'
    )
    
    if places.get("results"):
        best_place = sorted(places["results"], key=lambda x: x.get("rating", 0), reverse=True)[0]
        return best_place
    return None

def main():
    parser = argparse.ArgumentParser(description="Find a central restaurant for given locations.")
    parser.add_argument("coords", nargs='+', help="List of latitude,longitude pairs", type=str)
    args = parser.parse_args()
    
    coords = [tuple(map(float, coord.split(','))) for coord in args.coords]
    midpoint = calculateGeographicMidpoint(coords)
    
    
    if not GOOGLE_API_KEY:
        print("Google Maps API key not found. Set GOOGLE_MAPS_API_KEY as an environment variable.")
        return
    
    restaurant = find_restaurant(GOOGLE_API_KEY, midpoint)
    
    if restaurant:
        print(f"Best Restaurant: {restaurant['name']}")
        print(f"Address: {restaurant['vicinity']}")
        print(f"Rating: {restaurant.get('rating', 'N/A')}")
    else:
        print("No restaurants found near the midpoint.")
    
if __name__ == "__main__":
    main()
