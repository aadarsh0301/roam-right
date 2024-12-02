from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import json
import regex

app = Flask(__name__)
CORS(app) 

# Initialize Groq API client
client = Groq(api_key="")  # Replace with your GroqCloud API key
trip_details_json = {
    "destination": "",
    "budget": "",
    "startDate": "",
    "endDate": "",
    "response": ""
}

@app.route('/chat', methods=['POST'])
def chat_interface():
    extramessage = "Please format the response with appropriate HTML tags (e.g., <p>, <ul>, <li>, <br>) for each line or paragraph to ensure proper display in the React app. Ensure that the content is well-structured for readability and presentation."
    user_message = request.json.get('message')
    session_data = request.json.get('session_data', {})
    
    try:
        print(trip_details_json)
        if has_null_value(trip_details_json):
            prompt = validate_trip_details(user_message)
        else:
            # prompt needs to be set
            prompt = ""
        
        groq_response = client.chat.completions.create(
            model="llama3-70b-8192",  # Specify your Groq model
            messages=session_data.get('messages', []) + [
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            top_p=1.0
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
        jsonObj = (extract_json_object(response_content))
        print(jsonObj)
        if jsonObj:
            # Map extracted JSON to the predefined structure
            for key in trip_details_json:
                if key in jsonObj:
                    trip_details_json[key] = jsonObj[key]

        if jsonObj and 'response' in jsonObj:
            reply = jsonObj['response']  # Adjust this based on the actual structure of your JSON object
        else:
            reply = response_content 

        # Return the formatted HTML response
        return jsonify({
            "reply": reply,
            "session_data": session_data
        })
        
    except Exception as e:
        print("Error processing request:", e)  # Log the error
        return jsonify({
            "reply": "An error occurred while processing your request. Please try again.",
            "session_data": session_data
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
    "startDate": <start date>,
    "endDate": <end date>,
    "response": <response>
    }}
    If any detail is missing, generate a specific question to request that detail from the user and add it in JSON object in rsponse field. 
    - If travel dates are missing, ask: "Could you please specify your travel dates?"
    - If destination(s) are missing, ask: "Could you share the destination(s) you'd like to visit?"
    - If budget is missing, ask: "What is your budget for this trip?"

    If all details are present, confirm with: "Thank you! I have all the details to start planning your trip." Respond with only JSON no other comments    
    """
    return prompt

def extract_json_object(string):
    # Use regex to find the first JSON object
    match = regex.search(r'\{(?:[^{}]|(?R))*\}', string, regex.DOTALL)

    if match:
        print("in match")
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
