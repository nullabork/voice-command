"""
Input simulation module for executing keyboard scripts.
"""
import re
import time
import traceback
from pynput.keyboard import Key, Controller, KeyCode

# Remove the circular import from here
# Will import inside the functions that need it

# Initialize keyboard controller
keyboard = Controller()

# Debug flag - set to True for verbose logging
DEBUG = True

def strip_comments(line):
    """Strip comments from a line of script."""
    # Remove line comments (starting with --)
    if line.startswith('--'):
        return ''
    
    # Remove inline comments (after #)
    if '#' in line:
        line = line.split('#', 1)[0]
    
    return line.strip()

def parse_key(key_name):
    """Parse key name into pynput key object."""
    # Special keys mapping
    special_keys = {
        'enter': Key.enter,
        'space': Key.space,
        'tab': Key.tab,
        'escape': Key.esc,
        'esc': Key.esc,
        'backspace': Key.backspace,
        'delete': Key.delete,
        'shift': Key.shift,
        'ctrl': Key.ctrl,
        'control': Key.ctrl,
        'alt': Key.alt,
        'win': Key.cmd,
        'windows': Key.cmd,
        'cmd': Key.cmd,
        'command': Key.cmd,
        'up': Key.up,
        'down': Key.down,
        'left': Key.left,
        'right': Key.right,
        'home': Key.home,
        'end': Key.end,
        'page_up': Key.page_up,
        'page_down': Key.page_down,
        'f1': Key.f1,
        'f2': Key.f2,
        'f3': Key.f3,
        'f4': Key.f4,
        'f5': Key.f5,
        'f6': Key.f6,
        'f7': Key.f7,
        'f8': Key.f8,
        'f9': Key.f9,
        'f10': Key.f10,
        'f11': Key.f11,
        'f12': Key.f12,
    }
    
    # Return the corresponding key object
    if key_name.lower() in special_keys:
        if DEBUG:
            print(f"Using special key: {key_name} -> {special_keys[key_name.lower()]}")
        return special_keys[key_name.lower()]
    
    # For single character keys
    if len(key_name) == 1:
        if DEBUG:
            print(f"Using character key: {key_name}")
        return key_name
    
    # If not recognized, log warning and try as a regular character
    print(f"WARNING: Unrecognized key '{key_name}', treating as regular text")
    return key_name

def press_and_release(key):
    """Press and release a key with proper delay."""
    try:
        if DEBUG:
            print(f"Pressing key: {key}")
        keyboard.press(key)
        time.sleep(0.05)  # Small delay to ensure key is registered
        keyboard.release(key)
        time.sleep(0.05)  # Small delay after release
    except Exception as e:
        print(f"ERROR pressing key {key}: {str(e)}")
        traceback.print_exc()

def press_key_combination(keys):
    """Press a combination of keys."""
    pressed_keys = []
    try:
        # Press all keys in sequence
        for key in keys:
            if DEBUG:
                print(f"Pressing key in combination: {key}")
            keyboard.press(key)
            pressed_keys.append(key)
            time.sleep(0.05)  # Small delay between key presses
        
        # Small delay for key combination to register
        time.sleep(0.1)
        
        # Release all keys in reverse order
        for key in reversed(pressed_keys):
            if DEBUG:
                print(f"Releasing key in combination: {key}")
            keyboard.release(key)
            time.sleep(0.05)  # Small delay between key releases
    except Exception as e:
        # In case of error, release any pressed keys
        print(f"ERROR in key combination: {str(e)}")
        traceback.print_exc()
        for key in reversed(pressed_keys):
            try:
                keyboard.release(key)
            except:
                pass

