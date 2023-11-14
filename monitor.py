import requests
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template

# API details
apis = [
    {
        "name": "Astro AppInit",
        "url": "https://divine-partner.divinetalk.live/admin/v8/astroAppInit",
        "data": {
            "appCurrentVersion": "3.0",
            "device_brand": "samsung",
            "device_manufacture": "samsung",
            "device_model": "SM-A135F",
            "device_sdk_code": "33",
            "device_token": "",
            "role_id": ""
        }
    },
    {
        "name": "Astro IntroPageDesc",
        "url": "https://divine-partner.divinetalk.live/admin/v8/getIntroPageDesc",
        "data": None
    },
    {
        "name": "Cust AppInit",
        "url": "https://jarvis.divinetalk.live/api/v8/appInit",
        "data": {
            "appCurrentVersion": "3.2.9",
            "appInstanceId": "",
            "device_brand": "samsung",
            "device_manufacture": "samsung",
            "device_model": "SM-A135F",
            "device_sdk_code": "33",
            "device_token": ""
        },
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "Cust IntroPageDesc",
        "url": "https://jarvis.divinetalk.live/api/v8/getIntroPageDesc",
        "data": None
    }
]

# Function to make a POST request
def post_request(api_url, data=None, headers=None):
    try:
        response = requests.post(api_url, json=data, headers=headers)
        return {
            "status": response.status_code == 200,
            "timestamp": datetime.now().isoformat(),
            "response_time": response.elapsed.total_seconds(),
            "data": response.json()  # assuming the response is JSON
        }
    except requests.RequestException as e:
        return {
            "status": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Function to save the status to a file
def save_status(api_name, status_data):
    filename = f"{api_name}_status.json"
    with open(filename, "w") as file:
        json.dump(status_data, file)

# Scheduler setup
scheduler = BackgroundScheduler()

# Function to schedule checks
def scheduled_check(api_details):
    response = post_request(api_details['url'], data=api_details.get('data'), headers=api_details.get('headers'))
    save_status(api_details['name'], response)

# Scheduling the checks for each API endpoint
for api in apis:
    scheduler.add_job(scheduled_check, 'interval', minutes=5, args=[api])

scheduler.start()

# Flask app to retrieve status
app = Flask(__name__)

@app.route('/api/status/<api_name>')
def get_status(api_name):
    try:
        with open(f"{api_name}_status.json", "r") as file:
            status_data = json.load(file)
        return jsonify(status_data)
    except FileNotFoundError:
        return jsonify({"error": "Status file not found"}), 404

@app.route('/dashboard')
def dashboard():
    api_statuses = {}
    for api in apis:
        api_name = api['name']
        try:
            with open(f"{api_name}_status.json", "r") as file:
                api_status = json.load(file)
                # Assuming the 'status_code' is nested as indicated in the provided JSON structure
                status_code = api_status.get('data', {}).get('status_code', 'No status code')
                # print(f"Debug: {api_name} - Status Code: {status_code}, Type: {type(status_code)}")
                api_statuses[api_name] = api_status
        except FileNotFoundError:
            api_statuses[api_name] = {"error": "Status file not found"}

    return render_template('dashboard.html', api_statuses=api_statuses)  # Pass 'api_statuses', not 'api_status'

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
