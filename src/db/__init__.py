"""
Database package for voice command application.
"""
from src.db.db import (
    init_db,
    get_commands,
    get_command_mappings,
    add_command,
    update_command,
    delete_command,
    get_active_state,
    set_active_state,
    get_openai_api_key,
    set_openai_api_key,
    get_openai_request_count,
    increment_openai_request_count,
    get_global_shortcut_key,
    set_global_shortcut_key,
    get_ai_timeout_settings,
    set_ai_timeout_settings,
    update_ai_timeout_setting
)
