from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import requests
from flask import Flask, request, render_template
from user_agents import parse

load_dotenv()
API_KEY = os.getenv("IPSTACK_API_KEY", "your_api_key_here")

app = Flask(__name__)

logging.basicConfig(filename='tracking.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def get_geolocation(ip):
    """Fetch geolocation data based on the user's IP address using ipstack API."""
    if ip == "127.0.0.1":
        return "Localhost (Development)"
    try:
        response = requests.get(f"http://api.ipstack.com/{ip}?access_key={API_KEY}")
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown')
            region = data.get('region_name', 'Unknown')
            country = data.get('country_name', 'Unknown')
            isp = data.get('connection', {}).get('isp', 'Unknown')  # Connection info may not always be available
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
    """Handle tracking pixel requests and log user details."""
    try:
        ip = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        referrer = request.referrer or 'Unknown'
        language = request.headers.get('Accept-Language', 'Unknown')
        encoding = request.headers.get('Accept-Encoding', 'Unknown')
        timestamp = datetime.now().isoformat()

        geolocation = get_geolocation(ip)

        parsed_ua = parse(user_agent)
        browser = parsed_ua.browser.family or 'Unknown'
        browser_version = parsed_ua.browser.version_string or 'Unknown'
        os = parsed_ua.os.family or 'Unknown'
        os_version = parsed_ua.os.version_string or 'Unknown'
        device = parsed_ua.device.family or 'Unknown'

        screen_size = request.args.get('screen', 'Unknown')
        timezone = request.args.get('timezone', 'Unknown')

        logging.info(
            f"IP: {ip}, Browser: {browser} {browser_version}, OS: {os} {os_version}, Device: {device}, "
            f"User-Agent: {user_agent}, Referrer: {referrer}, Language: {language}, Encoding: {encoding}, "
            f"Geolocation: {geolocation}, Screen Size: {screen_size}, Timezone: {timezone}, Timestamp: {timestamp}"
        )

        return render_template("pixel.html"), 200

    except Exception as e:
        logging.error(f"Error in /track: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True)