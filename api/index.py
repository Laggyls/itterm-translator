import os
import re
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
FLOPTROPICA_EMOJI_RE = re.compile(r"[⭐🌟✨💅💋🥑🙄👀💖💘🔥👑🎀🤍🫦💫🤭💃🕺😮‍💨💅🏽]")

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
    "natural": (
        "Use a neutral everyday tone suitable for general communication. "
        "Keep wording clear, direct, and culturally natural without sounding too casual or too stiff."
    ),
    "formal": (
        "Use a formal, authoritative register suitable for official notices, workplace announcements, "
        "policy statements, legal/administrative communication, or academic writing. "
        "Prioritize precision, structure, and professionalism over casual expression."
    ),
    "friendly": (
        "Use a warm and approachable conversational tone intended to soften phrasing. "
        "Suitable for customer support, peer-to-peer chat, community replies, and polite requests. "
        "Keep it respectful, empathetic, and easy to read."
    ),
    "social": (
        "Use a social-media-native style for public posts/comments. "
        "Suitable for short-form platforms and community discussions. "
        "Allow light emoji and internet phrasing where natural, but keep readability and avoid spammy emoji."
    ),
    "floptropica": (
        "Use a campy and dramatic internet style (FLOPTROPICA vibe): playful sass, "
        "theatrical emphasis, and expressive emoji when natural. "
        "Best for entertainment captions, meme posts, and dramatic reactions, not for official content. "
        "Emoji style should frequently include symbols like stars, sparkles, nails, lips, avocado, side-eye, hearts, flames, and glam vibes "
        "(for example: ⭐, 🌟, ✨, 💅, 💋, 🥑, 🙄, 👀, 💖, 💘, 🔥, 👑, 🎀) when it fits the sentence naturally. "
        "Allow bizarre but coherent creative additions for context and humor, as long as core meaning and facts remain accurate."
    ),
    "linkedin": (
        "Use a polished LinkedIn professional voice suitable for portfolio and personal branding. "
        "Expand simple statements into high-impact, outcome-oriented phrasing that highlights explicit skills, ownership, and value. "
        "Format with one sentence per paragraph (line break between sentences), concise but professional."
    ),
}


SOCIAL_STYLE_BY_VARIANT = {
    "en_us": (
        "Write like a native English social media user on platforms like Threads/X: "
        "short, expressive, natural, with light emoji usage."
    ),
    "zh_cn": (
        "Write like a native Mainland China social media user (Bilibili/Weibo/Xiaohongshu style): "
        "internet-native wording, natural slang where appropriate, and fitting emoji usage when applicable."
    ),
    "zh_tw": (
        "Write like a native Taiwan social media user (Threads/Dcard/PTT style): "
        "Taiwan online expressions, natural cadence, and fitting emoji usage when applicable."
    ),
    "zh_hk_written": (
        "Write like a native Hong Kong online writer using written Chinese (Threads/local forums style): "
        "HK-preferred wording, concise flow, and fitting emoji usage, perfect for social media post that target Hong Kong audience."
    ),
    "zh_hk_spoken": (
        "Write like a native Hong Kong netizen in Cantonese (LIHKG/Threads style): "
        "authentic colloquial Cantonese wording and particles, with natural emoji usage when applicable."
    ),
}


def wants_chinese(target_variant):
    return target_variant.startswith("zh_")


