# Voice Command System

A web application that listens to voice commands and executes corresponding keyboard actions. Perfect for controlling games like Digital Combat Simulator (DCS) through voice.

## Features

- Voice command recognition using your system's default microphone
- Customizable keyboard scripts for each voice command
- Web interface for managing commands and monitoring speech recognition
- Toggle activation on/off through the web interface

## Requirements

- Python 3.7+
- A microphone connected to your computer
- Web browser

## Setup

1. Clone this repository

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. Use the web interface to add voice commands and their corresponding keyboard scripts.
2. Toggle the "Listening" button to activate voice recognition.
3. Speak your command, and the system will execute the corresponding keyboard script.

## Project Structure

The application is organized into modular components:

- `app.py` - Main entry point for the application 
- `db.py` - Database operations
- `api.py` - API routes and endpoints
- `speech_recognition_handler.py` - Speech recognition functionality
- `input_simulation.py` - Keyboard scripting and execution
- `public/` - Frontend static files
  - `index.html` - Main web interface
  - `js/main.js` - Alpine.js functionality

## Input Simulation Options

The application defaults to using `pynput` for keyboard simulation, but you can alternatively use `pyautogui` by:

1. Editing `requirements.txt` to uncomment the pyautogui dependency
2. Installing it with `pip install pyautogui` 
3. Modifying `input_simulation.py` accordingly

Both libraries can handle the same keyboard operations but offer different features:

- **pynput**: Lower-level with direct keyboard control, works well with background applications
- **pyautogui**: Higher-level with additional functions for mouse control and screen analysis

## Keyboard Script Syntax

Scripts use a simple syntax to define keyboard actions:

- **Comments:**
  - Lines starting with `--` are ignored.
  - Text after `#` on any line is ignored.

- **Delays:**
  - `100ms` - Wait 100 milliseconds
  - `2s` - Wait 2 seconds

- **Typing:**
  - `type "Hello World"` - Types the text "Hello World"

- **Key Combinations:**
  - `ctrl+c` - Press Ctrl+C
  - `shift+f10` - Press Shift+F10
  - `win+r` - Press Windows+R (opens Run dialog)

- **Single Keys:**
  - `enter` - Press Enter key
  - `escape` - Press Escape key
  - `f5` - Press F5 key

## Example Scripts

```
-- Open Notepad and type text
win+r              # Open run dialog
500ms              # Wait for dialog
type "notepad"     # Type notepad
500ms
enter              # Press enter to open notepad
1s                 # Wait for notepad to open
type "Hello, world!" # Type text into notepad
```

```
-- Save a file
ctrl+s             # Press save hotkey
500ms              # Wait half a second
type "filename.txt" # Type the filename
enter              # Press enter
```

## Troubleshooting

- **Microphone not working:** Make sure your default microphone is working and correctly set up in your operating system.
- **Speech recognition errors:** Make sure you have an active internet connection for the speech recognition service.
- **Keyboard commands not working in some applications:** Some applications may require elevated privileges to receive simulated keyboard input.

## License

MIT 