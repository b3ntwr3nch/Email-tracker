from flask import Flask, request, render_template
import logging
from datetime import datetime
import requests
from user_agents import parse

app = Flask(__name__)

logging.basicConfig(filename='tracking.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def get_geolocation(ip):
    """Fetch geolocation data based on the user's IP address using an external API."""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        if response.status_code == 200:
            data = response.json()
            return f"{data['city']}, {data['regionName']}, {data['country']}, ISP: {data['isp']}"
    except Exception as e:
        return 'Unknown'

@app.route('/track', methods=['GET'])
def track():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    referrer = request.referrer
    language = request.headers.get('Accept-Language')
    encoding = request.headers.get('Accept-Encoding')
    timestamp = datetime.now().isoformat()

    geolocation = get_geolocation(ip)

    parsed_ua = parse(user_agent)
    browser = parsed_ua.browser.family
    browser_version = parsed_ua.browser.version_string
    os = parsed_ua.os.family
    os_version = parsed_ua.os.version_string
    device = parsed_ua.device.family

    screen_size = request.args.get('screen', 'Unknown')
    timezone = request.args.get('timezone', 'Unknown')

    logging.info(
        f"IP: {ip}, Browser: {browser} {browser_version}, OS: {os} {os_version}, Device: {device}, "
        f"User-Agent: {user_agent}, Referrer: {referrer}, Language: {language}, Encoding: {encoding}, "
        f"Geolocation: {geolocation}, Screen Size: {screen_size}, Timezone: {timezone}, Timestamp: {timestamp}"
    )

    return render_template("pixel.html"), 200

if __name__ == '__main__':
    app.run(debug=True)