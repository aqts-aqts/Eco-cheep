import os
import base64
from openai import OpenAI
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
from user import get_user, create_user, check_password, update_user_messages, update_user_quests, finish_quest
from util import format_suggestions

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))
Session(app)

@app.route('/')
def index():
    if 'username' in session and session['username'] is not None:
        return redirect(url_for('cheep'))
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login_user', methods=['POST'])
def log_in():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return redirect(url_for('login'))
    
    user = get_user(username)
    if user is None or not check_password(password, user['password']):
        return redirect(url_for('login'))
    
    session['username'] = username
    return redirect(url_for('cheep'))

@app.route('/signup_user', methods=['POST'])
def sign_up():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return redirect(url_for('signup'))
    
    user = get_user(username)
    if user is not None:
        return redirect(url_for('signup'))
    
    create_user(username, password)
    session['username'] = username
    return redirect(url_for('cheep'))

@app.route('/cheep', methods=['POST', 'GET'])
def cheep():
    user = get_user(session['username'])

    if 'cheep_messages' not in session:
        session['cheep_messages'] = []
        for message in user['cheep_messages']:
            if message['role'] == 'user':
                session['cheep_messages'].append((session['username'], message['content']))
            elif message['role'] == 'assistant':
                session['cheep_messages'].append(('Cheep', message['content']))

    if request.method == 'POST':
        user_message = request.form['message']
        user['cheep_messages'].append({'role': 'user', 'content': user_message})

        bot_response = get_bot_response(user)
        user['cheep_messages'].append({'role': 'assistant', 'content': bot_response})

        session['cheep_messages'].append((session['username'], user_message))
        session['cheep_messages'].append(('Cheep', bot_response))
        update_user_messages(session['username'], user['cheep_messages'])
        
        session.modified = True
        return redirect(url_for('cheep'))

    return render_template('cheep.html', chat_history=session['cheep_messages'])

@app.route('/clear_chat')
def clear_chat():
    user = get_user(session['username'])
    user['cheep_messages'] = [{'role': 'system', 'content': open('data/cheep.txt').read()}]

    if 'cheep_messages' in session:
        session['cheep_messages'] = []

    update_user_messages(session['username'], user['cheep_messages'])
    return redirect(url_for('cheep'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('cheep_messages', None)
    return redirect(url_for('index'))

@app.route('/get_context', methods=['POST'])
def get_context():
    user_response = request.form['response']
    next_question, suggestions = process_user_response(user_response)
    return jsonify({'next_question': next_question, 'suggestions': suggestions})

@app.route('/change_suggestions', methods=['POST'])
def change_suggestions():
    context = request.form['response']
    suggestions = get_suggestions(context, 'suggestions')
    return jsonify({'suggestions': suggestions})

@app.route('/select_suggestion',  methods=['POST'])
def select_suggestion():
    suggestion = request.form['suggestion']
    exp = request.form['exp']
    proof = request.form['proof']

    user = get_user(session['username'])
    user['quests'].append({'description': suggestion, 'exp': exp, 'proof': proof})

    update_user_quests(session['username'], user['quests'])
    return jsonify({'proof': proof})

@app.route('/get_quests', methods=['GET'])
def get_quests():
    user = get_user(session['username'])
    return jsonify({'quests': user['quests']})

@app.route('/complete_quest', methods=['POST'])
def complete_quest():
    quest = request.form['quest']
    
    if 'questImage' not in request.files:
        return jsonify({'status': 'incomplete'})
    
    image = request.files['questImage']
    encoded_image = base64.b64encode(image.read()).decode('utf-8')
    url = f'data:image/png;base64,{encoded_image}'

    user_content = [
        {'type': 'text', 'text': quest},
        {'type': 'image_url', 'image_url': {'url': url}}
    ]

    msgs = [{'role': 'system', 'content': open('data/verifier.txt').read()}]
    msgs.append({'role': 'user', 'content': user_content})
    response = client.chat.completions.create(model='gpt-4o', messages=msgs).choices[0].message.content

    if response.lower() == 'incomplete':
        return jsonify({'status': 'incomplete'})
    elif response.lower() == 'complete':
        finish_quest(session['username'], quest)
        return jsonify({'status': 'complete'})
    else:
        return jsonify({'status': 'error'})

def process_user_response(response: str):
    if 'context_messages' not in session or session['context_messages'] is None:
        session['context_messages'] = [{"role": "system", "content": open("data/context_adder.txt").read()}]

    session['context_messages'].append({"role": "user", "content": response})
    next_question = client.chat.completions.create(model="gpt-4o", messages=session['context_messages']).choices[0].message.content
    session['context_messages'].append({"role": "assistant", "content": next_question})

    if '{' in next_question:
        suggestions = get_suggestions(next_question)
        session['context_messages'] = None
        return None, suggestions
    
    session.modified = True
    return next_question, []

def get_suggestions(context: str, type: str = 'context'):
    if 'environmental_messages' not in session or session['environmental_messages'] is None:
        session['environmental_messages'] = [{"role": "system", "content": open("data/environment_helper.txt").read()}]
    print(session['environmental_messages'])
    session['environmental_messages'].append({"role": "user", "content": context})
    suggestions = client.chat.completions.create(model="gpt-4o", messages=session['environmental_messages']).choices[0].message.content
    session['environmental_messages'].append({"role": "assistant", "content": suggestions})

    session.modified = True
    return format_suggestions(suggestions)

def get_bot_response(user: dict[str, str | list[str] | list[dict[str, str]]]) -> str:
    response = client.chat.completions.create(model='gpt-4o', messages=user['cheep_messages']).choices[0].message.content
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)