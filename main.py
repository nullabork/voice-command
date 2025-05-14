#!/usr/bin/env python3
"""
Voice Command Application - Main Entry Point

This file provides backward compatibility for the restructured codebase.
It imports from the new folder structure but maintains the same functionality.
"""
# Import from new structure
from src.core.app import app, socketio, initialize_app

# Main entry point
if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Start the Flask application with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False) 