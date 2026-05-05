import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

TARGET_VARIANT_RULES = {
    "en_us": "Translate into natural English. Keep the meaning accurate and clear.",
    "zh_cn": (
        "Translate into Mainland China Chinese. Use Simplified Chinese characters, "
        "Mainland vocabulary, and Mainland sentence patterns."
    ),
    "zh_tw": (
        "Translate into Taiwan Chinese. Use Traditional Chinese characters, "
        "Taiwan vocabulary, and Taiwan sentence patterns."
    ),
    "zh_hk_written": (
        "Translate into Hong Kong Written Chinese. Use Traditional Chinese characters, "
        "Hong Kong vocabulary, and written register suitable for public writing."
    ),
    "zh_hk_spoken": (
        "Translate into Hong Kong spoken Cantonese. Use colloquial Cantonese in "
        "written form with Traditional Chinese characters."
    ),
}

STYLE_RULES = {
    "natural": "Keep the tone natural and neutral.",
    "formal": "Use a formal and professional tone.",
    "friendly": "Use a warm and friendly tone.",
    "social": (
        "Use a social media style. Emoji are allowed if they fit naturally, "
        "but do not overuse them."
    ),
}


def build_system_prompt(target_variant, tone_style):
    variant_rule = TARGET_VARIANT_RULES.get(target_variant, TARGET_VARIANT_RULES["zh_cn"])
    style_rule = STYLE_RULES.get(tone_style, STYLE_RULES["natural"])
    return (
        "You are a high-accuracy bilingual translator for English and Chinese variants. "
        "Preserve meaning, context, and key terms. "
        f"{variant_rule} {style_rule} "
        "Output only the translated text without explanations."
    )


def call_deepseek(text, source_language, target_variant, tone_style):
    if not DEEPSEEK_API_KEY:
        return None, "Server missing DEEPSEEK_API_KEY."

    system_prompt = build_system_prompt(target_variant, tone_style)
    source_hint = (
        "auto-detect source language" if source_language == "auto" else f"source language is {source_language}"
    )
    user_prompt = f"Please translate this text ({source_hint}):\n\n{text}"

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.25,
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=45)
    except requests.RequestException as exc:
        return None, f"Network error when calling DeepSeek: {exc}"

    if response.status_code != 200:
        return None, f"DeepSeek API error ({response.status_code}): {response.text}"

    try:
        translated = response.json()["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, ValueError):
        return None, "DeepSeek returned unexpected response format."

    return translated, None


@app.route("/api/translate", methods=["POST"])
def translate():
    payload = request.get_json(silent=True) or {}

    text = (payload.get("text") or "").strip()
    source_language = payload.get("source_language", "auto")
    target_variant = payload.get("target_variant", "zh_cn")
    tone_style = payload.get("tone_style", "natural")

    if not text:
        return jsonify({"error": "text is required."}), 400

    translated, error = call_deepseek(text, source_language, target_variant, tone_style)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"translated": translated})


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "translator-api"})