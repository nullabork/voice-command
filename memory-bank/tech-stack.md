# Tech Stack

## Backend
- **Language:** Python
- **Web Framework:** Flask
- **API:** RESTful API through Flask endpoints for managing commands and state.
- **Real-time Communication:** Flask-SocketIO for bidirectional real-time events
- **Database:** SQLite3
- **Speech Recognition:** `speech_recognition` library with Google's API
- **Keyboard/OS Interaction:** `pynput` library for keyboard input simulation
- **Thread Management:** Python's `threading` module for concurrent processing

## Frontend
- **Structure:** Static HTML, CSS, JavaScript
- **HTML:** `public/index.html`
- **JavaScript:**
    - Framework: Alpine.js for reactive UI
    - WebSockets: Socket.IO client for real-time updates
    - Custom Logic: `public/js/main.js`
- **CSS & UI:**
    - Framework: Tailwind CSS via CDN
    - Component Library: DaisyUI for pre-styled components
    - Responsive design for multiple device sizes
- **Dependency Management:** External libraries loaded via CDNs.
- **Build Process:** None (no bundlers or build tools).

## Architecture
- **Modular Design:** Codebase is split into modules:
  - `app.py` - Main application entry point
  - `api.py` - API endpoints and routing
  - `db.py` - Database operations
  - `speech_recognition_handler.py` - Speech processing
  - `input_simulation.py` - Keyboard control
- **Serving:** The Flask application serves the static frontend files from a `public` directory.
- **Communication:**
  - RESTful API for CRUD operations on commands
  - WebSockets for real-time updates and script testing
- **State Management:**
  - Server state stored in SQLite database
  - Client state managed by Alpine.js
- **Error Handling & Recovery:**
  - Automatic restart of speech recognition threads
  - Toast notifications for user feedback
  - Detailed error logging
