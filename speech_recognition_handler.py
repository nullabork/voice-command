"""
Speech recognition module for voice command application.
"""
import time
import threading
import traceback
import speech_recognition as sr
from db import get_command_mappings, get_active_state, set_active_state
from input_simulation import execute_script

# Global flag for stopping the speech recognition thread
stop_listening = False
speech_thread = None
last_thread_health_check = 0
health_check_interval = 10  # seconds

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
                        
                        # Check if text matches any command phrases
                        matched_phrase, script = check_phrase_match(text, command_phrases)
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