def handle_special_function(function_name, args=None, socketio=None):
    """Handle special function calls in scripts."""
    # Import here to avoid circular import
    from speech_recognition_handler import toggle_sentiment_mode, get_sentiment_mode_state, toggle_scripts_execution, get_scripts_execution_state
    
    function_name = function_name.lower()
    
    if function_name == 'sentiment_on':
        # Turn on sentiment mode if not already on
        if not get_sentiment_mode_state():
            print("Turning sentiment mode ON")
            toggle_sentiment_mode()
            
            # Notify frontend if socketio is available
            if socketio:
                socketio.emit('sentiment_mode', {'active': True})
                socketio.emit('script_result', {
                    'success': True, 
                    'message': 'Sentiment mode activated'
                })
            return True
        else:
            print("Sentiment mode is already ON")
            return True
    
    elif function_name == 'sentiment_off':
        # Turn off sentiment mode if not already off
        if get_sentiment_mode_state():
            print("Turning sentiment mode OFF")
            toggle_sentiment_mode()
            
            # Notify frontend if socketio is available
            if socketio:
                socketio.emit('sentiment_mode', {'active': False})
                socketio.emit('script_result', {
                    'success': True, 
                    'message': 'Sentiment mode deactivated'
                })
            return True
        else:
            print("Sentiment mode is already OFF")
            return True
    
    elif function_name == 'scripts_on':
        # Turn on script execution if not already on
        if not get_scripts_execution_state():
            print("Enabling script execution")
            toggle_scripts_execution()
            
            # Notify frontend if socketio is available
            if socketio:
                socketio.emit('scripts_execution', {'active': True})
                socketio.emit('script_result', {
                    'success': True, 
                    'message': 'Script execution enabled'
                })
            return True
        else:
            print("Script execution is already enabled")
            return True
    
    elif function_name == 'scripts_off':
        # Turn off script execution if not already off
        if get_scripts_execution_state():
            print("Disabling script execution")
            toggle_scripts_execution()
            
            # Notify frontend if socketio is available
            if socketio:
                socketio.emit('scripts_execution', {'active': False})
                socketio.emit('script_result', {
                    'success': True, 
                    'message': 'Script execution disabled'
                })
            return True
        else:
            print("Script execution is already disabled")
            return True
    
    # Add more special functions here as needed
    
    return False  # Function not handled

def execute_script(script, preview_mode=False, socketio=None):
    """Execute a keyboard script.
    
    Args:
        script: The script to execute
        preview_mode: If True, only simulate execution for preview
        socketio: The SocketIO instance for sending updates to the frontend
    """
    print(f"Executing script: {script[:50]}...")
    
    if not script:
        print("WARNING: Empty script, nothing to execute")
        return
        
    lines = script.strip().split('\n')
    result_messages = []
    
    for line in lines:
        line = strip_comments(line)
        
        # Skip empty lines
        if not line:
            continue
        
        print(f"Processing command: {line}")
        result_messages.append(f"Command: {line}")
        
        try:
            # Handle function calls - like sentiment_on() or sentiment_off()
            function_match = re.match(r'(\w+)\(\)', line)
            if function_match:
                function_name = function_match.group(1)
                print(f"Found function call: {function_name}()")
                
                if handle_special_function(function_name, socketio=socketio):
                    result_messages.append(f"Executed function: {function_name}()")
                    continue
                else:
                    print(f"Unknown function: {function_name}()")
                    result_messages.append(f"WARNING: Unknown function: {function_name}()")
                    continue
            
            # Skip actual keyboard input if in preview mode
            if preview_mode:
                result_messages.append("Preview mode - not actually executing")
                continue
            
            # Handle delay lines
            if line.endswith('ms'):
                delay_match = re.match(r'(\d+)ms', line)
                if delay_match:
                    delay = int(delay_match.group(1)) / 1000  # Convert ms to seconds
                    print(f"Waiting for {delay} seconds")
                    time.sleep(delay)
                    continue
            
            if line.endswith('s'):
                delay_match = re.match(r'(\d+)s', line)
                if delay_match:
                    delay = int(delay_match.group(1))
                    print(f"Waiting for {delay} seconds")
                    time.sleep(delay)
                    continue
            
            # Handle typing lines
            type_match = re.match(r'type\s+"([^"]*)"', line)
            if type_match:
                text = type_match.group(1)
                print(f"Typing text: {text}")
                keyboard.type(text)
                # Add a small delay after typing
                time.sleep(0.2)
                continue
            
            # Handle key combinations
            if '+' in line:
                print(f"Executing key combination: {line}")
                keys = line.split('+')
                parsed_keys = [parse_key(k.strip()) for k in keys]
                press_key_combination(parsed_keys)
                continue
            
            # Handle single key presses
            key = parse_key(line)
            print(f"Pressing single key: {line}")
            press_and_release(key)
            
        except Exception as e:
            error_msg = f"ERROR executing line '{line}': {str(e)}"
            print(error_msg)
            traceback.print_exc()
            result_messages.append(error_msg)
    
    # Return results for preview
    if preview_mode:
        return "\n".join(result_messages) 