from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import speech_recognition as sr
import uuid
from dotenv import load_dotenv

load_dotenv()


speaking_bp = Blueprint('speaking', __name__)

# Define questions
QUESTIONS = [
    "How are you today?",
    "What did you do over the weekend?",
    "What is your favourite spot in your city?",
    "What are some of the most pressing environmental issues facing our planet today, and what steps can we take to address them?",
    "How has technology impacted the way we communicate and interact with one another, and what are some of the potential consequences of these changes?",
    "What are some of the most effective strategies for promoting diversity and inclusion in the workplace, and how can we ensure that everyone feels valued and respected?",
    "How has the COVID-19 pandemic affected our daily lives, and what lessons can we learn from this experience to better prepare for future crises?",
    "What are some of the most important qualities of effective leadership, and how can we cultivate these skills in ourselves and others?",
    "What are the main benefits and drawbacks of working from home compared to working in an office?",
    "How do different cultures approach education and learning, and what can we learn from these diverse perspectives?",
    "What role does social media play in shaping public opinion and how can we navigate its influence?",
    "How do advancements in artificial intelligence impact various industries and job markets?",
]

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

@speaking_bp.route('/modules', methods=['GET'])
def speaking_modules():
    return render_template('ielts_speaking.html')

@speaking_bp.route('/advanced-speaking-practice', methods=['GET'])
def speaking_practice():
    current_index = session.get('current_question_index', 0)
    if current_index >= len(QUESTIONS):
        return redirect(url_for('speaking.end_of_practice'))
    
    return render_template('speaking1_practice.html', 
                           questions=QUESTIONS, 
                           current_index=current_index, 
                           total_questions=len(QUESTIONS))

@speaking_bp.route('/next_question', methods=['POST'])
def next_question():
    current_index = session.get('current_question_index', 0)
    if current_index < len(QUESTIONS) - 1:
        session['current_question_index'] = current_index + 1
    return redirect(url_for('speaking.speaking_practice'))

@speaking_bp.route('/submit_audio', methods=['POST'])
def submit_audio():
    if 'audio' not in request.files:
        return 'No audio file provided', 400

    audio_file = request.files['audio']
    unique_filename = str(uuid.uuid4()) + '.wav'
    audio_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    audio_file.save(audio_path)

    current_index = session.get('current_question_index', 0)
    session.setdefault('audio_files', []).append(unique_filename)  # Save filenames instead of paths
    
    feedback = transcribe_audio(audio_path)
    session[f'answer_{current_index}'] = feedback
    
    if current_index >= len(QUESTIONS) - 1:
        return redirect(url_for('speaking.end_of_practice'))
    else:
        return redirect(url_for('speaking.speaking_practice'))

@speaking_bp.route('/submit_all', methods=['POST'])
def submit_all():
    audio_files = session.get('audio_files', [])
    feedbacks = {}
    
    for audio_file in audio_files:
        audio_path = os.path.join(UPLOAD_FOLDER, audio_file)
        feedback = transcribe_audio(audio_path)
        feedbacks[audio_file] = feedback
    
    session.pop('audio_files', None)  # Clean up session
    return render_template('sp_feedback.html', feedbacks=feedbacks)

@speaking_bp.route('/feedback', methods=['GET'])
def feedback():
    return render_template('sp_feedback.html', feedbacks={})
