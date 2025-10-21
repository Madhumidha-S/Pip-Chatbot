from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from flask_session import Session
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

class PipChatbot:
    def __init__(self, model, bot_name="Pip"):
        self.model = model
        self.bot_name = bot_name
        self.system_prompt = f"You are a helpful assistant named {self.bot_name}. Always refer to yourself as {self.bot_name}."

    def get_bot_response(self, user_input, history):
        conversation = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in history]
        )
        full_prompt = f"{self.system_prompt}\n{conversation}\nuser: {user_input}"
        try:
            response = self.model.generate_content(full_prompt)
            bot_text = response.text.strip()
        except Exception as e:
            bot_text = f"[Error] Could not get response: {str(e)}"
        return bot_text
    
bot = PipChatbot(model)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    if 'history' not in session:
        session['history'] = []

    history = session['history']
    history.append({"role": "user", "content": user_message})
    bot_reply = bot.get_bot_response(user_message, history)
    history.append({"role": "bot", "content": bot_reply})
    session['history'] = history

    return jsonify({'message': bot_reply})

@app.route('/clear', methods=['POST'])
def clear_chat():
    session.pop('history', None)
    return jsonify({'message': "Chat history cleared"})

if __name__ == '__main__':
    app.run(debug=True)