def contains_cjk(text):
    return bool(re.search(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]", text))


def split_sentences(text):
    parts = re.split(r"(?<=[.!?。！？])\s*", text.strip())
    return [part for part in parts if part]


def has_floptropica_sentence_emojis(text):
    sentences = split_sentences(text)
    if not sentences:
        return False
    # Require emoji in every sentence plus a few sentences with 2 emojis for stronger vibe.
    sentences_with_emoji = sum(1 for s in sentences if FLOPTROPICA_EMOJI_RE.search(s))
    if sentences_with_emoji < len(sentences):
        return False
    sentences_with_two = sum(1 for s in sentences if len(FLOPTROPICA_EMOJI_RE.findall(s)) >= 2)
    return sentences_with_two >= max(1, len(sentences) // 3)


def has_floptropica_slang(text):
    hits = re.findall(r"\b(slay+y*|poosay|pookie|queen|diva)\b", text, flags=re.IGNORECASE)
    sentence_count = len(split_sentences(text))
    required = 2 if sentence_count >= 4 else 1
    return len(hits) >= required


def has_floptropica_caps_english(text, target_variant):
    if target_variant != "en_us":
        return True
    return bool(re.search(r"\b[A-Z]{4,}\b", text))


def has_linkedin_paragraph_style(text):
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return True
    paragraphs = [p for p in text.split("\n") if p.strip()]
    return len(paragraphs) >= len(sentences) - 1


def contains_emoji(text):
    return bool(re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", text))


def has_required_style_markers(text, tone_style, target_variant):
    if tone_style == "floptropica":
        return (
            has_floptropica_sentence_emojis(text)
            and has_floptropica_slang(text)
            and has_floptropica_caps_english(text, target_variant)
        )
    if tone_style == "linkedin":
        return has_linkedin_paragraph_style(text) and not contains_emoji(text)
    return True


def build_system_prompt(target_variant, tone_style):
    variant_rule = TARGET_VARIANT_RULES.get(target_variant, TARGET_VARIANT_RULES["zh_cn"])
    style_rule = STYLE_RULES.get(tone_style, STYLE_RULES["natural"])
    if tone_style == "social":
        style_rule = SOCIAL_STYLE_BY_VARIANT.get(target_variant, style_rule)
    elif tone_style == "floptropica":
        style_rule = (
            "Write in a FLOPTROPICA-style internet voice adapted to the selected target variant. "
            "Prioritize full FLOPTROPICA vibe over strict grammar and spelling perfection. "
            "You may creatively adapt wording for humor and personality (not strict one-to-one translation), "
            "but keep the core meaning and key facts intact. "
            "Reference iconic FLOPTROPICA culture elements where relevant and natural, such as Jiafei, CupcakKe, or DaBoyz. "
            "Do not force references if the input context is serious or unrelated. "
            "Distribute emoji across sentences: frequently add 1-2 fitting emojis near sentence endings, "
            "instead of placing all emojis only at the very end. "
            "Use signature slang like SLAYYYY, Poosay, pookie, Queen, diva naturally in the output. "
            "If target output is English, include expressive FULL-CAPS stress words (for example: SLAYYYY, ICONIC, MAJOR, LITERALLY). "
            "Be more bizarre, vivid, and context-rich than standard translation while preserving intent. "
            "For Chinese outputs, ensure native Chinese internet flavor by target variant: "
            "Mainland should feel like Bilibili/Weibo meme speech, Taiwan should feel like Dcard/PTT/Threads wording, "
            "Hong Kong written should reflect HK online written style, and Hong Kong spoken should use authentic Cantonese netizen tone."
        )
    elif tone_style == "linkedin":
        style_rule = (
            "Rewrite in LinkedIn-ready style for portfolio usage. "
            "Transform simple lines into professional, results-focused statements that imply capability and initiative. "
            "Use one sentence per paragraph with explicit skill language and polished tone. "
            "Do not use emojis, emoticons, or internet slang."
        )

    return (
        "You are a high-accuracy bilingual translator for English and Chinese variants. "
        "Preserve meaning, context, and key terms. "
        "The user's selected target variant is mandatory and must be followed strictly. "
        "Never keep the output in the source language unless the target variant is that language. "
        f"{variant_rule} {style_rule} "
        "Do not invent new factual claims. Output only the translated text without explanations."
    )


def call_deepseek(text, source_language, target_variant, tone_style):
    if not DEEPSEEK_API_KEY:
        return None, "Server missing DEEPSEEK_API_KEY."

    system_prompt = build_system_prompt(target_variant, tone_style)
    source_hint = (
        "Auto-detect the source language first."
        if source_language == "auto"
        else f"The source language is {source_language}."
    )
    user_prompt = (
        f"{source_hint} Translate the following text into target variant '{target_variant}'.\n"
        "Do not output explanations, only the final translation.\n\n"
        f"{text}"
    )

    temperature = 0.25
    if tone_style == "floptropica":
        temperature = 0.75

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
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

    # One retry with stricter language constraints when auto-detect drifts
    # or when style markers are missing for explicit meme tones.
    mismatch = (wants_chinese(target_variant) and not contains_cjk(translated)) or (
        target_variant == "en_us" and contains_cjk(translated)
    )
    style_missing = not has_required_style_markers(translated, tone_style, target_variant)
    if mismatch or style_missing:
        correction_rules = []
        if mismatch:
            correction_rules.append(f"Output must be in target variant '{target_variant}' only.")
        if style_missing and tone_style == "floptropica":
            correction_rules.append(
                "Reformat in full FLOPTROPICA mode: prioritize vibe over strict grammar, put emoji in EVERY sentence with some sentences having 2 emojis "
                "(not a single emoji cluster at the end), and include signature slang such as SLAYYYY, Poosay, pookie, Queen, diva. "
                "If output language is English, include at least one FULL-CAPS stress word like SLAYYYY, ICONIC, MAJOR, or LITERALLY."
            )
        if style_missing and tone_style == "linkedin":
            correction_rules.append(
                "Reformat as LinkedIn style with one sentence per paragraph, stronger professional skill-explicit phrasing, and strictly no emojis."
            )
        retry_payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"{system_prompt} This is a correction pass. "
                        + " ".join(correction_rules)
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        try:
            retry_response = requests.post(DEEPSEEK_URL, json=retry_payload, headers=headers, timeout=45)
            if retry_response.status_code == 200:
                retry_text = retry_response.json()["choices"][0]["message"]["content"].strip()
                if retry_text:
                    translated = retry_text
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
            pass

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