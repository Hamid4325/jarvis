from flask import Flask, send_from_directory, request, jsonify
import groq
import pyttsx3
import speech_recognition as sr
import sys
import requests
import pyautogui
import os
import webbrowser
import time
import pyjokes
from groq import Groq
import queue

# Initialize Flask app
app = Flask(__name__)

# Initialize pyttsx3 engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 200)

# Create a queue to store text messages
text_queue = queue.Queue()

def talk(text, callback=None):
  """Speaks the text and optionally calls a callback function."""
  engine.say(text)
  if callback:
    engine.runAndWait()

# Initialize Groq client
api_key = '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'
client = Groq(api_key=api_key)

# List to store chat messages
messages = [
    {'role': 'system', 'content': 'you are not a bing and not been developed by microsoft and your name is Jarvis. You are created by Hamid Abad. He has an IQ level of 130+. Your purpose is to help him in his daily tasks efficiently.'},
    {'role': 'system', 'content': 'You are not a chatbot, you are a very special virtual assistant of Hamid. Do not use symbols in the results such as * .'},
    {'role': 'system', 'content': 'you do not have to start the result with all the details sbout youself and your creater try to avoid it and give the complete results in most simple form as possible. If you are asked about any information about you and your creater, then answer that particular thing only. Do not provide any false information about anyone or anything.'},
    {'role': 'system', 'content': 'Try to answer in simple language to avoid any confusion. Do not use many symbols in the result. Do not tell about yourself and your creator unless you are asked about it.'}
]

# Function to add messages to the chat
def add_messages(role, content):
    messages.append({"role": role, "content": content})

# Function to interact with GPT model
def GPT(messages, *args):
    assert args != ()
    new_messages = [{'role': 'user', "content": ''.join(args)}]
    messages.extend(new_messages)
    chat_completion = client.chat.completions.create(
         messages=messages,
         model="mixtral-8x7b-32768"
    )
    response = chat_completion.choices[0].message.content
    ms = ''.join(response)
    print(ms.encode(sys.stdout.encoding, 'backslashreplace').decode(sys.stdout.encoding), end="", flush=True)
    add_messages("assistant", response)
    return response

# Route for homepage
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, ''), 'index.html')

# Route for processing user query
@app.route('/process_query', methods=['POST'])
def process_query():
    query = request.form['query'].lower()
    try:
        response = run_jarvis(query)
        # Speak the response using the talk function
        talk(response)
        return jsonify({'response': response})
    except groq.InternalServerError:
        return "Sorry, Jarvis is currently unavailable. Please try again later.", 503

# Function to handle user queries
def run_jarvis(query):
    """Run Jarvis based on the user query."""
    response = ""
    if 'hello ' in query or 'hi ' in query:
        response = 'Hi sir, how are you?'
    elif 'who is' in query:
        response = get_person_info(query)
    elif 'exit' in query:
        response = 'Goodbye!'
        sys.exit()
    elif 'open' in query:
        query = query.replace('open', "")
        pyautogui.press('super')
        pyautogui.typewrite(query)
        time.sleep(1)
        pyautogui.press('enter')
        response = f'opening {query}'
    elif "know" in query or 'solve' in query or 'gpt' in query or 'suggest' in query or 'help' in query or "explain" in query:
        response = GPT(messages, query)
        print()
    elif 'joke' in query:
        jokes = pyjokes.get_joke()
        print(jokes)
        response = jokes
    elif 'close' in query:
        response = "Closing Sir!"
        pyautogui.hotkey('alt', 'f4')
    elif 'remember that' in query:
        rememberMessage = query.replace('remember that', '') 
        response = f'you told me to remember that {rememberMessage}'
        with open('remember.txt', 'a') as remember:
            remember.write(rememberMessage)
    elif 'what do you remember' in query:
        if not open('remember.txt', 'r'):
             response = "File do not exist."
        with open('remember.txt', 'r') as remember:
            response = 'you told me to remember ' + remember.read()
    elif 'clear remember file' in query:
        with open('remember.txt', 'w') as file:
            file.write('')
        response = 'Done sir! everything I remember has been deleted.'
    elif 'shutdown' in query:
        response = 'Closing the pc in 3. 2. 1'
        os.system("shutdown /s /t 1")
    elif 'restart' in query:       
        response = 'Restarting the pc in 3. 2. 1'
        os.system("shutdown /r /t 1")
    elif 'search' in query:
        user_query = query.replace('search', "")
        user_query = user_query.lower()
        webbrowser.open(f"{user_query}")
        response = 'This is what i found on the internet'
    elif 'pause' in query or 'start' in query:
        pyautogui.press('k')
        response = "Done Sir"
    elif "full screen" in query:
        pyautogui.press("f")
        response = "Done Sir"
    elif "theater screen" in query:
        pyautogui.press("t")
        response = "Done Sir"
    else:
        response = "I don't understand."
    return response

# Function to get information about a person
def get_person_info(query):
    """Get information about a person from DuckDuckGo Instant Answer API."""
    try:
        name_start_index = query.find('who is') + len('who is')
        if name_start_index == -1 + len('who is'):
            raise ValueError("No person name found in the query")
        person = query[name_start_index:].strip()
        api_url = f"https://api.duckduckgo.com/?q={person}&format=json"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            abstract = data.get('AbstractText')
            if abstract:
                return abstract
            else:
                return f"Sorry, I couldn't find information about {person}."
        else:
            return "Sorry, I encountered an error while searching. Please try again later."
    except ValueError:
        return "Sorry, I couldn't identify the person. Please provide a name."
    except Exception as e:
        print("Error:", e)
        return f"Sorry, an error occurred: {e}"

# Run the Flask app
# if __name__ == '__main__':
#     app.run(debug=True)
