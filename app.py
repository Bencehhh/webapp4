import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from flask_cors import CORS

# Load the environment variables from .env file
load_dotenv()

# Fetch the Discord Webhook URL from environment variable
DISCORD_WEBHOOK = os.getenv('DISCORD_RELAY')

# Create Flask app instance
app = Flask(__name__)

# Enable CORS for all routes (this allows requests from any origin)
CORS(app)

# Send a message to Discord via webhook
def send_to_discord(content):
    if DISCORD_WEBHOOK:
        payload = {'content': content}
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        if response.status_code == 204:
            return True
        else:
            print(f"Failed to send message to Discord: {response.status_code}")
    else:
        print("Discord Webhook URL is not set!")
    return False

# Route to handle the .urdone command
@app.route('/urdone', methods=['POST'])
def urdone():
    data = request.json
    user_id = data.get("user_id")
    chat_logs = data.get("chat_logs")

    if user_id and chat_logs:
        log_message = f"User {user_id} chat logs:\n" + "\n".join(chat_logs)
        if send_to_discord(log_message):
            return jsonify({"status": "success", "message": "Logs sent to Discord."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to send logs to Discord."}), 500
    return jsonify({"status": "error", "message": "Missing user_id or chat_logs."}), 400

# Route to handle the .thepurge command
@app.route('/thepurge', methods=['POST'])
def thepurge():
    # Perform a shutdown action (for demonstration, you can adjust as per your server setup)
    shutdown_message = "Shutdown sequence initiated on the Roblox server."
    if send_to_discord(shutdown_message):
        return jsonify({"status": "success", "message": "Shutdown sequence initiated."}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to send shutdown message to Discord."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run on port 5000, accessible to Roblox
