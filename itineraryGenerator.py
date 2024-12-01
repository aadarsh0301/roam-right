from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# Initialize Groq API client
client = Groq(api_key="")  # Replace with your GroqCloud API key

@app.route('/chat', methods=['POST'])
def chat_interface():
    extramessage = "Please format the response with appropriate HTML tags (e.g., <p>, <ul>, <li>, <br>) for each line or paragraph to ensure proper display in the React app. Ensure that the content is well-structured for readability and presentation."
    user_message = request.json.get('message')
    session_data = request.json.get('session_data', {})

    try:
        # Add the user message to the dynamic context
        groq_response = client.chat.completions.create(
            model="llama3-70b-8192",  # Specify your Groq model
            messages=session_data.get('messages', []) + [
                {"role": "user", "content": user_message + extramessage}
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

        # Return the formatted HTML response
        return jsonify({
            "reply": response_content,
            "session_data": session_data
        })

    except Exception as e:
        print("Error processing request:", e)  # Log the error
        return jsonify({
            "reply": "An error occurred while processing your request. Please try again.",
            "session_data": session_data
        })

if __name__ == '__main__':
    app.run(debug=True)
