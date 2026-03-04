from flask import Blueprint, jsonify, make_response, request
import globals
import googlemaps

places_bp = Blueprint("places", __name__)

# access to user db (for fetching data)
users = globals.db.users

# google maps api key and client
GOOGLE_API_KEY = globals.google_API_key
gmaps = googlemaps.Client(key = GOOGLE_API_KEY)

# get nearby places based on user location (mobiel front end)
@places_bp.route('/api/v1.0/search/nearby_places', methods=['POST'])
def get_nearby_places():
    
    data = request.json

    lat = data["lat"]
    lng = data["lng"]
    radius = data["radius"]
    place_type = data["keyword"]
    
    places_result = gmaps.places_nearby(
        location = (lat, lng),
        radius = radius,
        open_now = False,
        keyword=place_type
    )
    
    results = []
    for place in places_result.get("results", []):
        results.append({
            "place_id": place["place_id"],
            "name": place["name"],
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"],
            "vicinity": place.get("vicinity", "")
        })
    
    return make_response(jsonify(results), 200)
  
# get details of nearby places 
@places_bp.route('/api/v1.0/search/nearby_places/<string:place_id>', methods=['GET'])
def get_place_details(place_id):
    my_fields = [
            'name', 
            'international_phone_number', 
            'type',
            'formatted_address',
            'opening_hours',
            'rating',
            'review',
            'url',
            'website',
            'photo',
            'editorial_summary',
            'geometry/location'
        ]
        
    # make request for details
    place_details = gmaps.place(
        place_id = place_id, 
        fields = my_fields
    )
    
    return make_response(jsonify(place_details), 200)
