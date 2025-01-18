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
def send_to_discord(file_path):
    if DISCORD_WEBHOOK:
        try:
            # Prepare the payload with the file attachment
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'text/csv')}
                response = requests.post(DISCORD_WEBHOOK, files=files)

            # Log the status code and response text
            logger.info(f"Discord Webhook Response: {response.status_code} - {response.text}")

            # Check if the file was successfully sent (status code 204 for successful upload)
            if response.status_code == 204:
                return True
            else:
                logger.error(f"Failed to send file to Discord: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error while sending file to Discord: {e}")
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
    # Perform a shutdown action (for demonstration, you can adjust as per your server setup)
    shutdown_message = "Shutdown sequence initiated on the Roblox server."
    if send_to_discord(shutdown_message):
        return jsonify({"status": "success", "message": "Shutdown sequence initiated."}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to send shutdown message to Discord."}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)  # Run on port 5000, accessible to Roblox
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
