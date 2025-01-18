import os
import logging
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from flask_cors import CORS

# Load the environment variables from .env file
load_dotenv()

# Fetch the Discord Webhook URL from environment variable
DISCORD_WEBHOOK = os.getenv('DISCORD_RELAY')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app instance
app = Flask(__name__)

# Enable CORS for trusted origins
CORS(app, resources={r"/*": {"origins": "*"}})

if not DISCORD_WEBHOOK:
    raise ValueError("Discord Webhook URL is not set in the environment variables.")

# Send a message to Discord via webhook
def send_to_discord(content):
    if DISCORD_WEBHOOK:
        payload = {'content': content}
        try:
            response = requests.post(DISCORD_WEBHOOK, json=payload)
            if response.status_code == 204:
                logger.info("Message sent to Discord successfully.")
                return True
            else:
                logger.error(f"Failed to send message to Discord: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message to Discord: {e}")
    else:
        logger.error("Discord Webhook URL is not set!")
    return False

# Route to handle the /urdone command
@app.route('/urdone', methods=['POST'])
def urdone():
    data = request.json
    user_id = data.get("user_id")
    chat_logs_csv = data.get("chat_logs_csv")

    if user_id and chat_logs_csv:
        # Save or process CSV data
        log_message = f"User {user_id} chat logs (CSV):\n{chat_logs_csv}"
        if send_to_discord(log_message):
            return jsonify({"status": "success", "message": "Logs sent to Discord."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to send logs to Discord."}), 500
    return jsonify({"status": "error", "message": "Missing user_id or chat_logs_csv."}), 400

# Route to handle the /thepurge command
@app.route('/thepurge', methods=['POST'])
def thepurge():
    shutdown_message = "Shutdown sequence initiated on the Roblox server."
    if send_to_discord(shutdown_message):
        func = request.environ.get('werkzeug.server.shutdown')
        if func:
            func()
        return jsonify({"status": "success", "message": "Shutdown sequence initiated."}), 200
    return jsonify({"status": "error", "message": "Failed to send shutdown message to Discord."}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run on port 5000, accessible to Roblox
