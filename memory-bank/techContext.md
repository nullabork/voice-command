# Technical Context

## Programming Languages & Frameworks
- **Primary Language**: Python 3.7+
- **Web Framework**: Flask 2.3.3
- **Frontend**: HTML, CSS, JavaScript
- **Frontend Framework**: Alpine.js for reactivity
- **CSS Framework**: Tailwind CSS with DaisyUI components
- **Real-time Communication**: Flask-SocketIO 5.3.6 / Socket.IO

## Core Libraries & Dependencies
### Backend
- **Speech Recognition**: SpeechRecognition 3.10.0
- **Keyboard Simulation**: pynput 1.7.6 (primary) / pyautogui (alternative)
- **Cross-Origin Support**: Flask-Cors 4.0.0
- **Audio Processing**: pyaudio 0.2.13
- **HTTP Requests**: requests 2.31.0
- **Environment Management**: python-dotenv

### Frontend
- All frontend libraries are loaded via CDN (no build process)
- Alpine.js for reactive UI components
- Tailwind CSS for styling
- DaisyUI for pre-built UI components
- Socket.IO client for real-time communication

## Database
- **Type**: SQLite3 (embedded)
- **Schema**:
  - Commands table (id, name, script)
  - Phrases table (id, command_id, phrase_text)
  - Settings table (key, value)
- **Access Pattern**: Direct Python DB-API with connection pooling

## Development Environment
- **Source Control**: Git
- **Dependency Management**: pip with requirements.txt
- **Testing**: Manual testing (no automated tests yet)
- **Deployment**: Local installation with Python interpreter

## System Requirements
- **Operating System**: Windows 10+ / Linux / macOS
- **Hardware**: Microphone
- **Browser Support**: Modern browsers (Chrome, Firefox, Edge, Safari)
- **Python Version**: 3.7 or higher

## File Structure
```
/
├── app.py                   # Main application entry point
├── api.py                   # API endpoints and routes
├── db.py                    # Database operations
├── speech_recognition_handler.py # Speech processing
├── input_simulation.py      # Keyboard control
├── requirements.txt         # Python dependencies
├── voicecommand.db          # SQLite database
├── public/                  # Frontend files
│   ├── index.html           # Main HTML interface
│   ├── js/
│   │   └── main.js          # Frontend JavaScript
│   └── css/                 # (No custom CSS files, uses CDN)
└── memory-bank/             # Documentation
```

## Technical Constraints
- Speech recognition requires internet for Google's API
- Keyboard simulation might require elevated privileges in some applications
- Performance depends on system microphone quality
- Background noise can affect recognition accuracy

## Technical Decisions
- **SQLite vs. Other Databases**: Chosen for simplicity and zero-config setup
- **Flask vs. Django**: Flask chosen for lightweight, minimal approach
- **WebSockets vs. Polling**: WebSockets for real-time updates without overhead
- **pynput vs. pyautogui**: pynput preferred for lower-level keyboard control
- **Alpine.js vs. React/Vue**: Alpine.js chosen for simplicity without build process

## Extensibility Considerations
- Input simulation can be extended to support mouse actions
- Speech recognition provider could be swapped (e.g., to local models)
- Database could be migrated to a client-server model for multi-user support
- UI could be extended with more analytics and visualization tools 