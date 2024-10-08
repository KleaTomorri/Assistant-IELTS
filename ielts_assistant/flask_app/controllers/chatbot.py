from flask import Blueprint, render_template, request, session, jsonify
from ai71 import AI71
from dotenv import load_dotenv
import os

chatbot_bp = Blueprint('chatbot', __name__)

load_dotenv()

AI71_API_KEY = os.getenv('AI71_API_KEY')

client = AI71(AI71_API_KEY)

with open("chatbot.guide") as f:
    chatbotGuide = f.read()

@chatbot_bp.route('/')
def chatbot():
    session.clear()
    return render_template("chatbot.html")

@chatbot_bp.route('/chat', methods=["POST"])
def chat():
    if 'conversation' not in session:
        session['conversation'] = []
    user_message = request.form["message"]
    session['conversation'].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="tiiuae/falcon-180B-chat",
            messages=[{"role": "system", "content": chatbotGuide}] + session['conversation']
        )
        output = response.choices[0].message.content
        session['conversation'].append({"role": "assistant", "content": output})
        return jsonify({"response": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
