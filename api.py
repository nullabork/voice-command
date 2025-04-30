"""
API routes module for voice command application.
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
import db
from speech_recognition_handler import start_speech_recognition, stop_speech_recognition

# Create the API blueprint
api_bp = Blueprint('api', __name__)

# Routes for serving static files
@api_bp.route('/')
def index():
    return send_from_directory('public', 'index.html')

@api_bp.route('/<path:path>')
def serve_public(path):
    return send_from_directory('public', path)

# API Routes
@api_bp.route('/api/commands', methods=['GET'])
def get_commands():
    commands = db.get_commands()
    return jsonify(commands)

@api_bp.route('/api/commands', methods=['POST'])
def add_command():
    data = request.get_json()
    
    if not data or 'phrase' not in data or 'script' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    command_id = db.add_command(data['phrase'], data['script'])
    
    return jsonify({
        'id': command_id, 
        'phrase': data['phrase'], 
        'script': data['script']
    }), 201

@api_bp.route('/api/commands/<int:command_id>', methods=['PUT'])
def update_command(command_id):
    data = request.get_json()
    
    if not data or 'phrase' not in data or 'script' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    success = db.update_command(command_id, data['phrase'], data['script'])
    
    if not success:
        return jsonify({'error': 'Command not found'}), 404
    
    return jsonify({
        'id': command_id, 
        'phrase': data['phrase'], 
        'script': data['script']
    })

@api_bp.route('/api/commands/<int:command_id>', methods=['DELETE'])
def delete_command(command_id):
    success = db.delete_command(command_id)
    
    if not success:
        return jsonify({'error': 'Command not found'}), 404
    
    return jsonify({'message': 'Command deleted successfully'}), 200

@api_bp.route('/api/toggle', methods=['GET', 'POST'])
def toggle_active_state():
    # Get socketio from Flask app config
    socketio = current_app.config.get('socketio')
    if not socketio:
        socketio = request.environ.get('socketio')
        
    print(f"SocketIO available in toggle route: {socketio is not None}")
    
    if request.method == 'POST':
        data = request.get_json()
        if 'active' in data:
            active_value = data['active']
            db.set_active_state(active_value)
            
            # Start or stop the speech recognition thread based on active state
            if active_value:
                print("Starting speech recognition...")
                start_speech_recognition(socketio)
            else:
                print("Stopping speech recognition...")
                stop_speech_recognition()
    
    active = db.get_active_state()
    
    return jsonify({'active': active}) 