"""
Speech recognition module for voice command application.
"""
import time
import threading
import traceback
import json
import os
import requests
from db import get_command_mappings, get_active_state, set_active_state, increment_openai_request_count, get_commands, get_global_shortcut_key, get_ai_timeout_settings
from input_simulation import execute_script
from speech_recognizer import SpeechRecognizer

# Global flag for stopping the speech recognition thread
stop_listening = False
speech_thread = None
last_thread_health_check = 0
health_check_interval = 10  # seconds

# Command debounce tracking
last_command_time = 0
last_command_phrase = None
COMMAND_DEBOUNCE_TIME = 2.0  # seconds

# Sentiment mode flag (toggled by shortcut key)
sentiment_mode_active = False

# AI mode timeout variables
ai_timeout_timer = None
ai_timeout_end_time = None

# Scripts execution flag (controls whether scripts are executed)
scripts_enabled = True

# OpenAI API settings
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Global speech recognizer instance
speech_recognizer = None

def update_openai_api_key(api_key):
    """Update the OpenAI API key."""
    global OPENAI_API_KEY
    OPENAI_API_KEY = api_key
    os.environ['OPENAI_API_KEY'] = api_key
    print(f"OpenAI API key updated: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else api_key}")
    return True

def toggle_sentiment_mode(socketio=None):
    """Toggle the sentiment mode flag."""
    global sentiment_mode_active, ai_timeout_timer, ai_timeout_end_time
    
    # Cancel any existing timeout timer
    if ai_timeout_timer is not None:
        ai_timeout_timer.cancel()
        ai_timeout_timer = None
        ai_timeout_end_time = None
    
    # Toggle the mode
    sentiment_mode_active = not sentiment_mode_active
    print(f"Sentiment mode {'activated' if sentiment_mode_active else 'deactivated'}")
    
    # If turning on and timeout is enabled, start the timer
    if sentiment_mode_active:
        timeout_settings = get_ai_timeout_settings()
        if timeout_settings['enabled']:
            start_ai_timeout(timeout_settings['seconds'], socketio)
    
    return sentiment_mode_active

def start_ai_timeout(seconds, socketio=None):
    """Start the AI mode timeout timer."""
    global ai_timeout_timer, ai_timeout_end_time
    
    # Cancel any existing timer
    if ai_timeout_timer is not None:
        ai_timeout_timer.cancel()
    
    print(f"Starting AI mode timeout for {seconds} seconds")
    
    # Set the end time for UI display
    ai_timeout_end_time = time.time() + seconds
    
    # Create a timer to turn off AI mode after timeout
    ai_timeout_timer = threading.Timer(seconds, ai_timeout_callback, args=[socketio])
    ai_timeout_timer.daemon = True
    ai_timeout_timer.start()
    
    # If socketio is provided, emit the timeout start
    if socketio:
        socketio.emit('ai_timeout', {
            'active': True,
            'endTime': ai_timeout_end_time,
            'remainingSeconds': seconds
        })
    
    return True

def ai_timeout_callback(socketio=None):
    """Called when the AI mode timeout expires."""
    global sentiment_mode_active, ai_timeout_timer, ai_timeout_end_time
    
    print("AI mode timeout expired, turning off sentiment mode")
    
    # Turn off sentiment mode
    sentiment_mode_active = False
    ai_timeout_timer = None
    ai_timeout_end_time = None
    
    # Notify frontend if socketio is available
    if socketio:
        socketio.emit('sentiment_mode', {'active': False})
        socketio.emit('ai_timeout', {'active': False})
        socketio.emit('system_message', {
            'type': 'info',
            'message': 'AI mode was automatically deactivated due to timeout'
        })
    
    return True

def get_sentiment_mode_state():
    """Get the current state of the sentiment mode."""
    return sentiment_mode_active

def get_ai_timeout_state():
    """Get the current state of the AI timeout timer."""
    global ai_timeout_end_time
    
    if ai_timeout_end_time is None:
        return {
            'active': False,
            'remainingSeconds': 0
        }
    
    remaining_seconds = max(0, int(ai_timeout_end_time - time.time()))
    
    return {
        'active': remaining_seconds > 0,
        'endTime': ai_timeout_end_time,
        'remainingSeconds': remaining_seconds
    }

