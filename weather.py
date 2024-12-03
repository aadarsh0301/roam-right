import requests
from datetime import timedelta

def get_coordinates(location, max_retries=3, delay=1):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    headers = {
        "User-Agent": "TravelItineraryApp/1.0"
    }
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            return None, None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    print("Max retries reached. Unable to get coordinates.")
    return None, None


def get_weather(lat, lon, start_date, duration):
    print(lat,lon,start_date)
    weather_data = []
    base_url = "https://api.open-meteo.com/v1/forecast"
    for day in range(duration):
        date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
        print(date, lat, lon)
        url = f"{base_url}?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&start_date={date}&end_date={date}&timezone=auto"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if 'daily' in data and data['daily']['temperature_2m_max']:
                weather_data.append({
                    "date": date,
                    "max_temp": data['daily']['temperature_2m_max'][0],
                    "min_temp": data['daily']['temperature_2m_min'][0]
                })
        except requests.exceptions.RequestException as e:
            print(f"Failed to get weather data for {date}: {str(e)}")
    return weather_data

def transform_places_to_visit(result):
    transformed_places = {
        date: set(places)
        for date, places in result["places_to_visit"].items()
    }
    return transformed_places

def transform_places(raw_places):
    transformed_places = {}
    for date, places in raw_places.items():
        cleaned_set = set()
        for place in places:
            if "**" in place:
                start = place.find("**") + 2
                end = place.find("**", start)
                place_name = place[start:end].strip()
                cleaned_set.add(place_name)
        transformed_places[date] = cleaned_set

    return transformed_places
