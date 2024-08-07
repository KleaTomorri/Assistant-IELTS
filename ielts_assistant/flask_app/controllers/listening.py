import requests
import os
from flask import Blueprint, render_template, request
from gtts import gTTS
from ai71 import AI71

listening_bp = Blueprint('listening', __name__, url_prefix='/listening')

@listening_bp.route('/listening-practice', methods=['GET'])
def listening_page():
    return render_template('listening.html')

@listening_bp.route('/modules', methods=['GET'])
def listening_modules():
    return render_template('ielts_listening.html')

@listening_bp.route('/listening-practice', methods=['POST'])
def process_listening():
    topic = request.form['topic']
    passage, questions = generate_listening_passage_and_questions(topic)
    audio_url = generate_audio(passage)
    return render_template('listening_result.html', audio_url=audio_url, questions=questions)




def generate_listening_passage_and_questions(topic):
    api_url = "https://api.ai71.ai/v1/chat/completions"
    api_key = "api71-api-547d865a-e5de-4710-8fa8-55b1579a6392"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


    passage_payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Write a simple conversation between Sam and Anna for IELTS listening preparation about the topic: {topic}."}
        ],
        "max_tokens": 150
    }

    try:
        response = requests.post(api_url, headers=headers, json=passage_payload)
        response.raise_for_status()
        data = response.json()
        passage = data["choices"][0]["message"]["content"]

        print("Generated Passage:")
        print(passage)

       
        questions_payload = {
            "model": "tiiuae/falcon-180B-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate 3 fill-in-the-blank questions, 2 alternative questions, and 2 typing questions about the following conversation: {passage} between Sam and Anna. Format each question separately with a clear label for its type."}
            ],
            "max_tokens": 200
        }

        questions_response = requests.post(api_url, headers=headers, json=questions_payload)
        questions_response.raise_for_status()
        questions_data = questions_response.json()
        questions_raw = [choice["message"]["content"] for choice in questions_data["choices"]]

      
        fill_in_the_blank = []
        alternatives = []
        typing = []

        for question in questions_raw:
            if "fill-in-the-blank" in question:
                fill_in_the_blank.append(question)
            elif "alternative" in question:
                alternatives.append(question)
            elif "typing" in question:
                typing.append(question)

      
        questions = {
            "fill_in_the_blank": fill_in_the_blank,
            "alternatives": alternatives,
            "typing": typing
        }

        print("Generated Questions:")
        print(questions)

        return passage, questions

    except requests.RequestException as e:
        print("An error occurred:", e)
        return None, None


def generate_audio(passage_text):
    audio_dir = os.path.join('flask_app', 'static', 'audio')
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    audio_file = os.path.join(audio_dir, 'output.mp3')
    tts = gTTS(passage_text, lang='en', slow=False)
    tts.save(audio_file)

    if os.path.exists(audio_file):
        print(f"Audio file created successfully: {audio_file}")
        return 'audio/output.mp3'
    else:
        print("Error: Audio file was not created.")
        return None

@listening_bp.route('/submit_listening_answers', methods=['POST'])
def submit_listening_answers():
   
    answers = request.form.to_dict()
  
    
    print("Submitted Answers:")
    print(answers)
    

    return render_template('some_response_page.html')  
