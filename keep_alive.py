from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive! 🤖"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/status')
def status():
    return {
        "status": "online",
        "message": "Discord bot is running"
    }

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()