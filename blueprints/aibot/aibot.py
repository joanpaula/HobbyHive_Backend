from flask import Blueprint, request, jsonify
from google import genai
from google.genai import types
import json
import globals

aibot_bp = Blueprint("aibot", __name__)

# client using gemini api key
client = genai.Client(api_key=globals.gemini_API_key)

@aibot_bp.route('/api/v1.0/suggest-hobbies', methods=['POST'])
def suggest_hobbies():
    
    # user input from mobile frontend
    user_data = request.json
    interest = user_data.get('interest', 'general')

    # gemini prompt for hobby suggestions based on user input
    prompt = f"The user is interested in '{interest}'. Suggest 3 specific but common hobbies. Return as a JSON object with a 'hobbies' key."

    # model for the prompt
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # AI string to python list
        return jsonify(json.loads(response.text))

    except Exception as e:
        print(f"AI Error: {e}")
        # default response
        return jsonify({"hobbies": ["Hiking", "Coding", "Gardening"]}), 200