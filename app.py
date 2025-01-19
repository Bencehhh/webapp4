import os
import logging
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from flask_cors import CORS

# Load the environment variables from .env file
load_dotenv()

DISCORD_WEBHOOK = os.getenv('DISCORD_RELAY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

if not DISCORD_WEBHOOK:
    logger.critical("Discord Webhook URL is not set in the environment variables.")
    raise ValueError("Discord Webhook URL is required for this application to work.")

# Funkció: Fájl küldése Discord Webhookon keresztül
def send_to_discord(content=None, file_path=None):
    try:
        if file_path:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'text/csv')}
                response = requests.post(DISCORD_WEBHOOK, files=files)
        else:
            response = requests.post(DISCORD_WEBHOOK, json={"content": content})

        if response.status_code == 204:
            logger.info("Message succesfully sent.")
            return True
        else:
            logger.error(f"Unable to send message: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"Error while sending request: {e}")
    return False

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get("command", "").lower()
    user_id = data.get("user_id")
    chat_logs_csv = data.get("chat_logs_csv")

    if command == "howdy":
        if user_id and chat_logs_csv:
            csv_filename = f"chat_logs_{user_id}.csv"
            try:
                with open(csv_filename, 'w') as f:
                    f.write(chat_logs_csv)

                if send_to_discord(file_path=csv_filename):
                    os.remove(csv_filename)
                    return jsonify({"status": "success", "message": "Fetching data is successful."}), 200
                else:
                    os.remove(csv_filename)
                    return jsonify({"status": "error", "message": "Unable to fetch data."}), 500
            except Exception as e:
                logger.exception(f"Problem found during executing the 'Howdy' command: {e}")
                return jsonify({"status": "error", "message": "Serverside issues."}), 500
        else:
            return jsonify({"status": "error", "message": "Lack of data: user_id or chat_logs_csv."}), 400
    elif command == "bye bye":
        if send_to_discord(content="Server shutdown triggered"):
            return jsonify({"status": "success", "message": "Server shutdown success."}), 200
        else:
            return jsonify({"status": "error", "message": "Message can not be sent."}), 500
    else:
        return jsonify({"status": "error", "message": "Unknown command."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)