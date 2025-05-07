# Voice Command System

A web application that listens to voice commands and executes corresponding keyboard actions. Perfect for controlling games like Digital Combat Simulator (DCS) through voice.

## Features

- Voice command recognition using your system's default microphone
- Customizable keyboard scripts for each voice command
- Web interface for managing commands and monitoring speech recognition
- Toggle activation on/off through the web interface
- **AI Sentiment Analysis Mode**: Use OpenAI to understand voice commands by intent rather than exact matching
- **Partial Matching**: Trigger commands when phrases appear anywhere in speech, not just exact matches
- **Script Execution Control**: Enable/disable script execution while still listening for commands
- **AI Mode Timeout**: Automatically turn off AI mode after a specified period to save API usage

## Requirements

- Python 3.7+
- A microphone connected to your computer
- Web browser
- OpenAI API key (for AI Sentiment Analysis feature)

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

## Compiling to Executable

### Local Compilation

You can compile the application into a standalone executable using PyInstaller:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Compile the application:
   ```
   pyinstaller --onefile --add-data "public;public" --icon=public/favicon.ico --name VoiceCommand app.py
   ```
   
   Or use the included build script:
   ```
   build.bat
   ```

3. The executable will be created in the `dist` folder

### GitHub Actions Release

This repository includes a GitHub Action workflow that can build and release the application:

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Build and Release" workflow
3. Click "Run workflow"
4. Enter the version number (e.g., v1.0.0) and release notes
5. Click "Run workflow" to start the build process
6. Once complete, the executables for Windows, Linux, and macOS will be available in the "Releases" section of the repository

### Requirements for the Executable

The compiled executable:
- Requires no Python installation on the target machine
- Needs internet connection for speech recognition and OpenAI features
- Needs a working microphone
- May need administrator privileges to simulate keyboard input in some applications

#### Platform-Specific Notes

- **Windows**: 
  - May require running as administrator for keyboard simulation in some applications
  - Compatible with Windows 10/11

- **Linux**:
  - Requires PortAudio and PyAudio dependencies (installed automatically in the build)
  - May require `libxcb-xinerama0` for GUI display (`sudo apt-get install libxcb-xinerama0`)
  - Needs appropriate permissions for microphone access

- **macOS**:
  - May require allowing microphone access in System Preferences/Settings
  - May need to approve the app in Security & Privacy settings
  - On newer versions, you might need to remove the quarantine attribute with: `xattr -d com.apple.quarantine /path/to/VoiceCommand`

## Usage

1. Use the web interface to add voice commands and their corresponding keyboard scripts.
2. Toggle the "Listening" button to activate voice recognition.
3. Speak your command, and the system will execute the corresponding keyboard script.

### Command Matching Modes

The system offers three ways to match your voice to commands:

1. **Exact Match**: Your phrase must appear exactly in what you say (always active)
2. **Partial Match**: Enable this per command to match if phrase appears anywhere in speech
3. **AI Mode**: Uses OpenAI to understand command intent even with different phrasing

When using AI Mode, your phrases should be treated as descriptions of what the command does, rather than exact text to match. This helps the AI better understand the intent of your command.

### Special Functions

You can control system features from within scripts:

- `sentiment_on()`: Activate AI mode
- `sentiment_off()`: Deactivate AI mode
- `scripts_on()`: Enable script execution
- `scripts_off()`: Disable script execution

Note: Even when scripts are disabled, a script containing `scripts_on()` will still execute.

## Project Structure

The application is organized into modular components:

- `app.py` - Main entry point for the application 
- `db.py` - Database operations
- `api.py` - API routes and endpoints
- `speech_recognition_handler.py` - Speech recognition functionality
- `input_simulation.py` - Keyboard scripting and execution
- `speech_recognizer.py` - Speech recognition interface
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

- **Special Functions:**
  - `sentiment_on()` - Activate AI mode
  - `sentiment_off()` - Deactivate AI mode
  - `scripts_on()` - Enable script execution
  - `scripts_off()` - Disable script execution

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
-- Save a file and disable scripts
ctrl+s             # Press save hotkey
500ms              # Wait half a second
type "filename.txt" # Type the filename
enter              # Press enter
1s                 # Wait for save to complete
scripts_off()      # Disable script execution for safety
```

## Troubleshooting

- **Microphone not working:** Make sure your default microphone is working and correctly set up in your operating system.
- **Speech recognition errors:** Make sure you have an active internet connection for the speech recognition service.
- **Keyboard commands not working in some applications:** Some applications may require elevated privileges to receive simulated keyboard input.
- **AI Mode not working:** Ensure you have set your OpenAI API key in the settings.
- **Script execution not working:** Check if scripts are enabled using the "Scripts On/Off" toggle.

## License

MIT 