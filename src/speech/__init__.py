"""
Speech recognition package for voice command application.
"""
from src.speech.recognition_handler import (
    start_speech_recognition,
    stop_speech_recognition,
    update_openai_api_key,
    toggle_sentiment_mode,
    get_sentiment_mode_state,
    get_ai_timeout_state,
    toggle_scripts_execution,
    get_scripts_execution_state
)
