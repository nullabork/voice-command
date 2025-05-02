"""
API routes module for voice command application.
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
import db
import os
from speech_recognition_handler import start_speech_recognition, stop_speech_recognition, update_openai_api_key

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
    
    if not data or 'script' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Handle both single phrase and multiple phrases
    phrases = data.get('phrases', [])
    if not phrases and 'phrase' in data:
        phrases = [data['phrase']]
    
    if not phrases:
        return jsonify({'error': 'At least one phrase is required'}), 400
    
    # Get sentiment analysis fields
    understand_sentiment = data.get('understand_sentiment', False)
    sentiment_prefix = data.get('sentiment_prefix', '')
    
    command_id = db.add_command(
        phrases, 
        data['script'], 
        understand_sentiment=understand_sentiment, 
        sentiment_prefix=sentiment_prefix
    )
    
    return jsonify({
        'id': command_id, 
        'phrases': phrases,
        'phrase': phrases[0],  # For backward compatibility
        'script': data['script'],
        'understand_sentiment': understand_sentiment,
        'sentiment_prefix': sentiment_prefix
    }), 201

@api_bp.route('/api/commands/<int:command_id>', methods=['PUT'])
def update_command(command_id):
    data = request.get_json()
    
    if not data or 'script' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Handle both single phrase and multiple phrases
    phrases = data.get('phrases', [])
    if not phrases and 'phrase' in data:
        phrases = [data['phrase']]
    
    if not phrases:
        return jsonify({'error': 'At least one phrase is required'}), 400
    
    # Get sentiment analysis fields
    understand_sentiment = data.get('understand_sentiment', False)
    sentiment_prefix = data.get('sentiment_prefix', '')
    
    success = db.update_command(
        command_id, 
        phrases, 
        data['script'],
        understand_sentiment=understand_sentiment,
        sentiment_prefix=sentiment_prefix
    )
    
    if not success:
        return jsonify({'error': 'Command not found'}), 404
    
    return jsonify({
        'id': command_id, 
        'phrases': phrases,
        'phrase': phrases[0],  # For backward compatibility
        'script': data['script'],
        'understand_sentiment': understand_sentiment,
        'sentiment_prefix': sentiment_prefix
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

@api_bp.route('/api/openai-key', methods=['GET', 'POST'])
def manage_openai_api_key():
    """Get or set the OpenAI API key."""
    if request.method == 'POST':
        data = request.get_json()
        if 'api_key' in data:
            api_key = data['api_key']
            # Store the API key in the database
            db.set_openai_api_key(api_key)
            
            # Update the environment variable for the current session
            os.environ['OPENAI_API_KEY'] = api_key
            
            # Update the API key in the speech recognition handler
            update_openai_api_key(api_key)
            
            return jsonify({'success': True, 'message': 'API key updated successfully'})
        else:
            return jsonify({'error': 'Missing API key'}), 400
    
    # GET method - return the current API key
    api_key = db.get_openai_api_key()
    
    # Return a masked version of the API key for security
    masked_key = ''
    if api_key:
        # Show only the last 4 characters
        masked_key = '•' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else api_key
    
    return jsonify({'api_key': masked_key, 'is_set': bool(api_key)})

@api_bp.route('/api/openai-stats', methods=['GET'])
def get_openai_stats():
    """Get OpenAI API usage statistics."""
    # Get the OpenAI API request count
    request_count = db.get_openai_request_count()
    
    return jsonify({
        'request_count': request_count
    }) 