from flask import Flask, request, jsonify
from opencc import OpenCC
from deep_translator import GoogleTranslator
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows your GitHub website to talk to this API

def localize_text(text, region):
    if region == 'TW':
        return OpenCC('s2twp').convert(text) # Simplified to TW with phrases
    elif region == 'HK':
        return OpenCC('s2hk').convert(text)  # Simplified to HK characters
    return text # Mainland Default

@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    region = data.get('region', 'CN')
    
    # 1. Translate to Simplified Chinese
    base = GoogleTranslator(source='auto', target='zh-CN').translate(text)
    
    # 2. Localize based on Skopos
    result = localize_text(base, region)
    
    return jsonify({"translated": result})

# Vercel needs the app object
app.debug = True