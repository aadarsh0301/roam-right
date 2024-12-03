from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from datetime import datetime
import json
import regex
from weather import get_coordinates, get_weather, transform_places_to_visit, transform_places
from directions_tom_tom import calculate_daily_travel_times

app = Flask(__name__)
CORS(app)
OPEN_ROUTE_KEY = ""
TOM_TOM_KEY=""
GROQ_API_KEY=""
# Initialize Groq API client
client = Groq(api_key=GROQ_API_KEY)  # Replace with your GroqCloud API key
trip_details_json = {
    "destination": "",
    "budget": "",
    "startDate": "",
    "endDate": "",
    "response": ""
}
@app.route('/intialize', methods=['POST'])
def initialize():
    for key in trip_details_json.keys():
        trip_details_json[key]=""
    return jsonify({
        "reply": "Initialized"
    })
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
    lat, lon = get_coordinates(location)
    if lat is None or lon is None:
        return f"Failed to get coordinates for {location}."

    available_places = get_top_100_places(client, location)

    weather_details = get_weather(lat, lon, start_date, duration)
    if not weather_details:
        return f"Could not retrieve weather data for {location}."

    places_to_visit = get_daily_recommendations(client, location, weather_details, available_places)

    result = {
        "weather_summary": "\n".join(
            [f"Date: {day['date']}, Max Temp: {day['max_temp']}°C, Min Temp: {day['min_temp']}°C"
             for day in weather_details]
        ),
        "places_to_visit": places_to_visit
    }

    return result
def addWeatherAndDirections(trip_details):
    start_date = datetime.strptime(trip_details['startDate'], "%Y-%m-%d")
    end_date = datetime.strptime(trip_details['endDate'], "%Y-%m-%d")
    duration = (end_date - start_date).days + 1
    result = get_weather_and_places(trip_details['destination'], start_date, duration)
    main_res = transform_places(transform_places_to_visit(result))
    print(main_res)
    origin_lat, origin_lon = get_coordinates(trip_details['destination'])

    travel_times = calculate_daily_travel_times(main_res, origin_lat, origin_lon, TOM_TOM_KEY)
    return main_res,travel_times

@app.route('/chat', methods=['POST'])
def chat_interface():
    extramessage = "Please format the response with appropriate HTML tags (e.g., <p>, <ul>, <li>, <br>) for each line or paragraph to ensure proper display in the React app. Ensure that the content is well-structured for readability and presentation."
    includes = "Include travel times and provide direction. give hotel recommendations as well as food recommendations, include links wherever possible"
    user_message = request.json.get('message')
    requestType = request.json.get('type')
    session_data = request.json.get('session_data', {})
    print("\nuser_message " + str(user_message))
    print("\nrequestType " + str(requestType))
    print("\nsession_data " + str(session_data))
    type = ""
    try:
        print("\nTRIP JSON " + str(trip_details_json))
        if has_null_value(trip_details_json):
            prompt = validate_trip_details(user_message)
            type = "chat"
        else:
            if requestType == "itinerary":
                main_res, travelTimes = addWeatherAndDirections(trip_details_json)
                prompt = "Generate detailed itinerary along with time using the below details "+ str(trip_details_json) + str(extramessage)+ str(includes) + str(travelTimes) + str(main_res)
                type = "itinerary_reply"
            elif requestType == "map":
                prompt = promptForMap(user_message)
                type="map_reply"
                print("Asking for map")
            else:
                prompt=user_message+extramessage
                type="chat"

        if type != "Done":
            groq_response = client.chat.completions.create(
                model="llama3-70b-8192",  # Specify your Groq model
                messages=session_data.get('messages', []) + [
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                top_p=1.0,
            )

            # Log the raw response
            print("GroqCloud response:", groq_response)

            # Extract the bot's response content
            response_content = ""
            for choice in groq_response.choices:
                response_content += choice.message.content  # Access the content

            # Append the bot's reply to the session data
            session_data['messages'] = session_data.get('messages', []) + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response_content},
            ]

            if has_null_value(trip_details_json):
                jsonObj = (extract_json_object(response_content))
                if jsonObj:
                    # Map extracted JSON to the predefined structure
                    for key in trip_details_json:
                        if key in jsonObj:
                            trip_details_json[key] = jsonObj[key]

                    if 'response' in jsonObj:
                        reply = jsonObj['response']  # Adjust this based on the actual structure of your JSON object
                    else:
                        reply = ""
                else:
                    reply = ""
            else:
                reply = response_content

            if reply == "Thank you! I have all the details to start planning your trip.":
                type = "details_received"
        else:
            reply = "Enjoy"
        # Return the formatted HTML response
        return jsonify({
            "reply": reply,
            "updated_session_data": session_data,
            "replyType": type
        })

    except Exception as e:
        print("Error processing request:", e)  # Log the error
        return jsonify({
            "reply": "An error occurred while processing your request. Please try again.",
            "updated_session_data": session_data,
            "type": "chat"
        })


def validate_trip_details(user_response):
    """
    Validate if the user's response contains all required trip details: travel dates, destination(s), and budget.
    """
    prompt = f"""
    The user needs to provide three essential details for planning a trip:
    1. Travel dates
    2. Destination(s)
    3. Budget

    Here is the user's response:
    "{user_response}"

    Check if all three details are included in the response. Add the details in a JSON object of this format and return only this:
    {{
    "destination": <destination(s)>,
    "budget": <budget>,
    "startDate": <start date> in format 'yyyy-mm-dd',
    "endDate": <end date> in format 'yyyy-mm-dd',
    "response": <response>
    }}
    If any detail is missing, generate a specific question to request that detail from the user and add it in JSON object in rsponse field. 
    - If travel dates are missing, ask: "Could you please specify your travel dates?"
    - If destination(s) are missing, ask: "Could you share the destination(s) you'd like to visit?"
    - If budget is missing, ask: "What is your budget for this trip?"

    If all details are present, confirm with: "Thank you! I have all the details to start planning your trip." Respond with only JSON no other comments    
    """
    return prompt

def promptForMap(user_response):
    prompt = f"""
    Based on the following itinerary:
    "{user_response}"
    
    Please generate a JSON array of directions in the format below:
    
    [
        {{
            "from_name": "Point A",
            "from_lat": 21.23,
            "from_lon": 21.234,
            "to_name": "Point B",
            "to_lat": 23.23,
            "to_lon": 23.234
        }},
        {{
            "from_name": "Point C",
            "from_lat": 29.23,
            "from_lon": 29.234,
            "to_name": "Point D",
            "to_lat": 25.23,
            "to_lon": 27.234
        }}
    ]
    
    Ensure the response is in valid JSON format with no additional comments or explanations.
    """
    return prompt

def extract_json_object(string):
    # Use regex to find the first JSON object
    match = regex.search(r'\{(?:[^{}]|(?R))*\}', string, regex.DOTALL)

    if match:
        json_str = match.group(0)  # Extract the matched JSON object string

        try:
            # Try to parse the extracted string as JSON to verify it's valid
            parsed_json = json.loads(json_str)
            return parsed_json  # Return the parsed JSON object
        except json.JSONDecodeError:
            return None  # If it's not a valid JSON object, return None
    return None  # If no JSON object is found, return None

def has_null_value(json_obj):
    return any(value is "" for value in json_obj.values())

if __name__ == '__main__':
    app.run(debug=True)