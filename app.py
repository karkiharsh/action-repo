
from flask import Flask, request, jsonify
import pymongo
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["github_events"]
collection = db["events"]

# Create a webhook endpoint to receive GitHub events
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if 'pusher' in data:
        event_type = "Push"
        author = data['pusher']['name']
        branch = data['ref'].split('/')[-1]
        timestamp = datetime.now().strftime("%d %B %Y - %I:%M %p UTC")
        message = f"{author} pushed to {branch} on {timestamp}"

    elif 'pull_request' in data:
        event_type = "Pull Request"
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.now().strftime("%d %B %Y - %I:%M %p UTC")
        message = f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"

    else:
        return jsonify({"message": "Event type not supported"}), 400

    # Save event to MongoDB
    collection.insert_one({
        "event_type": event_type,
        "message": message,
        "timestamp": timestamp
    })

    return jsonify({"message": "Event received and stored"}), 200

# Run the Flask server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
