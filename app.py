from flask import Flask, request, render_template
import logging
from datetime import datetime
import requests
from user_agents import parse

app = Flask(__name__)

logging.basicConfig(filename='tracking.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def get_geolocation(ip):
    """Fetch geolocation data based on the user's IP address using an external API."""
    if ip == "127.0.0.1":
        return "Localhost (Development)"
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('city', 'Unknown')}, {data.get('regionName', 'Unknown')}, {data.get('country', 'Unknown')}, ISP: {data.get('isp', 'Unknown')}"
    except Exception as e:
        return 'Unknown'

@app.route('/favicon.ico')
def favicon():
    return '', 204
@app.route('/track', methods=['GET'])
def track():
    try:
        # Basic Request Details
        ip = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        referrer = request.referrer or 'Unknown'
        language = request.headers.get('Accept-Language', 'Unknown')
        encoding = request.headers.get('Accept-Encoding', 'Unknown')
        timestamp = datetime.now().isoformat()

        # Geolocation
        geolocation = get_geolocation(ip)

        # Parse User-Agent
        parsed_ua = parse(user_agent)
        browser = parsed_ua.browser.family or 'Unknown'
        browser_version = parsed_ua.browser.version_string or 'Unknown'
        os = parsed_ua.os.family or 'Unknown'
        os_version = parsed_ua.os.version_string or 'Unknown'
        device = parsed_ua.device.family or 'Unknown'

        # Query Parameters
        screen_size = request.args.get('screen', 'Unknown')
        timezone = request.args.get('timezone', 'Unknown')

        # Log the Collected Information
        logging.info(
            f"IP: {ip}, Browser: {browser} {browser_version}, OS: {os} {os_version}, Device: {device}, "
            f"User-Agent: {user_agent}, Referrer: {referrer}, Language: {language}, Encoding: {encoding}, "
            f"Geolocation: {geolocation}, Screen Size: {screen_size}, Timezone: {timezone}, Timestamp: {timestamp}"
        )

        # Return a Tracking Pixel
        return render_template("pixel.html"), 200

    except Exception as e:
        logging.error(f"Error in /track: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True)