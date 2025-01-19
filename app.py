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
    logger.critical("Discord Webhook URL is not set in the environment variables.")
    raise ValueError("Discord Webhook URL is required for this application to work.")

# List of whitelisted users
WHITELISTED_USERS = ["urfavbestiecupid", "uscscyber", "WhiteStarCyber", "BenXiadous"]

# Function to send a file to Discord via webhook
def send_to_discord(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/csv')}
            response = requests.post(DISCORD_WEBHOOK, files=files)

        if response.status_code == 204:
            logger.info("File successfully sent to Discord.")
            return True
        else:
            logger.error(f"Failed to send file to Discord: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"Error sending file to Discord: {e}")
    return False

# Route to handle commands
@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get("command", "").lower()  # Make command case-insensitive
    user_id = data.get("user_id")
    chat_logs_csv = data.get("chat_logs_csv")

    if command == "howdy":
        if user_id and chat_logs_csv:
            csv_filename = f"chat_logs_{user_id}.csv"
            try:
                # Save chat logs to a file
                with open(csv_filename, 'w') as f:
                    f.write(chat_logs_csv)

                # Send CSV file to Discord
                if send_to_discord(csv_filename):
                    os.remove(csv_filename)  # Clean up file after sending
                    return jsonify({"status": "success", "message": "Logs sent to Discord."}), 200
                else:
                    os.remove(csv_filename)  # Clean up file on failure
                    return jsonify({"status": "error", "message": "Failed to send logs to Discord."}), 500
            except Exception as e:
                logger.exception(f"Error handling 'Howdy' command: {e}")
                return jsonify({"status": "error", "message": "Internal server error."}), 500
        else:
            return jsonify({"status": "error", "message": "Missing user_id or chat_logs_csv."}), 400
    elif command == "bye bye":
        shutdown_message = "Shutdown sequence initiated on the Roblox server."
        if send_to_discord(shutdown_message):
            return jsonify({"status": "success", "message": "Shutdown sequence initiated."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to send shutdown message to Discord."}), 500
    else:
        return jsonify({"status": "error", "message": "Unknown command."}), 400

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
