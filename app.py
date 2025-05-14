#!/usr/bin/env python3
"""
Voice Command Application

A web application that listens to voice commands and executes keyboard actions.
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import sys
import traceback
import threading
import time

# Import app modules
import db
from api import api_bp
from speech_recognition_handler import start_speech_recognition, stop_speech_recognition, update_openai_api_key, toggle_sentiment_mode, get_sentiment_mode_state, get_ai_timeout_state, toggle_scripts_execution, get_scripts_execution_state
from input_simulation import execute_script

# Initialize Flask application
app = Flask(__name__, 
            static_folder='public',
            template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register the API blueprint
app.register_blueprint(api_bp)

# Store socketio as a global in the app context
app.config['socketio'] = socketio

# Flag to track if we've already initialized speech recognition
speech_recognition_initialized = False

# Flag to track if the AI timeout update thread is running
ai_timeout_update_thread_running = False

# Store socketio in the app config for use in API routes
@app.before_request
def before_request():
    request.environ['socketio'] = socketio

def initialize_app():
    """Initialize the application."""
    # Initialize database
    db.init_db()
    
    # Update OpenAI API key from database
    api_key = db.get_openai_api_key()
    if api_key:
        update_openai_api_key(api_key)
    
    # Start AI timeout update thread
    start_ai_timeout_update_thread()
    
    print("Application initialized.")

    global speech_recognition_initialized
    if db.get_active_state() and not speech_recognition_initialized:
        print("Starting speech recognition on socket connection...")
        speech_recognition_initialized = True
        start_speech_recognition(socketio)

def ai_timeout_update_loop():
    """Background thread that sends regular AI timeout updates to clients."""
    global ai_timeout_update_thread_running
    
    try:
        while ai_timeout_update_thread_running:
            # Get current timeout state
            timeout_state = get_ai_timeout_state()
            
            # If timeout is active, send update to all clients
            if timeout_state['active']:
                socketio.emit('ai_timeout_update', timeout_state)
            
            # Sleep for a short time to avoid excessive updates
            time.sleep(0.5)
    except Exception as e:
        print(f"Error in AI timeout update thread: {str(e)}")
        traceback.print_exc()

def start_ai_timeout_update_thread():
    """Start the AI timeout update thread."""
    global ai_timeout_update_thread_running
    
    # Set the flag to keep the thread running
    ai_timeout_update_thread_running = True
    
    # Start the thread
    timeout_thread = threading.Thread(target=ai_timeout_update_loop)
    timeout_thread.daemon = True
    timeout_thread.start()
    
    print("AI timeout update thread started")

@socketio.on('connect')
def handle_connect():
    print('Client connected to WebSocket')
    
    # If the app should be active, start speech recognition
    
    
    # Send current AI timeout state to the newly connected client
    socketio.emit('ai_timeout_update', get_ai_timeout_state(), room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from WebSocket')

# Add WebSocket route for testing scripts
@socketio.on('test_script')
def handle_test_script(data):
    print(f'Testing script: {data["script"]}')
    try:
        # Execute in preview mode to get result message without actual key presses
        result = execute_script(data['script'], preview_mode=True, socketio=socketio)
        socketio.emit('script_result', {
            'success': True, 
            'message': result if result else 'Script preview successful'
        })
    except Exception as e:
        print(f'Error executing script: {str(e)}')
        socketio.emit('script_result', {'success': False, 'message': f'Error: {str(e)}'})

@socketio.on('toggle_sentiment_mode')
def handle_toggle_sentiment_mode():
    try:
        # Pass socketio to toggle_sentiment_mode for timeout notifications
        active = toggle_sentiment_mode(socketio)
        print(f'Sentiment mode toggled via WebSocket: {"active" if active else "inactive"}')
        socketio.emit('sentiment_mode', {'active': active})
        socketio.emit('script_result', {'success': True, 'message': f'Sentiment mode {"activated" if active else "deactivated"}'})
    except Exception as e:
        print(f'Error toggling sentiment mode: {str(e)}')
        socketio.emit('script_result', {'success': False, 'message': f'Error: {str(e)}'})

@socketio.on('toggle_scripts_execution')
def handle_toggle_scripts_execution():
    try:
        # Toggle script execution state
        active = toggle_scripts_execution()
        print(f'Script execution toggled via WebSocket: {"enabled" if active else "disabled"}')
        socketio.emit('scripts_execution', {'active': active})
        socketio.emit('script_result', {'success': True, 'message': f'Script execution {"enabled" if active else "disabled"}'})
    except Exception as e:
        print(f'Error toggling script execution: {str(e)}')
        socketio.emit('script_result', {'success': False, 'message': f'Error: {str(e)}'})

# Global error handler for API routes
@app.errorhandler(Exception)
def handle_error(e):
    print(f'Global API error: {str(e)}')
    return jsonify({
        'error': str(e),
        'stack_trace': traceback.format_exc()
    }), 500

# Main entry point
if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Start the Flask application with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False) 