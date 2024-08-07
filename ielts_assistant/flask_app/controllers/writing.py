import os
import random
from flask import Blueprint, render_template, request, redirect, url_for, session,Request
from ai71 import AI71


AI71_API_KEY = "api71-api-547d865a-e5de-4710-8fa8-55b1579a6392"
client = AI71(AI71_API_KEY)

writing_bp = Blueprint('writing', __name__)

import re

def clean_text(text):
    unwanted_patterns = [r'\bUSER\b', r'\bPROMPT\b', r'\bSITUATION\b', r'\bUSER\b']
    combined_pattern = '|'.join(unwanted_patterns)
    cleaned_text = re.sub(combined_pattern, '', text)
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text

@writing_bp.route('/modules', methods=['GET'])
def writing_practices():
    return render_template('ielts_writing.html')


@writing_bp.route('/general-task1', methods=['GET'])
def general_task1():
   
    messages = [
        {"role": "system", "content": "You are an IELTS examiner. Generate a unique Task 1 prompt for IELTS General Writing."},
        {"role": "user", "content": "Task 1: Candidates are presented with a situation and are asked to write a letter requesting information or explaining the situation. The letter may be personal, semi-formal, or formal in style. Provide a prompt for this task."}
    ]
    task1_response = client.chat.completions.create(
        model="tiiuae/falcon-180B-chat",
        messages=messages,
        temperature=0.7 
    )
    
    
    task1_data = task1_response.choices[0].message.content
    
  
    task1_data = clean_text(task1_data)
    
    session['task1'] = task1_data  
    return render_template('general_task1.html', task=task1_data)


def clean_prompt(prompt):
   
    prompt = re.sub(r'\b(USER:|PROMPT:|SITUATION:|TASK:)\b', '', prompt, flags=re.IGNORECASE)
    return prompt.strip()


@writing_bp.route('/general-task2', methods=['POST'])
def general_task2():

    task1_answer = request.form.get('task1_answer')
    session['task1_answer'] = task1_answer

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Generate a unique Task 2 prompt for IELTS General Writing."},
        {"role": "user", "content": "Task 2: Candidates are asked to write an essay in response to a point of view, argument, or problem. The essay can be slightly more personal in style than the Academic Writing Task 2 essay. Provide a prompt for this task."}
    ]
    task2_response = client.chat.completions.create(
        model="tiiuae/falcon-180B-chat",
        messages=messages,
        temperature=0.7  
    )

 
    task2_data = task2_response.choices[0].message.content
    task2_data_cleaned = clean_prompt(task2_data)
    session['task2'] = task2_data_cleaned  

    return render_template('general_task2.html', task=task2_data_cleaned)





@writing_bp.route('/submit', methods=['POST'])
def submit_tasks():
    task1_answer = session.get('task1_answer', '') or request.form.get('task1_answer', '')
    task2_answer = session.get('task2_answer', '') or request.form.get('task2_answer', '')

    feedback_prompt = f"""
    You are an IELTS examiner. Your task is to provide detailed feedback on the following user answers based on the IELTS Writing Mark Schemes:
    - Task Achievement
    - Coherence and Cohesion
    - Lexical Resource
    - Grammatical Range and Accuracy

    Do not generate new answers. Instead, analyze the provided answers and give feedback on the following aspects:
    1. Grammar: Identify specific grammatical errors, if any, and mention strong points.
    2. Vocabulary: Evaluate the richness and appropriateness of vocabulary used, mentioning any misused words.
    3. Coherence: Assess the logical flow and coherence of the content, noting any awkward transitions or unclear points.
    4. Context: Determine if the answer appropriately addresses the task requirements, mentioning if any part of the task was misunderstood or left unaddressed.
    5. Word Count: Provide the word count and mention if it meets the required length.

    Provide feedback for each task separately for the given answers.

    Task 1 Answer:
    {task1_answer}

    Task 2 Answer:
    {task2_answer}
    """

    try:
        feedback_response = client.chat.completions.create(
            model="tiiuae/falcon-180B-chat",
            messages=[{"role": "user", "content": feedback_prompt}],
            temperature=0.0
        )

        logging.debug("Feedback Response: %s", feedback_response)

        feedback = feedback_response.choices[0].message.content if feedback_response and feedback_response.choices else None
        if feedback:
    
            task1_feedback, task2_feedback = "", ""
            if "Task 2" in feedback:
                parts = feedback.split("Task 2", 1)
                task1_feedback = parts[0].strip()
                task2_feedback = parts[1].strip()
            else:
                task1_feedback = feedback.strip()
            logging.debug("Task 1 Feedback: %s", task1_feedback)
            logging.debug("Task 2 Feedback: %s", task2_feedback)
            def extract_sections(feedback):
                sections = {}
                for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]:
                    try:
                        start = feedback.index(f"{section}:") + len(f"{section}:")
                        end = feedback.find("\n", start)
                        if end == -1:
                            end = len(feedback)
                        sections[section] = feedback[start:end].strip()
                    except ValueError:
                        sections[section] = "No feedback available."
                return sections

            task1_sections = extract_sections(task1_feedback)
            task2_sections = extract_sections(task2_feedback)
        else:
            task1_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}
            task2_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}
    except Exception as e:
        logging.error("Error parsing feedback: %s", e)
        task1_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}
        task2_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}

    return render_template('academic_writing_feedback.html', 
                           feedback_task1_word_count=task1_sections['Word Count'],
                           feedback_task1_grammar=task1_sections['Grammar'], 
                           feedback_task1_vocabulary=task1_sections['Vocabulary'],
                           feedback_task1_coherence=task1_sections['Coherence'],
                           feedback_task1_context=task1_sections['Context'],
                           feedback_task2_word_count=task2_sections['Word Count'],
                           feedback_task2_grammar=task2_sections['Grammar'], 
                           feedback_task2_vocabulary=task2_sections['Vocabulary'],
                           feedback_task2_coherence=task2_sections['Coherence'],
                           feedback_task2_context=task2_sections['Context'])












