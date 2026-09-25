"""
app.py

A small Flask backend that connects to the Gemini API and powers a
"Breaking News" only chatbot. The chatbot's behaviour/personality is
defined in chatbot_config.py (SYSTEM_PROMPT).
"""

import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

from chatbot_config import SYSTEM_PROMPT, BOT_NAME

# Load variables from the .env file (GEMINI_API_KEY, etc.)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to your .env file before running the app."
    )

# Create the Gemini client once when the app starts.
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)


@app.route("/")
def home():
    """Render the chat UI."""
    return render_template("index.html", bot_name=BOT_NAME)


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and reply using the Gemini model."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message first."}), 400

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        reply_text = (response.text or "").strip()

        if not reply_text:
            reply_text = "Sorry, I couldn't generate a response. Please try again."

    except Exception as error:
        # Keep the error message generic for the user, log the real one.
        print(f"Gemini API error: {error}")
        reply_text = "Something went wrong while contacting the AI service. Please try again."

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
