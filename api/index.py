import os  # Standard library to read environment variables
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Vercel will automatically inject the key into 'os.environ'
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def get_deepseek_translation(text, region):
    # If the key is missing, this will help you debug
    if not DEEPSEEK_API_KEY:
        return "Error: API Key not found in Environment Variables."

    system_prompt = (
        f"You are a professional IT translator. Translate the input to Chinese "
        f"specifically for the {region} region. "
        "Use local IT terminology (e.g., 'Software' -> '軟體' for TW, '软件' for CN). "
        "For Hong Kong, use a professional hybrid style if appropriate."
    )
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.3
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    # Simple error handling for the API response
    if response.status_code != 200:
        return f"DeepSeek API Error: {response.text}"
        
    return response.json()['choices'][0]['message']['content']

# ... (Keep the rest of your routes the same)