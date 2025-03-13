# 🌐 WebScope 4.0

## 🧠 What Makes WebScope Unique?

WebScope isn’t “just another browser automation tool.” It goes well beyond what tools like Selenium, Puppeteer, and Playwright provide out of the box.

Where others focus on *automating interactions*, **WebScope focuses on understanding and interpreting web login flows**.

### 🧩 What WebScope 3.0 Does:

- Scrapes live or JS-rendered pages using headless browsers
- Detects login forms and autofill-related fields (username, email, password)
- Analyzes form structure, visibility, labels, and logic
- Provides a user-friendly **web UI** and **REST API**
- Supports **multiple browser automation engines** as pluggable modules

> 🔍 None of the standard tools (Selenium, Puppeteer, etc.) offer login form *intelligence* out of the box — WebScope fills that gap.

---

## ⚙️ Features

- ✅ Heuristic-based login form detection
- ✅ Autofill field classification
- ✅ Supports static + JS-rendered pages
- ✅ Pluggable browser engines (Selenium Grid, Browserless, Puppeteer, Playwright)
- ✅ Flask API with optional HTML GUI
- ✅ Screenshot and HTML capture
- ✅ History logging (non-removable by design)
- ✅ Containerized, scalable microservice-ready architecture

---

## 🧱 Architecture

WebScope is designed with modular containers — each browser tool runs in isolation and communicates with WebScope through dedicated ports.

| Container         | Tool               | Port | Description                              |
|------------------|--------------------|------|------------------------------------------|
| `webscope`        | WebScope UI/API    | 5000 | Main Flask-based interface               |
| `selenium-hub`    | Selenium Grid Hub  | 4444 | Receives WebDriver commands              |
| `browserless`     | Headless Chrome    | 4445 | REST API to Chrome (Puppeteer-style)     |
| `puppeteer-api`   | Puppeteer Wrapper  | 4446 | Custom Node.js Express API               |
| `playwright-api`  | Playwright Wrapper | 4447 | Python or Node-based REST service        |

<img width="581" alt="Screenshot 2025-03-13 at 6 48 58 a m" src="https://github.com/user-attachments/assets/25d5fdc6-f68c-45ab-a69f-fb661e1c15a4" />

## Modern Alternatives You Could Add to WebScope 4.0

<img width="604" alt="Screenshot 2025-03-13 at 6 50 24 a m" src="https://github.com/user-attachments/assets/77bcbbe9-3082-4ee7-9a49-8223b54faba2" />


---

## 🚀 Use Cases

- Login flow analysis at scale
- UX auditing for authentication forms
- Building a dataset of form structures across the web
- Powering browser-based scraping pipelines
- API backend for autofill, form detection, or security tools

---

## 🧪 Example API Usage

```http
POST /analyze
Content-Type: application/json

{
  "url": "https://example.com/login",
  "tool": "puppeteer",  // selenium | browserless | playwright
  "mode": "comprehensive"
}
```

---

## 🛠 Roadmap Ideas

- Visual diffing of login flows across versions
- Full page screenshot support
- Accessibility auditing
- CAPTCHA detection
- Mobile view emulation
- Dashboard for session/task queue management

---

## 🤔 Why Not Just Use Selenium or Puppeteer?

Because none of them **understand forms** — they automate interactions, but they don’t:

- Know what field is a login vs. an email vs. hidden
- Log or analyze form structure over time
- Offer multi-tool routing behind a unified API
- Persist audit history or expose a real GUI

WebScope turns those raw tools into a **form intelligence engine**.

---

## 🔒 License

This project is provided for **personal, educational, and internal research use only**.

- ✅ You are allowed to run, explore, and build upon this project for non-commercial use.
- 🚫 **Commercial use (including SaaS platforms, resale, or derivative commercial products) is strictly prohibited** without **explicit written permission from the author**.

If you're interested in using WebScope in a commercial product or business context, please contact the creator to discuss licensing terms.

📬 Contact: jlima8900@hotmail.com

---

## ✨ Built by Joao Lima

Someone with a deep curiosity for browser automation, authentication flows, and web security tooling.
