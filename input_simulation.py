"""
Input simulation module for executing keyboard scripts.
"""
import re
import time
import traceback
from pynput.keyboard import Key, Controller, KeyCode

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

def execute_script(script):
    """Execute a keyboard script."""
    print(f"Executing script: {script[:50]}...")
    
    if not script:
        print("WARNING: Empty script, nothing to execute")
        return
        
    lines = script.strip().split('\n')
    
    for line in lines:
        line = strip_comments(line)
        
        # Skip empty lines
        if not line:
            continue
        
        print(f"Processing command: {line}")
        
        try:
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
            print(f"ERROR executing line '{line}': {str(e)}")
            traceback.print_exc() 