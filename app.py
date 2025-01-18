import os
import logging
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from flask_cors import CORS
import time
import threading
import signal

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
def send_to_discord(file_path=None, message=None):
    if DISCORD_WEBHOOK:
        try:
            if file_path:
                # Send the file
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path, f, 'text/csv')}
                    response = requests.post(DISCORD_WEBHOOK, files=files)
            elif message:
                # Send a message if no file
                payload = {'content': message}
                response = requests.post(DISCORD_WEBHOOK, json=payload)

            logger.info(f"Discord Webhook Response: {response.status_code} - {response.text}")
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error while sending to Discord: {e}")
            return False
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
        try:
            # Save the CSV data to a file
            csv_filename = f"chat_logs_{user_id}.csv"
            with open(csv_filename, 'w') as f:
                f.write(chat_logs_csv)

            # Send the CSV file to Discord
            if send_to_discord(csv_filename):
                os.remove(csv_filename)  # Clean up the file after sending it to Discord
                return jsonify({"status": "success", "message": "Logs sent to Discord."}), 200
            else:
                os.remove(csv_filename)  # Clean up even if sending fails
                return jsonify({"status": "error", "message": "Failed to send logs to Discord."}), 500
        except Exception as e:
            logger.error(f"Error in /urdone: {e}")
            return jsonify({"status": "error", "message": f"Failed to process request: {e}"}), 500
    return jsonify({"status": "error", "message": "Missing user_id or chat_logs_csv."}), 400

# Route to handle the /thepurge command
@app.route('/thepurge', methods=['POST'])
def thepurge():
    def shutdown():
        logger.info("Server is shutting down...")
        send_to_discord(message="Shutdown sequence initiated on the Roblox server.")
        os.kill(os.getpid(), signal.SIGINT)  # Gracefully terminate the server

    # Wait for 15 seconds before shutting down
    threading.Timer(15, shutdown).start()

    return jsonify({"status": "success", "message": "Shutdown sequence initiated."}), 200

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)  # Run on port 5000, accessible to Roblox
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
