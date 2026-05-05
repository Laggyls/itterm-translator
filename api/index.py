from flask import Flask, request, jsonify
from opencc import OpenCC
from deep_translator import GoogleTranslator
from flask_cors import CORS

# Vercel looks for the variable named 'app'
app = Flask(__name__)
CORS(app)

def localize_text(text, region):
    if region == 'TW':
        return OpenCC('s2twp').convert(text)
    elif region == 'HK':
        return OpenCC('s2hk').convert(text)
    return text

@app.route('/')
def home():
    return "IT Translator API is running! Use /api/translate for POST requests."

@app.route('/api/translate', methods=['POST'])
def translate():
    # ... your existing translation code ...
    try:
        data = request.json
        text = data.get('text', '')
        region = data.get('region', 'CN')
        
        base = GoogleTranslator(source='auto', target='zh-CN').translate(text)
        result = localize_text(base, region)
        
        return jsonify({"translated": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This is required for local testing, but Vercel uses the 'app' variable above
if __name__ == "__main__":
    app.run()