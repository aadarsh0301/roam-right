import requests
from weather import get_coordinates

def get_directions(origin_lat, origin_lon, dest_lat, dest_lon, api_key):
    # Define TomTom Routing API endpoint
    base_url = "https://api.tomtom.com/routing/1/calculateRoute"
    url = f"{base_url}/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json"

    # Define query parameters
    params = {
        "routeType": "fastest",
        "traffic": "true",
        "travelMode": "car",
        "key": api_key
    }

    try:
        # Make GET request to TomTom API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse response JSON
        directions = response.json()
        if 'routes' in directions and directions['routes']:
            route = directions['routes'][0]['summary']
            distance_km = route.get('lengthInMeters', 0) / 1000  # Convert meters to kilometers
            duration_min = route.get('travelTimeInSeconds', 0) / 60  # Convert seconds to minutes
            return distance_km, duration_min
        else:
            print(f"No routes found between coordinates: {origin_lat}, {origin_lon} and {dest_lat}, {dest_lon}.")
            return None, None
    except requests.exceptions.RequestException as e:
        #print(f"Error fetching directions: {e}")
        return None, None
    except KeyError as e:
        print(f"Unexpected response format: {e}")
        return None, None

def calculate_daily_travel_times(input_places, origin_lat, origin_lon, api_key):
    def get_coordinates_for_place(place_name):
        """Mock implementation for geocoding; replace with real service."""
        return 47.6097, -122.3331

    travel_details = {}

    for date, places in input_places.items():
        places_list = list(places)
        travel_details[date] = {}

        for i in range(len(places_list)):
            for j in range(i + 1, len(places_list)):
                place_a = places_list[i]
                place_b = places_list[j]
                lat_a, lon_a = get_coordinates(place_a)
                lat_b, lon_b = get_coordinates(place_b)
                distance, duration = get_directions(lat_a, lon_a, lat_b, lon_b, api_key)
                travel_details[date][(place_a, place_b)] = {
                    "distance_km": distance,
                    "duration_min": duration
                }

    return travel_details