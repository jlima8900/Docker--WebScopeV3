# 🔐 WebScope 2.0 - Autofill Inspector

**WebScope** is a tool for dynamically analyzing web login pages and extracting autofill selectors. This project expands upon the original concept by **Eric Manilloff**, introducing major **security, performance, and usability improvements**.

---

## 🚀 Key Enhancements Over the Original

| **Feature** | **Original Script** | **Improved Version** |
|------------|-----------------|-----------------|
| **Browser Evasion** | Used standard Selenium WebDriver | Uses **`undetected_chromedriver` (uc.Chrome)** to bypass bot detection |
| **Headless Mode** | Required additional flags for headless execution | Seamlessly integrated in **`undetected_chromedriver`** |
| **Better Input Field Detection** | Only basic username/password detection | Uses **JavaScript execution** to extract visible input fields |
| **Handles Iframes** | No iframe handling | **Detects and switches to iframes** dynamically |
| **Form Interactions** | Did not interact with the page | **Simulates clicks & scrolling** to trigger dynamic content |
| **Two-Factor Authentication (TOTP) Field Detection** | Did not detect OTP fields | **Detects TOTP fields** commonly used for 2FA |
| **Submit Button Detection** | Limited | **Expanded selector coverage** for submit buttons |
| **Output Formats** | JSON only | **Supports both JSON & YAML outputs** |
| **Secure HTTPS Interface** | No HTTPS support | **Uses self-signed SSL certificate** for secure connections |
| **Logging & Debugging** | Minimal logs | **Enhanced logging & debugging** with step-by-step analysis |
| **Docker Integration** | No containerized setup | **Full Docker support** with a lightweight container |
| **Deployment Options** | Only manual setup | **Supports both Docker & local Python environments** |
| **Python Dependency Management** | No virtual environment setup | **Uses `requirements.txt` and containerized `pip install`** |
| **Performance & Stability** | Occasional timeouts on slow sites | **Handles timeouts, retries, and failures gracefully** |
| **Error Handling** | Minimal error handling | **Catches WebDriver errors, network issues, and bot detection blocks** |
| **Automatic Screenshots** | No visual debugging | **Saves screenshots (`screenshot.png`) for troubleshooting** |

---

## 🔍 Detailed Explanation of Improvements

### 1️⃣ Using `undetected_chromedriver` to Bypass Bot Detection
- The **original script** used the standard Selenium **`webdriver.Chrome()`**, which is often detected and blocked by websites.
- The **improved version** now uses **`undetected_chromedriver`** (`uc.Chrome()`), making it **less likely to be blocked** by login pages.

---

### 2️⃣ Enhanced Form Field Detection
- **Runs JavaScript** to extract **all visible input fields**, including:
  - **Username fields** (`input[autocomplete='username']`)
  - **Password fields** (`input[autocomplete='current-password']`)
  - **TOTP (2FA) fields** (`input[name*='otp']`)
  - **Submit buttons** (`button[type='submit']`)
- **Dynamically updates selectors** instead of using static lists.

---

### 3️⃣ Handling Login Forms Inside Iframes
- **Detects and switches to iframes** automatically.
- Supports **nested iframes** (e.g., Microsoft Login, Google OAuth).
- **Logs iframe detection** (`Found X iframes on the page`).

---

### 4️⃣ Simulating User Interaction (Scrolling & Clicking)
- **Simulates user interactions** to trigger login forms that appear dynamically:
  - **Clicks on the body element**.
  - **Scrolls to the bottom** of the page.
  - **Waits for additional elements to load**.

---

### 5️⃣ Improved Output Formats (JSON + YAML)
- Supports **both JSON & YAML formats** for better readability:
  ```json
  {
      "page": "https://example.com",
      "username-field": "input[name='user']",
      "password-field": "input[name='pass']",
      "totp-code-field": "input[name='otp']",
      "submit-button": "button[type='submit']"
  }
  ```
  ```yaml
  - page: https://example.com
    username-field: input[name='user']
    password-field: input[name='pass']
    totp-code-field: input[name='otp']
    submit-button: button[type='submit']
  ```

---

### 6️⃣ Secure HTTPS Interface with a Self-Signed SSL Certificate
- Uses **HTTPS (`https://localhost:9017`)** with a **self-signed SSL certificate**.
- **Certificate is auto-generated** in the `/ssl/` directory.

---

### 7️⃣ Better Error Handling & Logging
- **Detailed logging** (every step is logged).
- **Graceful handling** of:
  - **Bot detection blocks**.
  - **Timeouts & network failures**.
  - **WebDriver crashes**.

---

### 8️⃣ Docker Support for Easy Deployment
- **Runs fully inside Docker** with:
  - Pre-installed **Chrome, undetected_chromedriver, and Selenium**.
  - **One-liner setup** with `docker-compose up -d --build`.

---

## 🔮 Future Improvements
- 🔹 **Add database storage** for extracted autofill data.
- 🔹 **Enhance bot evasion** (randomized user-agents, fingerprint spoofing).
- 🔹 **Extend TOTP detection** for non-standard 2FA implementations.
- 🔹 **Improve UI for displaying results** (graphical visualization).
- 🔹 **Enable bulk URL scanning** for security researchers.

---

## 🔥 Summary of All Upgrades
✅ **Bypasses bot detection** using `undetected_chromedriver`.  
✅ **Detects iframes** and switches automatically.  
✅ **Simulates scrolling & clicks** to trigger hidden login forms.  
✅ **Extracts username, password, and TOTP fields dynamically**.  
✅ **Saves screenshots** for debugging login page rendering.  
✅ **Improved error handling & logging** for stability.  
✅ **Supports JSON & YAML output formats**.  
✅ **Runs securely over HTTPS** with a **self-signed SSL certificate**.  
✅ **Containerized with Docker** for easy deployment.  


---

This **documented upgrade history** ensures that **all previous features** are **retained and improved** while introducing **major performance & security enhancements**. 🚀
