#!/usr/bin/env python3
"""
Voice Command Application

A web application that listens to voice commands and executes keyboard actions.
"""
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO

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
    # Initialize the database
    db.init_db()
    
    # Check if active state is true, and start speech recognition if needed
    if db.get_active_state():
        print("Active state is true at startup, starting speech recognition...")
        start_speech_recognition(socketio)
        print("Speech recognition started.")
    else:
        print("Active state is false at startup, speech recognition not started.")

# Main entry point
if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Start the Flask application with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 