# Tech Stack

## Backend
- **Language:** Python
- **Web Framework/Server:** Standard Python `http.server` or a lightweight framework (like Flask/FastAPI - TBD)
- **API:** HTTP/RESTful API for managing commands and state.
- **Real-time Communication:** WebSockets (for sending speech chunks to frontend).
- **Database:** SQLite3
- **Speech Recognition:** `speech_recognition` library
- **Keyboard/OS Interaction:** `pynput` library (or similar, e.g., `pyautogui`)

## Frontend
- **Structure:** Static HTML, CSS, JavaScript
- **HTML:** `public/index.html`
- **JavaScript:**
    - Framework: Alpine.js
    - Custom Logic: `public/main.js`, `public/js/*.js`
- **CSS:**
    - Framework: DaisyUI
- **Dependency Management:** Use CDNs for external libraries (Alpine.js, DaisyUI).
- **Build Process:** None (no bundlers or build tools).

## Serving
- The Python backend application will serve the static frontend files from a `public` directory.
