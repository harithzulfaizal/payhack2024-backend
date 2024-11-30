from datetime import datetime
import googlemaps

API_KEY = "AIzaSyDmaY90xxqMqQyHKq8c4AJNB3R5b6YDpIU"

def get_nearby_places(address, keyword):
    gmaps = googlemaps.Client(key=API_KEY)
    geocode_result = gmaps.geocode(address)
    # Extract latitude and longitude
    if geocode_result:
        location = geocode_result[0]["geometry"]["location"]
        lat = location["lat"]
        lng = location["lng"]

        # Perform a nearby search
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=5000,
            keyword=keyword 
        )
        print(places_result['results'][-1]['user_ratings_total'])
        # Print the names of the places found
        return places_result["results"]
    else:
        print("Address not found")

get_nearby_places("8 Jalan Kenari Subang Jaya", " restaurants budget-friendly")
