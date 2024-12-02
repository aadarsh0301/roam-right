import requests
from datetime import datetime
from groq import Groq
from weather import get_coordinates, get_weather, transform_places_to_visit, transform_places
from directions_tom_tom import get_directions, calculate_daily_travel_times

api_key = "" #openroute
API_KEY = ""

def initialize_groq_client():
    try:
        return Groq(api_key=API_KEY)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Groq client: {e}")

def get_top_100_places(groq_client, location):
    prompt = f"List the top 100 places to visit around {location}. Include landmarks, attractions, and popular destinations."
    try:
        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        response_text = completion.choices[0].message.content
        return [place.strip() for place in response_text.split("\n") if place.strip()]
    except Exception as e:
        raise RuntimeError(f"Error fetching top 100 places: {e}")

def get_daily_recommendations(groq_client, location, weather_details, available_places):
    used_places = set()
    daily_recommendations = {}

    for day in weather_details:
        date = day['date']
        max_temp = day['max_temp']
        min_temp = day['min_temp']

        prompt = (
            f"Based on the weather for {date} in {location}:\n"
            f"- Max Temp: {max_temp}°C\n"
            f"- Min Temp: {min_temp}°C\n"
            f"From the following list, recommend 10 places to visit today, avoiding places already recommended:\n"
            f"{', '.join(available_places)}"
        )
        try:
            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=1,
                max_tokens=512,
                top_p=1,
                stream=False
            )
            response_text = completion.choices[0].message.content
            recommended_places = [
                place.strip()
                for place in response_text.split("\n")
                if place.strip() and place not in used_places
            ][:10]
            used_places.update(recommended_places)
            available_places = [place for place in available_places if place not in used_places]
            daily_recommendations[date] = recommended_places
        except Exception as e:
            print(f"Error fetching daily recommendations for {date}: {e}")
            daily_recommendations[date] = ["Error fetching recommendations"]

    return daily_recommendations

def get_weather_and_places(location, start_date, duration):
    groq_client = initialize_groq_client()
    lat, lon = get_coordinates(location)
    if lat is None or lon is None:
        return f"Failed to get coordinates for {location}."

    available_places = get_top_100_places(groq_client, location)

    weather_details = get_weather(lat, lon, start_date, duration)
    if not weather_details:
        return f"Could not retrieve weather data for {location}."

    places_to_visit = get_daily_recommendations(groq_client, location, weather_details, available_places)

    result = {
        "weather_summary": "\n".join(
            [f"Date: {day['date']}, Max Temp: {day['max_temp']}°C, Min Temp: {day['min_temp']}°C"
             for day in weather_details]
        ),
        "places_to_visit": places_to_visit
    }

    return result



location = "Seattle"
start_date = datetime.strptime("2024-12-02", "%Y-%m-%d")
print(start_date)
duration = 4

result = get_weather_and_places(location, start_date, duration)

#print(f"RAW OUPUT:{result["places_to_visit"]}")

# print("Weather Summary:")
# print(result["weather_summary"])

# print("\nPlaces to Visit:")
# for date, places in result["places_to_visit"].items():
#     print(f"Date: {date}")
#     for place in places:
#         print(f"- {place}")


main_res = transform_places(transform_places_to_visit(result))
print(main_res)


origin_lat, origin_lon = get_coordinates(location)

travel_times = calculate_daily_travel_times(main_res, origin_lat, origin_lon, api_key)
print(travel_times)

prompt = f"Create a detailed travel itinerary for a {location}. I "