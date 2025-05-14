"""
API routes module for voice command application.
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app, render_template
import db
import os
from speech_recognition_handler import start_speech_recognition, stop_speech_recognition, update_openai_api_key, toggle_sentiment_mode, get_sentiment_mode_state, execute_script, get_scripts_execution_state, toggle_scripts_execution

# Create the API blueprint
api_bp = Blueprint('api', __name__)

# Routes for serving templates and static files
@api_bp.route('/')
def index():
    # Use new template system
    return render_template('layout.html')

@api_bp.route('/public/<path:path>')
def serve_public(path):
    return send_from_directory('public', path)

# Also add a JS-specific route for better organization
@api_bp.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('public/js', path)

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
    
    # Get sentiment analysis field
    understand_sentiment = data.get('understand_sentiment', False)
    
    # Get partial match field
    partial_match = data.get('partial_match', False)
    
    command_id = db.add_command(
        phrases, 
        data['script'], 
        understand_sentiment=understand_sentiment,
        partial_match=partial_match
    )
    
    return jsonify({
        'id': command_id, 
        'phrases': phrases,
        'phrase': phrases[0],  # For backward compatibility
        'script': data['script'],
        'understand_sentiment': understand_sentiment,
        'partial_match': partial_match
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
    
    # Get sentiment analysis field
    understand_sentiment = data.get('understand_sentiment', False)
    
    # Get partial match field
    partial_match = data.get('partial_match', False)
    
    success = db.update_command(
        command_id, 
        phrases, 
        data['script'],
        understand_sentiment=understand_sentiment,
        partial_match=partial_match
    )
    
    if not success:
        return jsonify({'error': 'Command not found'}), 404
    
    return jsonify({
        'id': command_id, 
        'phrases': phrases,
        'phrase': phrases[0],  # For backward compatibility
        'script': data['script'],
        'understand_sentiment': understand_sentiment,
        'partial_match': partial_match
    })

@api_bp.route('/api/commands/<int:command_id>', methods=['DELETE'])
def delete_command(command_id):
    success = db.delete_command(command_id)
    
    if not success:
        return jsonify({'error': 'Command not found'}), 404
    
    return jsonify({'message': 'Command deleted successfully'}), 200

@api_bp.route('/api/active', methods=['GET'])
def get_active():
    active = db.get_active_state()
    return jsonify({'active': active})

@api_bp.route('/api/active', methods=['POST'])
def set_active():
    data = request.get_json()
    if 'active' not in data:
        return jsonify({'error': 'Missing active state'}), 400
    
    active = data['active']
    db.set_active_state(active)
    
    if active:
        # Start speech recognition with socketio instance
        socketio = request.environ.get('socketio')
        start_speech_recognition(socketio)
    else:
        # Stop speech recognition
        stop_speech_recognition()
    
    return jsonify({'active': active})

@api_bp.route('/api/openai-key', methods=['GET'])
def get_openai_key_status():
    api_key = db.get_openai_api_key()
    is_set = bool(api_key)
    
    # Mask the API key for security
    masked_key = ""
    if api_key and len(api_key) > 4:
        masked_key = '*' * (len(api_key) - 4) + api_key[-4:]
    elif api_key:
        masked_key = api_key  # Don't mask if it's too short
    
    return jsonify({
        'isSet': is_set,
        'apiKey': masked_key
    })

@api_bp.route('/api/openai-key', methods=['POST'])
def set_openai_key():
    data = request.get_json()
    if 'apiKey' not in data:
        return jsonify({'error': 'Missing API key'}), 400
    
    api_key = data['apiKey']
    db.set_openai_api_key(api_key)
    
    # Update the API key in the speech recognition handler
    update_openai_api_key(api_key)
    
    return jsonify({'success': True})

@api_bp.route('/api/openai-stats', methods=['GET'])
def get_openai_stats():
    request_count = db.get_openai_request_count()
    return jsonify({
        'requestCount': request_count
    })

@api_bp.route('/api/shortcut-key', methods=['GET'])
def get_shortcut_key():
    shortcut_key = db.get_global_shortcut_key()
    return jsonify({
        'shortcutKey': shortcut_key
    })

@api_bp.route('/api/shortcut-key', methods=['POST'])
def set_shortcut_key():
    data = request.get_json()
    if 'shortcutKey' not in data:
        return jsonify({'error': 'Missing shortcut key'}), 400
    
    shortcut_key = data['shortcutKey']
    db.set_global_shortcut_key(shortcut_key)
    
    return jsonify({'success': True})

@api_bp.route('/api/sentiment-mode', methods=['GET'])
def get_sentiment_mode():
    active = get_sentiment_mode_state()
    return jsonify({'active': active})

@api_bp.route('/api/sentiment-mode', methods=['POST'])
def set_sentiment_mode():
    data = request.get_json()
    if 'active' not in data:
        return jsonify({'error': 'Missing active state'}), 400
    
    active = data['active']
    new_state = toggle_sentiment_mode() if active != get_sentiment_mode_state() else get_sentiment_mode_state()
    
    return jsonify({'active': new_state})

@api_bp.route('/api/ai-timeout', methods=['GET'])
def get_ai_timeout():
    """Get AI mode timeout settings."""
    timeout_settings = db.get_ai_timeout_settings()
    return jsonify(timeout_settings)

@api_bp.route('/api/ai-timeout', methods=['POST'])
def update_ai_timeout():
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        seconds = data.get('seconds', 60)
        
        db.set_ai_timeout_settings(enabled, seconds)
        
        # No need to call update_ai_timeout_state since the settings will be read from the DB when needed
        
        print(f"Updated AI timeout: enabled={enabled}, seconds={seconds}")
        return jsonify({'success': True, 'enabled': enabled, 'seconds': seconds})
    except Exception as e:
        print(f"Error updating AI timeout: {str(e)}")
        return jsonify({'error': str(e)}), 400

@api_bp.route('/api/scripts-execution', methods=['GET'])
def get_scripts_execution():
    """Get the current scripts execution state."""
    try:
        active = get_scripts_execution_state()
        return jsonify({'active': active})
    except Exception as e:
        print(f"Error getting scripts execution state: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/scripts-execution', methods=['POST'])
def toggle_scripts_execution_api():
    """Toggle the scripts execution state."""
    try:
        active = toggle_scripts_execution()
        
        # If socketio is available, emit the event
        socketio = request.environ.get('socketio')
        if socketio:
            socketio.emit('scripts_execution', {'active': active})
        
        return jsonify({'active': active})
    except Exception as e:
        print(f"Error toggling scripts execution: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/script-preview', methods=['POST'])
def preview_script():
    data = request.get_json()
    if 'script' not in data:
        return jsonify({'error': 'Missing script'}), 400
    
    try:
        # Execute the script, with a flag indicating this is just a preview
        result = execute_script(data['script'], preview_mode=True)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 