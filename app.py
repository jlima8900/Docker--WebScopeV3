import os
import logging
import json
import yaml
import requests
import time
import subprocess
import undetected_chromedriver as uc
from flask import Flask, request, jsonify, render_template, Response
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_socketio import SocketIO

# Initialize Flask and WebSockets
app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")  # ✅ Enable WebSockets

# WebScope Branding
APP_NAME = "🔍 WebScope 2.0 - Autofill Inspector"

# Load allowed IPs and Port from environment variables
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "0.0.0.0/0")
PORT = int(os.getenv("PORT", 9018))  # ✅ Ensure correct port

# ✅ Define log file inside the container
LOG_FILE = "/var/log/webscope.log"

# ✅ Logging Configuration (Writes logs to both file and console)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # ✅ Logs to file
        logging.StreamHandler()         # ✅ Logs to console
    ]
)

logging.info(f"{APP_NAME} is starting up... 🔍")


### ✅ Login Field Detection

def detect_login_fields(driver):
    """Detects username, password, TOTP (2FA), and submit buttons."""
    autofill_data = {
        "username-field": "N/A",
        "password-field": "N/A",
        "totp-code-field": "N/A",
        "submit-button": "N/A"
    }

    logging.info("🔎 Scanning for login fields...")

    # Log total number of input fields on the page
    all_elements = driver.find_elements(By.CSS_SELECTOR, "input, button")
    logging.info(f"🔍 Found {len(all_elements)} total form elements.")

    # ✅ Detect username fields
    username_selectors = [
        "input[autocomplete='username']", "input[type='text'][name*='user']",
        "input[type='email']", "input[name='loginfmt']", "input[id*='user']",
        "input[name='login']", "input[name='email']", "input[id*='email']",
        "input[placeholder*='email']", "input[placeholder*='username']",
        "input[aria-label*='username']", "input[aria-label*='email']",
        "input[name='session[username_or_email]']", "input[id='identifierId']",
        "input[type='text'][id*='login']"
    ]
    for selector in username_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logging.info(f"✅ Found {len(elements)} username field(s): {selector}")
            autofill_data["username-field"] = selector
            break

    # ✅ Detect password fields
    password_selectors = [
        "input[autocomplete='current-password']", "input[type='password'][name*='pass']",
        "input[name='passwd']", "input[id*='pass']", "input[type='password']",
        "input[aria-label*='password']", "input[placeholder*='password']",
        "input[autocomplete='new-password']", "input[name='session[password]']",
        "input[type='password'][id*='login']", "input[id='Passwd']"
    ]
    for selector in password_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logging.info(f"✅ Found {len(elements)} password field(s): {selector}")
            autofill_data["password-field"] = selector
            break

    # ✅ Detect TOTP/2FA fields
    totp_selectors = [
        "input[autocomplete='one-time-code']", "input[name*='otp']", "input[name*='totp']",
        "input[type='text'][id*='otp']", "input[placeholder*='one-time code']",
        "input[aria-label*='2fa']", "input[aria-label*='security code']",
        "input[type='text'][name*='twofactor']", "input[name='verification_code']"
    ]
    for selector in totp_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logging.info(f"✅ Found {len(elements)} TOTP/2FA field(s): {selector}")
            autofill_data["totp-code-field"] = selector
            break

    # ✅ Detect submit buttons
    submit_selectors = [
        "button[type='submit']", "input[type='submit']", "button[name='login']", "button[id*='signin']"
    ]
    for selector in submit_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logging.info(f"✅ Found {len(elements)} submit button(s): {selector}")
            autofill_data["submit-button"] = selector
            break

    return autofill_data

### ✅ Extract Autofill Parameters
def extract_autofill_parameters(url):
    """Uses Selenium to analyze login fields dynamically."""
    autofill_data = {
        "page": url,
        "username-field": "N/A",
        "password-field": "N/A",
        "totp-code-field": "N/A",
        "submit-button": "N/A"
    }

    try:
        logging.info(f"Analyzing page: {url}")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        autofill_data.update(detect_login_fields(driver))

    except Exception as e:
        logging.error(f"Error analyzing {url}: {str(e)}")

    return autofill_data


### ✅ Analyze Route

@app.route("/analyze", methods=["POST"])
def analyze():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    autofill_data = extract_autofill_parameters(url)

    response_data = {
        "json": json.dumps([autofill_data], indent=4),
        "yaml": yaml.dump([autofill_data], default_flow_style=False)
    }

    return jsonify(response_data)


### ✅ Flask Routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/logs")
def logs():
    return render_template("log.html")

@app.route("/stream-logs")
def stream_logs():
    """Streams logs from a log file instead of Docker."""
    def generate_logs():
        with open(LOG_FILE, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                yield f"data: {line}\n\n"

    return Response(generate_logs(), mimetype="text/event-stream")


if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    context = ('ssl/server.crt', 'ssl/server.key')
    socketio.run(app, debug=False, host='0.0.0.0', port=PORT, ssl_context=context, server='eventlet')
