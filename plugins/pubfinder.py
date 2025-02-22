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
user_collection = db['users']


#geographic midpoint between users - at the moment - all users in database
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

def find_restaurant(location, radius=1000):
    gmaps = googlemaps.Client(key = GOOGLE_API_KEY)
    places = gmaps.places_nearby(
        location=location,
        radius=radius,
        type='restaurant'
    )
    
    if places.get("results"):
        best_place = sorted(places["results"], key=lambda x: x.get("rating", 0), reverse=True)[0]
        return best_place
    else:
        return find_restaurant(location, radius = radius + 1000)
    #return None

def chooseRestaurant():
    reply = ""
    if not GOOGLE_API_KEY:
        print("[ERROR]Google Maps API key not found. Set GOOGLE_MAPS_API_KEY as an environment variable.")
        return
    coords = []
    users = user_collection.find({})
    if users != None:
        for user in users:
            if user['riotid'] == 'roLab' or user['riotid'] == 'SMIRNOFF' or user['riotid'] == 'Wklej' or user['riotid'] == 'FatherInLaw':
                coords.append(user['coordinates'])
    if len(coords) > 1:
        midpoint = calculateGeographicMidpoint(coords)
        restaurant = find_restaurant(midpoint)
    else:
        return None
    
    if restaurant:
        return restaurant
        #reply = reply + f"Best Restaurant: {restaurant['name']}\n"
        #reply = reply + f"Address: {restaurant['vicinity']}\n"
        #reply = reply + f"Rating: {restaurant.get('rating', 'N/A')}\n"
    #else:
        #reply = reply + "No restaurants found near the midpoint."

    return None
    
   