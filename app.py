import os
import logging
import json
import yaml
import requests
import time
import undetected_chromedriver as uc
from flask import Flask, request, jsonify, render_template
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# VaultScope Branding
APP_NAME = "🔐 WebScope - Autofill Inspector"

# Load allowed IPs and Port from environment variables
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "0.0.0.0/0")
PORT = int(os.getenv("PORT", 9017))

app = Flask(__name__, template_folder="templates", static_folder="static")

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(f"{APP_NAME} is starting up... 🔍")

def detect_login_fields(driver):
    """Tries to detect login fields within the active frame."""
    autofill_data = {
        "username-field": "N/A",
        "password-field": "N/A",
        "totp-code-field": "N/A",
        "submit-button": "N/A"
    }

    logging.info("🔎 Scanning for login fields...")

    # Try detecting username field
    username_selectors = [
        "input[autocomplete='username']", "input[type='text'][name*='user']", "input[type='email']",
        "input[name='loginfmt']", "input[id*='user']", "input[name='login']", "input[name='email']",
        "input[id*='email']", "input[placeholder*='email']", "input[placeholder*='username']",
        "input[aria-label*='username']", "input[aria-label*='email']", "input[name='session[username_or_email]']",
        "input[id='identifierId']", "input[type='text'][id*='login']"
    ]
    for selector in username_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logging.info(f"✅ Found {len(elements)} username field(s) matching: {selector}")
            autofill_data["username-field"] = selector
            break

    # Try detecting password field
    password_selectors = [
        "input[autocomplete='current-password']", "input[type='password'][name*='pass']",
        "input[name='passwd']", "input[id*='pass']", "input[type='password']", "input[aria-label*='password']",
        "input[placeholder*='password']", "input[autocomplete='new-password']", "input[name='session[password]']",
        "input[type='password'][id*='login']", "input[id='Passwd']"
    ]
    for selector in password_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logging.info(f"✅ Found {len(elements)} password field(s) matching: {selector}")
            autofill_data["password-field"] = selector
            break

    # Try detecting TOTP field (2FA)
    totp_selectors = [
        "input[autocomplete='one-time-code']", "input[name*='otp']", "input[name*='totp']",
        "input[type='text'][id*='otp']", "input[placeholder*='one-time code']", "input[aria-label*='2fa']",
        "input[aria-label*='security code']", "input[type='text'][name*='twofactor']", "input[name='verification_code']"
    ]
    for selector in totp_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logging.info(f"✅ Found {len(elements)} TOTP field(s) matching: {selector}")
            autofill_data["totp-code-field"] = selector
            break

    # Try detecting submit button
    submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button[name='login'], button[id*='signin']")
    if submit_buttons:
        logging.info(f"✅ Found {len(submit_buttons)} submit button(s).")
        autofill_data["submit-button"] = "button[type='submit']"

    return autofill_data

def extract_autofill_parameters(url):
    """Use Selenium to dynamically analyze a page and extract autofill selectors."""

    driver = None  # Initialize driver
    autofill_data = {  # ✅ Ensure autofill_data is always initialized
        "page": url,
        "username-field": "N/A",
        "password-field": "N/A",
        "totp-code-field": "N/A",
        "submit-button": "N/A"
    }

    try:
        logging.info(f"Analyzing page: {url}")

        # Chrome options for better compatibility
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.get(url)

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        time.sleep(5)

        # Simulate User Interaction
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            ActionChains(driver).move_to_element(body).click().perform()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        except Exception as e:
            logging.warning(f"User interaction failed: {str(e)}")

        # Detect iframes and extract fields
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        logging.info(f"🔍 Found {len(iframes)} iframe(s) on the page.")

        if iframes:
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    logging.info("✅ Switched to iframe, trying field detection...")

                    iframe_autofill_data = detect_login_fields(driver)

                    if iframe_autofill_data["username-field"] != "N/A" or iframe_autofill_data["password-field"] != "N/A":
                        logging.info("🎯 Login fields found inside an iframe, using this data.")
                        autofill_data = iframe_autofill_data
                        break

                except Exception as e:
                    logging.warning(f"Error switching to iframe: {str(e)}")

            driver.switch_to.default_content()
            logging.info("🔙 Switched back to main page after iframe analysis.")

        # If no fields were found in iframes, try main page
        if autofill_data["username-field"] == "N/A" and autofill_data["password-field"] == "N/A":
            logging.info("🔍 No login fields detected in iframes, scanning main page...")
            autofill_data = detect_login_fields(driver)

        driver.save_screenshot("/app/screenshot.png")

        return autofill_data

    except Exception as e:
        logging.error(f"Error analyzing {url}: {str(e)}")
        return {"error": f"Failed to analyze {url}. Error: {str(e)}"}

    finally:
        if driver:
            driver.quit()

@app.route("/")
def home():
    return render_template("index.html")

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

@app.route("/interactive")
def interactive():
    return render_template("interactive.html")

if __name__ == '__main__':
    context = ('ssl/server.crt', 'ssl/server.key')
    app.run(debug=False, host='0.0.0.0', port=PORT, ssl_context=context)
