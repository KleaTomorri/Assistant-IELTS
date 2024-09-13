import requests
import os
from flask import Blueprint, render_template, request, session, redirect, url_for

from flask_app.models.reading import Question, UserAnswer, UserProgress


api_key = os.getenv('AI71_API_KEY')  
api_url = "https://api.ai71.ai/v1/chat/completions"

reading_bp = Blueprint('reading', __name__)

def clean_generated_content(content):
    unwanted_keywords = ["Title:", "Passage:", "User:", "Questions:", "User"]
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        for keyword in unwanted_keywords:
            if line.startswith(keyword):
                line = line[len(keyword):].strip()
        cleaned_lines.append(line)

    cleaned_content = '\n'.join(cleaned_lines)
    for keyword in unwanted_keywords:
        cleaned_content = cleaned_content.replace(keyword, "").strip()

    return cleaned_content

def generate_content(topic, module_type):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_messages = {
        "basic": "Write a simple  reading passage suitable for beginners in English as an IELTS practice.",
        "intermediate": "Write a moderately complex reading passage suitable for intermediate learners, along with intermediate level questions and multiple-choice options.",
        "advanced": "Write a complex reading passage suitable for advanced learners, along with advanced level questions and multiple-choice options."
    }

    payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {"role": "system", "content": f"Here’s a comprehensive system guideline for generating {system_messages[module_type]}"},
            {"role": "user", "content": f"Write a reading passage with a 2-word title providing as an IELTS practice about the topic: {topic} or about any event related with the {topic}."}
        ],
        "max_tokens": 600
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        passage_content = data["choices"][0]["message"]["content"]
        
        # Clean the generated passage content
        cleaned_passage_content = clean_generated_content(passage_content)

        # Assuming the first line is the title
        passage_lines = cleaned_passage_content.split('\n')
        title = clean_generated_content(passage_lines[0].strip())  # First line as title
        passage = '\n'.join(passage_lines[1:]).strip()  # Remaining lines as passage

        questions_payload = {
            "model": "tiiuae/falcon-180B-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate 12 multiple-choice questions and options based on the following passage: {passage} and the correct answer for each of the questions."}
            ],
            "max_tokens": 600
        }

        questions_response = requests.post(api_url, headers=headers, json=questions_payload)
        questions_response.raise_for_status()
        questions_data = questions_response.json()
        questions = questions_data["choices"][0]["message"]["content"]

        # Clean the generated questions content
        cleaned_questions_content = clean_generated_content(questions)

        questions_list = []
        correct_answers = {}

        for q_index, block in enumerate(cleaned_questions_content.split("\n\n")[:12]):  # Limit to 12 questions
            if block.strip():
                q_and_options = block.split("\n")
                question_text = clean_generated_content(q_and_options[0].strip())
                options = [clean_generated_content(opt.strip()) for opt in q_and_options[1:]]

                if not options:
                    continue

                correct_answer = options[0]
                questions_list.append({"question": question_text, "options": options})
                correct_answers[f'question_{q_index}'] = correct_answer

                question_data = {
                    "passage": passage,
                    "question_text": question_text,
                    "correct_answer": correct_answer,
                    "options": ", ".join(options)
                }
                Question.save(question_data)

        session['correct_answers'] = correct_answers

        return title, passage, questions_list

    except requests.RequestException as e:
        print("An error occurred:", e)
        return None, None, None

@reading_bp.route('/modules', methods=['GET'])
def reading_practices():
    return render_template('ielts_reading.html')

@reading_bp.route('/custom-reading-topic', methods=['GET'])
def basic():
    return render_template('custom_reading_module1.html')

@reading_bp.route('/generate_passage/<module_type>', methods=['POST'])
def generate_passage(module_type):
    topic = request.form['topic']
    
    title, passage, questions = generate_content(topic, module_type)

    if title is None or passage is None or questions is None:
        return render_template('error.html', message="An error occurred while generating the content.")

    return render_template('basic.html', title=title, passage=passage, questions=questions)

@reading_bp.route('/submit_answers', methods=['POST'])
def submit_answers():
    user_answers = {key: request.form.get(key) for key in request.form.keys() if key.startswith('question_')}
    correct_answers = session.get('correct_answers', {})
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    topic = session.get('topic')

    total_correct = 0
    total_questions = len(correct_answers)  # Ensure this reflects the number of questions

    answer_details = []

    for q_key, user_answer in user_answers.items():
        correct_answer = correct_answers.get(q_key)
        is_correct = user_answer == correct_answer
        question_id = Question.get_id_by_text(correct_answer)
        user_answer_data = {
            "user_id": user_id,
            "question_id": question_id,
            "user_answer": user_answer,
            "is_correct": is_correct
        }
        UserAnswer.save(user_answer_data)

        if is_correct:
            total_correct += 1

        answer_details.append({
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    score = (total_correct / total_questions) * 100

    user_progress = UserProgress.get_by_user_id(user_id)
    if user_progress:
        UserProgress.update(user_id, total_questions, total_correct)
    else:
        progress_data = {
            "user_id": user_id,
            "total_questions": total_questions,
            "correct_answers": total_correct,
            "score": score
        }
        UserProgress.save(progress_data)

    feedback = {
        "score": score,
        "total_correct": total_correct,
        "total_questions": total_questions,
        "answer_details": answer_details,
        "recommendations": generate_recommendations(total_correct, total_questions)
    }

    return render_template('reading_feedback1.html', feedback=feedback, user_name=user_name, topic=topic)


def generate_recommendations(correct, total):
    percentage = (correct / total) * 100
    if percentage == 100:
        return "Outstanding performance! You answered every question correctly. Keep up the excellent work!"
    elif percentage >= 75:
        return "Great job! You have a strong grasp of the material. To further enhance your skills, consider reviewing any missed areas."
    elif percentage >= 50:
        return "Good effort! You have a solid understanding but there's room for improvement. Review the material and focus on the areas where you missed questions."
    else:
        return "Keep practicing! Understanding and mastering this material takes time. Review the passage and questions thoroughly and try again."