#ACADEMIC WRITING ROUTES



@writing_bp.route('/academic_task1', methods=['GET', 'POST'])
def academic_task1():
    if request.method == 'POST':
        session['academic_task1_answer'] = request.form.get('academic_task1_answer')
        return redirect(url_for('writing.academic_task2'))

    return render_template('academic_task1.html')


@writing_bp.route('/academic_task2', methods=['GET', 'POST'])
def academic_task2():
    if request.method == 'POST':
        session['academic_task2_answer'] = request.form.get('academic_task2_answer')
        return redirect(url_for('writing.submit_academic_tasks'))

    return render_template('acdemic_task2.html')



import logging

@writing_bp.route('/submit_academic_tasks', methods=['GET', 'POST'])
def submit_academic_tasks():
    academic_task1_answer = session.get('academic_task1_answer', '') or request.form.get('academic_task1_answer', '')
    academic_task2_answer = session.get('academic_task2_answer', '') or request.form.get('academic_task2_answer', '')

    feedback_prompt = f"""
    You are an IELTS examiner. Your task is to provide detailed feedback on the following user answers based on the IELTS Writing Mark Schemes:
    - Task Achievement
    - Coherence and Cohesion
    - Lexical Resource
    - Grammatical Range and Accuracy

    Do not generate new answers. Instead, analyze the provided answers and give feedback on the following aspects:
    1. Grammar: Identify specific grammatical errors, if any, and mention strong points.
    2. Vocabulary: Evaluate the richness and appropriateness of vocabulary used, mentioning any misused words.
    3. Coherence: Assess the logical flow and coherence of the content, noting any awkward transitions or unclear points.
    4. Context: Determine if the answer appropriately addresses the task requirements, mentioning if any part of the task was misunderstood or left unaddressed.
    5. Word Count: Provide the word count and mention if it meets the required length.

    Provide feedback for each task separately for the given answers.

    Task 1 Answer:
    {academic_task1_answer}

    Task 2 Answer:
    {academic_task2_answer}
    """

    try:
        feedback_response = client.chat.completions.create(
            model="tiiuae/falcon-180B-chat",
            messages=[{"role": "user", "content": feedback_prompt}],
            temperature=0.0
        )

        logging.debug("Feedback Response: %s", feedback_response)

        feedback = feedback_response.choices[0].message.content if feedback_response and feedback_response.choices else None
        if feedback:

            task1_feedback, task2_feedback = "", ""
            if "Task 2 Answer:" in feedback:
                parts = feedback.split("Task 2 Answer:", 1)
                task1_feedback = parts[0].strip()
                task2_feedback = parts[1].strip()
            else:
                task1_feedback = feedback.strip()
            logging.debug("Task 1 Feedback: %s", task1_feedback)
            logging.debug("Task 2 Feedback: %s", task2_feedback)

            def extract_sections(feedback):
                sections = {}
                for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]:
                    try:
                        start = feedback.index(f"{section}:") + len(f"{section}:")
                        end = feedback.find("\n", start)
                        if end == -1:
                            end = len(feedback)
                        sections[section] = feedback[start:end].strip()
                    except ValueError:
                        sections[section] = "No feedback available."
                return sections

            task1_sections = extract_sections(task1_feedback)
            task2_sections = extract_sections(task2_feedback)
        else:
            task1_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}
            task2_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}
    except Exception as e:
        logging.error("Error parsing feedback: %s", e)
        task1_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}
        task2_sections = {section: "No feedback available." for section in ["Grammar", "Vocabulary", "Coherence", "Context", "Word Count"]}

    return render_template('academic_writing_feedback.html', 
                           feedback_task1_word_count=task1_sections['Word Count'],
                           feedback_task1_grammar=task1_sections['Grammar'], 
                           feedback_task1_vocabulary=task1_sections['Vocabulary'],
                           feedback_task1_coherence=task1_sections['Coherence'],
                           feedback_task1_context=task1_sections['Context'],
                           feedback_task2_word_count=task2_sections['Word Count'],
                           feedback_task2_grammar=task2_sections['Grammar'], 
                           feedback_task2_vocabulary=task2_sections['Vocabulary'],
                           feedback_task2_coherence=task2_sections['Coherence'],
                           feedback_task2_context=task2_sections['Context'])
