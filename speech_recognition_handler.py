"""
Speech recognition module for voice command application.
"""
import time
import threading
import traceback
import speech_recognition as sr
import json
import os
import requests
from db import get_command_mappings, get_active_state, set_active_state, get_sentiment_commands
from input_simulation import execute_script

# Global flag for stopping the speech recognition thread
stop_listening = False
speech_thread = None
last_thread_health_check = 0
health_check_interval = 10  # seconds

# OpenAI API settings
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def update_openai_api_key(api_key):
    """Update the OpenAI API key."""
    global OPENAI_API_KEY
    OPENAI_API_KEY = api_key
    os.environ['OPENAI_API_KEY'] = api_key
    print(f"OpenAI API key updated: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else api_key}")
    return True

def check_phrase_match(text, command_phrases):
    """Check if the recognized text matches any command phrase."""
    if not text:
        return None, None
        
    text = text.lower()
    print(f"Checking for matches in text: '{text}'")
    print(f"Available commands: {list(command_phrases.keys())}")
    
    for phrase, script in command_phrases.items():
        phrase_lower = phrase.lower()
        if phrase_lower in text:
            print(f"MATCH FOUND: '{phrase_lower}' in '{text}'")
            return phrase, script
            
    print("No matches found.")
    return None, None

def check_sentiment_match(text, sentiment_commands):
    """Check if the text matches any sentiment-based command using ChatGPT."""
    if not text or not sentiment_commands:
        return None, None
    
    text = text.lower()
    print(f"Checking for sentiment matches in: '{text}'")
    
    # Check if the text starts with any of the defined prefixes
    for prefix, commands in sentiment_commands.items():
        if not prefix or not text.startswith(prefix.lower()):
            continue
            
        # If we have a prefix match, remove the prefix from the text
        remainder_text = text[len(prefix):].strip()
        print(f"Found prefix '{prefix}', analyzing: '{remainder_text}'")
        
        # If there's no text after the prefix, skip
        if not remainder_text:
            continue
            
        # If we only have one command for this prefix, just use it
        if len(commands) == 1:
            cmd = commands[0]
            print(f"Only one command with prefix '{prefix}', using it")
            return cmd['phrases'][0], cmd['script']
        
        # Format commands for the API
        formatted_commands = []
        for cmd in commands:
            cmd_phrases = ", ".join(cmd['phrases'])
            formatted_commands.append(f"Command: {cmd_phrases}")
        
        command_list = "\n".join(formatted_commands)
        
        # Use ChatGPT to determine the best match
        if not OPENAI_API_KEY:
            print("ERROR: OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
            return None, None
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            # Create the prompt for ChatGPT
            prompt = f"""
I have several voice commands with the prefix '{prefix}'. A user said: "{remainder_text}"

Available commands:
{command_list}

Which command best matches what the user said? Respond with ONLY the exact command text that matches best, nothing else. If there's no good match, respond with "NO_MATCH".
"""
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You determine which predefined command best matches a user's voice input. Respond only with the exact command text that matches best."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            print("Sending request to OpenAI API...")
            response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(data), timeout=5)
            response.raise_for_status()
            
            result = response.json()
            matched_phrase = result['choices'][0]['message']['content'].strip()
            
            print(f"ChatGPT suggested match: '{matched_phrase}'")
            
            # If no match was found, return None
            if matched_phrase == "NO_MATCH":
                return None, None
            
            # Find the command that matches the suggested phrase
            for cmd in commands:
                for phrase in cmd['phrases']:
                    # Remove the "Command: " prefix if it exists in the match
                    clean_match = matched_phrase
                    if clean_match.startswith("Command: "):
                        clean_match = clean_match[9:]
                        
                    if clean_match.lower() == phrase.lower():
                        print(f"Found matching command: '{phrase}'")
                        return phrase, cmd['script']
            
            print(f"Couldn't find a command that matches ChatGPT's suggestion: '{matched_phrase}'")
            return None, None
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            traceback.print_exc()
            return None, None
            
    print("No sentiment matches found.")
    return None, None

def speech_recognition_loop(socketio=None):
    """Main loop for speech recognition."""
    global stop_listening
    
    # Initialize recognizer
    r = sr.Recognizer()
    
    try:
        # Get microphone as source
        with sr.Microphone() as source:
            print("Calibrating for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=2)
            print("Voice command system active!")
            
            while not stop_listening:
                try:
                    # Check if we should still be listening
                    if not get_active_state():
                        print("Active state is false, stopping speech recognition loop.")
                        break
                    
                    print("Listening for commands...")
                    
                    # Listen for audio with a timeout
                    audio = r.listen(source, timeout=5)
                    
                    # Recognize speech
                    try:
                        text = r.recognize_google(audio)
                        print(f"Recognized: {text}")
                        
                        # Send recognized text to connected clients if socketio is provided
                        if socketio:
                            socketio.emit('speech_chunk', {'text': text})
                        
                        # Get the latest commands from the database
                        command_phrases = get_command_mappings()
                        
                        # First, check for exact matches
                        matched_phrase, script = check_phrase_match(text, command_phrases)
                        
                        # If no exact match, try sentiment matching
                        if not matched_phrase:
                            sentiment_commands = get_sentiment_commands()
                            if sentiment_commands:
                                matched_phrase, script = check_sentiment_match(text, sentiment_commands)
                        
                        # Execute the matched command if found
                        if matched_phrase:
                            print(f"Executing command for phrase: '{matched_phrase}'")
                            print(f"Script to execute: {script}")
                            execute_script(script)
                        else:
                            print("No matching command found for the recognized speech.")
                    
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                    except sr.RequestError as e:
                        print(f"Recognition service error: {e}")
                    except Exception as e:
                        print(f"Unexpected error in speech recognition: {e}")
                        traceback.print_exc()
                
                except Exception as e:
                    print(f"Error in speech recognition loop: {e}")
                    traceback.print_exc()
                    time.sleep(1)  # Prevent tight loop on recurring errors
    except Exception as e:
        print(f"Critical error in speech recognition thread: {e}")
        traceback.print_exc()

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
    global stop_listening
    
    stop_listening = True
    print("Speech recognition thread stopping.")
    return True

def restart_speech_recognition(socketio=None):
    """Restart the speech recognition thread."""
    stop_speech_recognition()
    time.sleep(1)  # Give the thread time to stop
    return start_speech_recognition(socketio) 