def toggle_scripts_execution():
    """Toggle whether scripts are executed."""
    global scripts_enabled
    scripts_enabled = not scripts_enabled
    print(f"Script execution {'enabled' if scripts_enabled else 'disabled'}")
    return scripts_enabled

def get_scripts_execution_state():
    """Get the current state of script execution."""
    return scripts_enabled

def check_exact_match(text, command_phrases):
    """Check if the recognized text exactly matches any command phrase."""
    if not text:
        return None, None, None
        
    text = text.lower()
    print(f"Checking for exact matches in text: '{text}'")
    print(f"Available commands: {list(command_phrases.keys())}")
    
    for phrase, script in command_phrases.items():
        phrase_lower = phrase.lower()
        if phrase_lower in text:
            print(f"EXACT MATCH FOUND: '{phrase_lower}' in '{text}'")
            
            # Find command ID by phrase
            command_id = None
            for cmd in get_commands():
                if phrase in cmd['phrases']:
                    command_id = cmd['id']
                    break
                    
            return command_id, phrase, script
            
    print("No exact matches found.")
    return None, None, None

def check_partial_match(text, commands):
    """Check if the recognized text contains any phrases from commands with partial matching enabled."""
    if not text:
        return None, None, None
        
    text = text.lower()
    print(f"Checking for partial matches in text: '{text}'")
    
    # Filter commands with partial matching enabled
    partial_match_commands = [cmd for cmd in commands if cmd['partial_match']]
    
    if not partial_match_commands:
        print("No commands with partial matching enabled.")
        return None, None, None
    
    for cmd in partial_match_commands:
        for phrase in cmd['phrases']:
            phrase_lower = phrase.lower()
            if phrase_lower in text:
                print(f"PARTIAL MATCH FOUND: '{phrase_lower}' in '{text}'")
                return cmd['id'], phrase, cmd['script']
    
    print("No partial matches found.")
    return None, None, None

def validate_openai_settings():
    """Validate that OpenAI API key is set for sentiment analysis."""
    if not OPENAI_API_KEY:
        print("ERROR: OpenAI API key not set. Cannot use sentiment mode.")
        return False
    return True

def process_sentiment_analysis(text, socketio=None):
    """Process speech using sentiment analysis with OpenAI to determine the best command to execute."""
    if not text:
        return None, None, None
    
    if not validate_openai_settings():
        if socketio:
            socketio.emit('system_message', 
                        {'type': 'error', 
                         'message': 'OpenAI API key not set. Cannot use sentiment mode.'})
        return None, None, None
    
    # Get commands with sentiment analysis enabled
    sentiment_commands = get_commands()
    sentiment_commands = [cmd for cmd in sentiment_commands if cmd['understand_sentiment']]
    
    if not sentiment_commands:
        print("No commands with sentiment analysis enabled.")
        return None, None, None
    
    # Format commands for the API
    formatted_commands = []
    for cmd in sentiment_commands:
        cmd_phrases = ", ".join(cmd['phrases'])
        formatted_commands.append(f"Command: {cmd_phrases} => Script: {cmd['script']}")
    
    command_list = "\n".join(formatted_commands)
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Create the prompt for ChatGPT
        prompt = f"""
I have several voice commands configured with sentiment analysis. A user said: "{text}"

Available commands:
{command_list}

Which command best matches what the user said? Respond with ONLY the exact command text (one of the phrases) that matches best, nothing else. If there's no good match, respond with "NO_MATCH".
"""
        
        data = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": "You determine which predefined command best matches a user's voice input. Respond only with the exact command text that matches best."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        print("Sending request to OpenAI API for sentiment analysis...")
        response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(data), timeout=5)
        response.raise_for_status()
        
        # Increment the OpenAI request count
        increment_openai_request_count()
        
        result = response.json()
        matched_phrase = result['choices'][0]['message']['content'].strip()
        
        print(f"ChatGPT suggested match for sentiment analysis: '{matched_phrase}'")
        
        # If no match was found, return None
        if matched_phrase == "NO_MATCH":
            return None, None, None
        
        # Find the command that matches the suggested phrase
        for cmd in sentiment_commands:
            for phrase in cmd['phrases']:
                # Remove the "Command: " prefix if it exists in the match
                clean_match = matched_phrase
                if clean_match.startswith("Command: "):
                    clean_match = clean_match[9:]
                    
                if clean_match.lower() == phrase.lower():
                    print(f"Found matching command in sentiment analysis: '{phrase}'")
                    return cmd['id'], phrase, cmd['script']
        
        print(f"Couldn't find a command that matches ChatGPT's suggestion in sentiment analysis: '{matched_phrase}'")
        return None, None, None
        
    except Exception as e:
        print(f"Error calling OpenAI API in sentiment analysis: {e}")
        traceback.print_exc()
        return None, None, None

