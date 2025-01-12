from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from user_agents import parse
from dotenv import load_dotenv
import logging
import os
import requests

load_dotenv()
API_KEY = os.getenv("IPSTACK_API_KEY", "your_api_key_here")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracking.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

logging.basicConfig(filename='tracking.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)
    browser = db.Column(db.String(100))
    os = db.Column(db.String(100))
    device = db.Column(db.String(100))
    geolocation = db.Column(db.String(255))
    referrer = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, nullable=False)

# Function to fetch geolocation data using ipstack API
def get_geolocation(ip):
    """Fetch geolocation data based on the user's IP address using ipstack API."""
    if not ip or ip.startswith("192.168.") or ip.startswith("10.") or ip == "127.0.0.1":
        return "Private or Local Network"
    if not API_KEY or API_KEY == "your_api_key_here":
        logging.error("IPSTACK_API_KEY is missing or invalid")
        return "Unknown (API key missing)"
    try:
        response = requests.get(f"http://api.ipstack.com/{ip}?access_key={API_KEY}")
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown')
            region = data.get('region_name', 'Unknown')
            country = data.get('country_name', 'Unknown')
            isp = data.get('connection', {}).get('isp', 'Unknown')
            return f"{city}, {region}, {country}, ISP: {isp}"
        else:
            logging.error(f"Geolocation API error: {response.status_code}, {response.text}")
            return f"Error: {response.status_code}"
    except Exception as e:
        logging.error(f"Error in get_geolocation: {e}")
        return "Unknown"

@app.route('/favicon.ico')
def favicon():
    """Handle favicon.ico requests to avoid 404 errors."""
    return '', 204

@app.route('/track', methods=['GET'])
def track():
    """Handle tracking pixel requests and log user details to the database."""
    try:
        ip = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        referrer = request.referrer or 'Unknown'
        timestamp = datetime.now()

        geolocation = get_geolocation(ip)

        parsed_ua = parse(user_agent)
        browser = parsed_ua.browser.family or 'Unknown'
        os = parsed_ua.os.family or 'Unknown'
        device = parsed_ua.device.family or 'Unknown'

        new_entry = Tracking(
            ip=ip,
            browser=browser,
            os=os,
            device=device,
            geolocation=geolocation,
            referrer=referrer,
            user_agent=user_agent,
            timestamp=timestamp
        )
        db.session.add(new_entry)
        db.session.commit()

        return render_template("pixel.html"), 200

    except Exception as e:
        logging.error(f"Error in /track: {e}")
        return "Internal Server Error", 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)