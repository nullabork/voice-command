#!/usr/bin/env python3
"""
Voice Command Application

A web application that listens to voice commands and executes keyboard actions.
"""
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import sys

# Import app modules
import db
from api import api_bp
from speech_recognition_handler import start_speech_recognition, stop_speech_recognition, speech_recognition_loop
from input_simulation import execute_script

# Initialize Flask application
app = Flask(__name__, static_folder='public')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register the API blueprint
app.register_blueprint(api_bp)

# Store socketio as a global in the app context
app.config['socketio'] = socketio

# Flag to track if we've already initialized speech recognition
speech_recognition_initialized = False

# Store socketio in the app config for use in API routes
@app.before_request
def before_request():
    request.environ['socketio'] = socketio

# WebSocket for real-time speech recognition updates
@socketio.on('connect')
def handle_connect():
    print('Client connected to WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from WebSocket')

# Add WebSocket route for testing scripts
@socketio.on('test_script')
def handle_test_script(data):
    print(f'Testing script: {data["script"]}')
    try:
        execute_script(data['script'])
        socketio.emit('script_result', {'success': True, 'message': 'Script executed successfully'})
    except Exception as e:
        print(f'Error executing script: {str(e)}')
        socketio.emit('script_result', {'success': False, 'message': f'Error: {str(e)}'})

def initialize_app():
    """Initialize the application components."""
    global speech_recognition_initialized
    
    # Initialize the database
    db.init_db()
    
    # Load OpenAI API key from the database
    openai_api_key = db.get_openai_api_key()
    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key
        print(f"OpenAI API key loaded from database: {'*' * (len(openai_api_key) - 4) + openai_api_key[-4:] if len(openai_api_key) > 4 else openai_api_key}")
    else:
        print("WARNING: OpenAI API key not set. Sentiment analysis feature will not work.")
        print("You can set the OpenAI API key in the settings.")
    
    # In debug mode, Werkzeug loads the app twice - once for the reloader and once for the app
    # We only want to start speech recognition in the app instance (when WERKZEUG_RUN_MAIN is set)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true' and app.debug:
        print("Skipping speech recognition start in reloader process")
        return
    
    # Check if active state is true, and start speech recognition if needed
    if db.get_active_state():
        print("Active state is true at startup, starting speech recognition...")
        start_speech_recognition(socketio)
        speech_recognition_initialized = True
        print("Speech recognition started.")
    else:
        print("Active state is false at startup, speech recognition not started.")

# Main entry point
if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Start the Flask application with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False) 