def process_speech_input(text, socketio=None):
    """Process speech input and determine the appropriate command to execute.
    
    The matching priority is:
    1. Exact phrase matches (always checked)
    2. Partial phrase matches (if enabled for the command)
    3. AI sentiment analysis (only if sentiment mode is active)
    """
    if not text:
        return None, None, None
        
    print(f"Processing speech input: '{text}'")
    
    # Get all commands
    all_commands = get_commands()
    
    # Get phrase to script mappings for exact matching
    command_phrases = get_command_mappings()
    
    # 1. Always check for exact matches first
    command_id, matched_phrase, script = check_exact_match(text, command_phrases)
    if matched_phrase and script:
        print(f"Using exact match: '{matched_phrase}'")
        return command_id, matched_phrase, script
    
    # 2. Check for partial matches if no exact match found
    command_id, matched_phrase, script = check_partial_match(text, all_commands)
    if matched_phrase and script:
        print(f"Using partial match: '{matched_phrase}'")
        return command_id, matched_phrase, script
    
    # 3. Use sentiment analysis only if sentiment mode is active
    if sentiment_mode_active:
        print("No exact or partial matches found. Using AI sentiment analysis...")
        if socketio:
            socketio.emit('sentiment_mode', {'active': True})
        
        # Only use sentiment analysis if key is valid
        if validate_openai_settings():
            command_id, matched_phrase, script = process_sentiment_analysis(text, socketio)
            if matched_phrase and script:
                print(f"Using AI sentiment match: '{matched_phrase}'")
                return command_id, matched_phrase, script
    
    return None, None, None

def should_execute_command(phrase):
    """Check if we should execute this command based on debounce rules."""
    global last_command_time, last_command_phrase
    
    current_time = time.time()
    
    # If it's the same command and within the debounce time, don't execute
    if phrase == last_command_phrase and current_time - last_command_time < COMMAND_DEBOUNCE_TIME:
        print(f"Debouncing command '{phrase}' - too soon after last execution")
        return False
    
    # Update the last command time and phrase
    last_command_time = current_time
    last_command_phrase = phrase
    return True

def can_execute_script(script):
    """Check if a script can be executed based on the scripts_enabled flag.
    
    Special case: If scripts are disabled but the script contains scripts_on(),
    we still allow it to execute so scripts can be re-enabled.
    """
    global scripts_enabled
    
    # Always allow execution if scripts are enabled
    if scripts_enabled:
        return True
    
    # If scripts are disabled, only allow if it contains scripts_on()
    return "scripts_on()" in script

