from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Hugging Face API endpoint and token
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
HUGGINGFACE_API_TOKEN = "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"

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

@app.route('/chat', methods=['POST'])
def chat_interface():
    user_message = request.json.get('message')
    session_data = request.json.get('session_data', {})

    # Retrieve current session data
    trip_data = session_data.get('trip_data', {})
    state = session_data.get('state', 'start')

    response = {"state": state, "trip_data": trip_data, "reply": ""}

    if state == "start":
        response["reply"] = "I can help you plan your travel itinerary. Could you tell me the place you'd like to visit?"
        response["state"] = "awaiting_place"
    elif state == "awaiting_place":
        trip_data["place"] = user_message.strip()
        response["reply"] = "Great! What's your travel date? (e.g., YYYY-MM-DD)"
        response["state"] = "awaiting_date"
    elif state == "awaiting_date":
        trip_data["date"] = user_message.strip()
        response["reply"] = "Got it! What's your budget for the trip?"
        response["state"] = "awaiting_budget"
    elif state == "awaiting_budget":
        try:
            trip_data["budget"] = int(user_message.strip())
            response["reply"] = "Awesome! Do you have any specific interests? (e.g., nature, adventure, history)"
            response["state"] = "awaiting_interests"
        except ValueError:
            response["reply"] = "Please enter a valid budget amount."
    elif state == "awaiting_interests":
        trip_data["interests"] = user_message.strip()
        response["reply"] = "Thanks! Let me generate your itinerary now..."
        response["state"] = "processing"
        prompt = (
            f"Create a detailed travel itinerary for a trip to {trip_data['place']} on {trip_data['date']} "
            f"with a budget of ${trip_data['budget']}. The traveler is interested in {trip_data['interests']}. "
            f"Include weather details, top attractions, and activity suggestions."
        )
        hf_response = requests.post(
            HUGGINGFACE_API_URL,
            headers=headers,
            json={"inputs": prompt}
        )
        if hf_response.status_code == 200:
            try:
                # Ensure the response is in the expected format (list of responses)
                response_data = hf_response.json()

                # Access the first element of the list
                itinerary = response_data[0].get("generated_text", "Sorry, no response.")

                response["reply"] = f"Here's your itinerary:\n{itinerary}"
                response["state"] = "done"
            except (IndexError, KeyError) as e:
                response["reply"] = "Error processing the generated itinerary. Please try again later."
                response["state"] = "start"
        else:
            response["reply"] = "Error generating itinerary. Please try again later."
            response["state"] = "start"
    else:
        response["reply"] = "I'm here to help! Let me know how I can assist."
        response["state"] = "start"

    response["trip_data"] = trip_data
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
