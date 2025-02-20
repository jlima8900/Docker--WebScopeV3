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

# VaultScope Branding
APP_NAME = "🔐 VaultScope - Autofill Inspector"

# Load allowed IPs and Port from environment variables
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "0.0.0.0/0")
PORT = int(os.getenv("PORT", 9017))

app = Flask(__name__, template_folder="templates", static_folder="static")

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(f"{APP_NAME} is starting up... 🔍")

def extract_autofill_parameters(url):
    """Use Selenium to dynamically analyze a page and extract autofill selectors."""
    
    driver = None  # Initialize driver to avoid `referenced before assignment` error
    
    try:
        logging.info(f"Analyzing page: {url}")

        # Chrome options for better compatibility
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")  # ✅ Ignore SSL certificate errors
        options.add_argument("--allow-insecure-localhost")  # ✅ Accept self-signed certs
        
        # Use undetected ChromeDriver to avoid bot detection
        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.get(url)

        time.sleep(7)  # Ensure JavaScript executes

        # Simulate User Interaction to Trigger Login Form
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            ActionChains(driver).move_to_element(body).click().perform()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait after interaction
        except Exception as e:
            logging.warning(f"User interaction failed: {str(e)}")

        # Detect if page has iframes (Common for login forms)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        logging.info(f"🔍 Found {len(iframes)} iframe(s) on the page.")

        # Switch to iframe if necessary
        if iframes:
            try:
                driver.switch_to.frame(iframes[0])
                logging.info("✅ Switched to first iframe.")

                nested_iframes = driver.find_elements(By.TAG_NAME, "iframe")
                logging.info(f"🔍 Found {len(nested_iframes)} nested iframe(s).")

                if nested_iframes:
                    driver.switch_to.frame(nested_iframes[0])
                    logging.info("✅ Switched to nested iframe.")
            except Exception as e:
                logging.warning(f"Error switching iframes: {str(e)}")

        # Structure to store detected autofill fields
        autofill_data = {
            "page": url,
            "username-field": "N/A",
            "password-field": "N/A",
            "totp-code-field": "N/A",
            "submit-button": "N/A"
        }

        # Find username field
        username_selectors = [
            "input[autocomplete='username']", "input[type='text'][name*='user']",
            "input[type='email']", "input[name='loginfmt']", "input[id*='user']"
        ]
        for selector in username_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                autofill_data["username-field"] = selector
                break

        # Find password field
        password_selectors = [
            "input[autocomplete='current-password']", "input[type='password'][name*='pass']",
            "input[name='passwd']", "input[id*='pass']"
        ]
        for selector in password_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                autofill_data["password-field"] = selector
                break

        # Find TOTP field (2FA)
        totp_selectors = [
            "input[autocomplete='one-time-code']", "input[name*='otp']", "input[name*='totp']",
            "input[type='text'][id*='otp']"
        ]
        for selector in totp_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                autofill_data["totp-code-field"] = selector
                break

        # Detect submit button
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if submit_buttons:
            autofill_data["submit-button"] = "button[type='submit']"

        # Save a screenshot for debugging
        driver.save_screenshot("/app/screenshot.png")
        logging.info("📸 Screenshot saved as /app/screenshot.png")

        return autofill_data

    except Exception as e:
        logging.error(f"Error analyzing {url}: {str(e)}")
        return {"error": f"Failed to analyze {url}. Error: {str(e)}"}

    finally:
        if driver:
            driver.quit()

# Flask Routes
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

if __name__ == '__main__':
    context = ('ssl/server.crt', 'ssl/server.key')  # Self-signed cert
    app.run(debug=False, host='0.0.0.0', port=PORT, ssl_context=context)