def speech_recognition_loop(socketio=None):
    """Main loop for speech recognition."""
    global stop_listening, speech_recognizer
    
    # Initialize speech recognizer if not already initialized
    if speech_recognizer is None:
        speech_recognizer = SpeechRecognizer(
            energy_threshold=300,
            dynamic_energy_threshold=False,
            dynamic_energy_adjustment_damping=0.15,
            dynamic_energy_ratio=1.5,
            pause_threshold=0.1,
            phrase_threshold=0.2,
            non_speaking_duration=0.1,
            operation_timeout=None
        )
    
    print("Speech recognizer initialized")
    
    # Calibrate for ambient noise
    if not speech_recognizer.calibrate(duration=2):
        print("Failed to calibrate speech recognizer")
        return
    
    print("Voice command system active!")
    
    try:
        # Define callback for continuous recognition
        def handle_speech_text(text):
            nonlocal socketio
            
            if not text:
                return
                
            print(f"Recognized: {text}")
            
            # Send recognized text to connected clients if socketio is provided
            if socketio:
                socketio.emit('speech_chunk', {'text': text})
            
            # Process the speech input
            command_id, matched_phrase, script = process_speech_input(text, socketio)
            
            # Execute the matched command if found
            if matched_phrase and script:
                # Check if we should execute this command (debounce)
                if should_execute_command(matched_phrase):
                    print(f"Executing command for phrase: '{matched_phrase}'")
                    print(f"Script to execute: {script}")
                    
                    # Notify clients that a command was triggered
                    if socketio and command_id:
                        socketio.emit('command_triggered', {
                            'command_id': command_id,
                            'phrase': matched_phrase
                        })
                    
                    # Check if this script can be executed based on scripts_enabled flag
                    if can_execute_script(script):
                        # Execute the script
                        execute_script(script, socketio=socketio)
                    else:
                        print("Script execution is disabled. Skipping execution.")
                        if socketio:
                            socketio.emit('system_message', {
                                'type': 'warning',
                                'message': 'Script execution is disabled. Use scripts_on() to re-enable.'
                            })
                else:
                    print(f"Skipping execution of '{matched_phrase}' due to debounce rules")
        
        # Start continuous recognition
        speech_recognizer.start_continuous_recognition(handle_speech_text)
        
        # Wait until stop_listening is set to True
        while not stop_listening:
            # Check if we should still be listening
            if not get_active_state():
                print("Active state is false, stopping speech recognition loop.")
                break
            
            time.sleep(1)  # Check every second
            
        # Stop continuous recognition
        speech_recognizer.stop_continuous_recognition()
        
    except Exception as e:
        print(f"Critical error in speech recognition thread: {e}")
        traceback.print_exc()
        time.sleep(1)

def check_thread_health(socketio=None):
    """Check if speech recognition thread is healthy and restart if needed."""
    global speech_thread, last_thread_health_check, stop_listening
    
    # Only check periodically to avoid overhead
    current_time = time.time()
    if current_time - last_thread_health_check < health_check_interval:
        return
    
    last_thread_health_check = current_time
    
    # If the system is supposed to be active but thread is not running, restart it
    if get_active_state():
        if speech_thread is None or not speech_thread.is_alive():
            print("WARNING: Speech recognition thread is not running but should be active. Restarting...")
            stop_listening = False
            start_speech_recognition(socketio)
            # Notify the frontend that recovery was needed
            if socketio:
                socketio.emit('system_message', 
                              {'type': 'warning', 
                               'message': 'Speech recognition was restarted due to unexpected termination.'})

def start_speech_recognition(socketio=None):
    """Start speech recognition in a background thread."""
    global speech_thread, stop_listening
    print("Starting speech recognition thread")
    # First, stop any existing thread
    if speech_thread is not None and speech_thread.is_alive():
        print("Stopping existing speech recognition thread.")
        stop_listening = True
        speech_thread.join(timeout=2)
    
    # Then start a new thread
    stop_listening = False
    speech_thread = threading.Thread(target=speech_recognition_loop, args=(socketio,))
    speech_thread.daemon = True
    speech_thread.start()
    print("Speech recognition thread started.")
    
    # Start thread health checker
    health_checker = threading.Thread(target=health_checker_loop, args=(socketio,))
    health_checker.daemon = True
    health_checker.start()
    
    return True

def health_checker_loop(socketio=None):
    """Continuously check the health of the speech recognition thread."""
    while True:
        check_thread_health(socketio)
        time.sleep(5)  # Check every 5 seconds

def stop_speech_recognition():
    """Stop the speech recognition thread."""
    global stop_listening, speech_recognizer
    
    stop_listening = True
    
    # If speech_recognizer exists, stop continuous recognition
    if speech_recognizer:
        speech_recognizer.stop_continuous_recognition()
    
    print("Speech recognition thread stopping.")
    return True

def restart_speech_recognition(socketio=None):
    """Restart the speech recognition thread."""
    stop_speech_recognition()
    time.sleep(1)  # Give the thread time to stop
    return start_speech_recognition(socketio) 