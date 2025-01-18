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

# List of whitelisted users
WHITELISTED_USERS = ["urfavbestiecupid", "uscscyber", "WhiteStarCyber", "BenXiadous"]

# Function to send a file to Discord via webhook
def send_to_discord(file_path):
    if DISCORD_WEBHOOK:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/csv')}
            response = requests.post(DISCORD_WEBHOOK, files=files)
        
        if response.status_code == 204:
            return True
        else:
            logger.error(f"Failed to send file to Discord: {response.status_code}")
    else:
        logger.error("Discord Webhook URL is not set!")
    return False

# Route to handle commands
@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get("command")
    user_id = data.get("user_id")
    chat_logs_csv = data.get("chat_logs_csv")

    # Verify user is whitelisted
    if user_id not in WHITELISTED_USERS:
        return jsonify({"status": "error", "message": "User is not whitelisted."}), 403

    # Handle "Piece of cake" command
    if command == "Piece of cake":
        if chat_logs_csv:
            csv_filename = f"chat_logs_{user_id}.csv"
            with open(csv_filename, 'w') as f:
                f.write(chat_logs_csv)
            
            if send_to_discord(csv_filename):
                os.remove(csv_filename)
                return jsonify({"status": "success", "message": "Logs sent to Discord."}), 200
            else:
                os.remove(csv_filename)
                return jsonify({"status": "error", "message": "Failed to send logs to Discord."}), 500
        return jsonify({"status": "error", "message": "Missing chat_logs_csv."}), 400

    # Handle "Judgement Day" command
    elif command == "Judgement Day":
        shutdown_message = "Judgement Day initiated on the Roblox server."
        if send_to_discord(shutdown_message):
            return jsonify({"status": "success", "message": "Shutdown sequence initiated."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to send shutdown message to Discord."}), 500

    # Invalid command
    return jsonify({"status": "error", "message": "Invalid command."}), 400

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
