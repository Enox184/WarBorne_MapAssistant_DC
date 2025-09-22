from flask import Flask, request
from threading import Thread
import datetime

app = Flask('')

def log_request(endpoint):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    print(f"[{timestamp}] {endpoint} request from {client_ip} - {user_agent}")

@app.route('/')
def home():
    log_request("HOME")
    return "Bot is alive! 🤖"

@app.route('/ping')
def ping():
    log_request("PING")
    return "pong"

@app.route('/status')
def status():
    log_request("STATUS")
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