"""
Database module for voice command application.
"""
import sqlite3
import json

# Database setup
DB_PATH = 'voicecommand.db'

def init_db():
    """Initialize the SQLite database with required tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if we need to migrate data
    needs_migration = False
    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='commands'")
        table_def = cursor.fetchone()[0]
        needs_migration = "JSON" not in table_def and "json" not in table_def
    except:
        pass
        
    if needs_migration:
        print("Migrating database to support multiple phrases...")
        # Create a backup of the commands table
        cursor.execute("CREATE TABLE IF NOT EXISTS commands_backup AS SELECT * FROM commands")
        # Drop the existing table
        cursor.execute("DROP TABLE commands")
    
    # Check if we need to migrate to add sentiment fields
    sentiment_migration = False
    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='commands'")
        table_def = cursor.fetchone()[0]
        sentiment_migration = "understand_sentiment" not in table_def.lower()
    except:
        pass
        
    if sentiment_migration and not needs_migration:
        print("Migrating database to support sentiment analysis...")
        # Create a backup of the commands table
        cursor.execute("CREATE TABLE IF NOT EXISTS commands_backup AS SELECT * FROM commands")
        # Drop the existing table
        cursor.execute("DROP TABLE commands")
    
    # Check if we need to migrate to add partial match field
    partial_match_migration = False
    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='commands'")
        table_def = cursor.fetchone()[0]
        partial_match_migration = "partial_match" not in table_def.lower()
    except:
        pass
        
    if partial_match_migration and not needs_migration and not sentiment_migration:
        print("Migrating database to support partial matching...")
        # Create a backup of the commands table
        cursor.execute("CREATE TABLE IF NOT EXISTS commands_backup AS SELECT * FROM commands")
        # Drop the existing table
        cursor.execute("DROP TABLE commands")
    
    # Create commands table with phrases as JSON array if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phrases TEXT NOT NULL,  -- JSON array of phrases
        script TEXT NOT NULL,
        understand_sentiment INTEGER DEFAULT 0,  -- Boolean 0/1 for sentiment analysis
        partial_match INTEGER DEFAULT 0  -- Boolean 0/1 for partial phrase matching
    )
    ''')
    
    # Migrate data if needed for phrases
    if needs_migration:
        cursor.execute("SELECT id, phrase, script FROM commands_backup")
        for row in cursor.fetchall():
            phrases = json.dumps([row[1]])  # Convert single phrase to JSON array
            cursor.execute(
                'INSERT INTO commands (id, phrases, script) VALUES (?, ?, ?)',
                (row[0], phrases, row[2])
            )
        print("Migration completed.")
    
    # Migrate data if needed for sentiment fields
    if sentiment_migration and not needs_migration:
        # Check which columns exist in the backup table
        cursor.execute("PRAGMA table_info(commands_backup)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'phrases' in columns:
            # New schema backup
            cursor.execute("SELECT id, phrases, script FROM commands_backup")
            for row in cursor.fetchall():
                cursor.execute(
                    'INSERT INTO commands (id, phrases, script, understand_sentiment) VALUES (?, ?, ?, ?)',
                    (row[0], row[1], row[2], 0)
                )
        elif 'phrase' in columns:
            # Old schema backup
            cursor.execute("SELECT id, phrase, script FROM commands_backup")
            for row in cursor.fetchall():
                phrases = json.dumps([row[1]])  # Convert single phrase to JSON array
                cursor.execute(
                    'INSERT INTO commands (id, phrases, script, understand_sentiment) VALUES (?, ?, ?, ?)',
                    (row[0], phrases, row[2], 0)
                )
        print("Sentiment fields migration completed.")
    
    # Migrate data if needed for partial match field
    if partial_match_migration and not needs_migration and not sentiment_migration:
        # Check which columns exist in the backup table
        cursor.execute("PRAGMA table_info(commands_backup)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'understand_sentiment' in columns:
            # Schema has sentiment analysis
            cursor.execute("SELECT id, phrases, script, understand_sentiment FROM commands_backup")
            for row in cursor.fetchall():
                cursor.execute(
                    'INSERT INTO commands (id, phrases, script, understand_sentiment, partial_match) VALUES (?, ?, ?, ?, ?)',
                    (row[0], row[1], row[2], row[3], 0)
                )
        elif 'phrases' in columns:
            # New schema without sentiment field
            cursor.execute("SELECT id, phrases, script FROM commands_backup")
            for row in cursor.fetchall():
                cursor.execute(
                    'INSERT INTO commands (id, phrases, script, understand_sentiment, partial_match) VALUES (?, ?, ?, ?, ?)',
                    (row[0], row[1], row[2], 0, 0)
                )
        elif 'phrase' in columns:
            # Old schema
            cursor.execute("SELECT id, phrase, script FROM commands_backup")
            for row in cursor.fetchall():
                phrases = json.dumps([row[1]])  # Convert single phrase to JSON array
                cursor.execute(
                    'INSERT INTO commands (id, phrases, script, understand_sentiment, partial_match) VALUES (?, ?, ?, ?, ?)',
                    (row[0], phrases, row[2], 0, 0)
                )
        print("Partial match field migration completed.")
    
    # Migrate data from old table with sentiment_prefix to new schema without prefix
    try:
        cursor.execute("PRAGMA table_info(commands)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'sentiment_prefix' in columns:
            print("Migrating from sentiment_prefix schema to prefix-free schema...")
            # Create a backup of the commands table
            cursor.execute("CREATE TABLE IF NOT EXISTS commands_backup AS SELECT * FROM commands")
            
            # Drop the existing table
            cursor.execute("DROP TABLE commands")
            
            # Recreate the table without sentiment_prefix field
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrases TEXT NOT NULL,  -- JSON array of phrases
                script TEXT NOT NULL,
                understand_sentiment INTEGER DEFAULT 0,  -- Boolean 0/1 for sentiment analysis
                partial_match INTEGER DEFAULT 0  -- Boolean 0/1 for partial phrase matching
            )
            ''')
            
            # Check which columns exist in the backup table
            cursor.execute("PRAGMA table_info(commands_backup)")
            backup_columns = [column[1] for column in cursor.fetchall()]
            
            if 'understand_sentiment' in backup_columns:
                # Schema has sentiment analysis
                cursor.execute("SELECT id, phrases, script, understand_sentiment FROM commands_backup")
                for row in cursor.fetchall():
                    cursor.execute(
                        'INSERT INTO commands (id, phrases, script, understand_sentiment, partial_match) VALUES (?, ?, ?, ?, ?)',
                        (row[0], row[1], row[2], row[3], 0)
                    )
            else:
                # Schema without sentiment field
                cursor.execute("SELECT id, phrases, script FROM commands_backup")
                for row in cursor.fetchall():
                    cursor.execute(
                        'INSERT INTO commands (id, phrases, script, understand_sentiment, partial_match) VALUES (?, ?, ?, ?, ?)',
                        (row[0], row[1], row[2], 0, 0)
                    )
            print("Migration from sentiment_prefix schema completed.")
    except Exception as e:
        print(f"Error during schema migration: {e}")
    
    # Create settings table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    ''')
    
    # Initialize default settings if they don't exist
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                  ('active', 'false'))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                  ('openai_api_key', ''))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                  ('openai_request_count', '0'))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                  ('global_shortcut_key', ''))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                  ('ai_timeout_enabled', 'false'))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                  ('ai_timeout_seconds', '60'))
    
    conn.commit()
    conn.close()

def get_commands():
    """Get all command mappings from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, phrases, script, understand_sentiment, partial_match FROM commands')
    commands = []
    for row in cursor.fetchall():
        cmd = dict(row)
        # Parse phrases JSON array back to Python list
        cmd['phrases'] = json.loads(cmd['phrases'])
        # Add primary phrase for compatibility
        cmd['phrase'] = cmd['phrases'][0] if cmd['phrases'] else ""
        # Convert understand_sentiment to boolean
        cmd['understand_sentiment'] = bool(cmd['understand_sentiment'])
        # Convert partial_match to boolean
        cmd['partial_match'] = bool(cmd['partial_match'])
        commands.append(cmd)
    
    conn.close()
    return commands

def get_command_mappings():
    """Get command phrase to script mappings for recognition matching."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT phrases, script FROM commands')
    command_map = {}
    
    for row in cursor.fetchall():
        script = row['script']
        # Each phrase in the JSON array maps to the same script
        for phrase in json.loads(row['phrases']):
            command_map[phrase.lower()] = script
    
    conn.close()
    return command_map

def add_command(phrases, script, understand_sentiment=False, partial_match=False):
    """Add a new command to the database.
    
    Args:
        phrases: Single string or list of phrases
        script: Command script to execute
        understand_sentiment: Whether to use sentiment analysis
        partial_match: Whether to allow partial matching
    """
    # Ensure phrases is a list
    if isinstance(phrases, str):
        phrases = [phrases]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO commands (phrases, script, understand_sentiment, partial_match) VALUES (?, ?, ?, ?)',
        (json.dumps(phrases), script, 1 if understand_sentiment else 0, 1 if partial_match else 0)
    )
    
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return command_id

def update_command(command_id, phrases, script, understand_sentiment=False, partial_match=False):
    """Update an existing command in the database.
    
    Args:
        command_id: ID of command to update
        phrases: Single string or list of phrases
        script: Command script to execute
        understand_sentiment: Whether to use sentiment analysis
        partial_match: Whether to allow partial matching
    """
    # Ensure phrases is a list
    if isinstance(phrases, str):
        phrases = [phrases]
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE commands SET phrases = ?, script = ?, understand_sentiment = ?, partial_match = ? WHERE id = ?',
        (json.dumps(phrases), script, 1 if understand_sentiment else 0, 1 if partial_match else 0, command_id)
    )
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0

def delete_command(command_id):
    """Delete a command from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM commands WHERE id = ?', (command_id,))
    rows_affected = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_affected > 0

def get_active_state():
    """Get the active state from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('active',))
    active = cursor.fetchone()[0] == 'true'
    
    conn.close()
    return active

def set_active_state(active):
    """Set the active state in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE settings SET value = ? WHERE key = ?',
        (str(active).lower(), 'active')
    )
    
    conn.commit()
    conn.close()

def get_openai_api_key():
    """Get the OpenAI API key from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('openai_api_key',))
    result = cursor.fetchone()
    api_key = result[0] if result else ''
    
    conn.close()
    return api_key

def set_openai_api_key(api_key):
    """Set the OpenAI API key in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
        ('openai_api_key', api_key)
    )
    
    conn.commit()
    conn.close()
    return True

def get_openai_request_count():
    """Get the OpenAI API request count from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('openai_request_count',))
    result = cursor.fetchone()
    count = int(result[0]) if result else 0
    
    conn.close()
    return count

def increment_openai_request_count():
    """Increment the OpenAI API request count in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current count
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('openai_request_count',))
    result = cursor.fetchone()
    current_count = int(result[0]) if result else 0
    
    # Increment count
    new_count = current_count + 1
    
    # Update in database
    cursor.execute(
        'UPDATE settings SET value = ? WHERE key = ?',
        (str(new_count), 'openai_request_count')
    )
    
    conn.commit()
    conn.close()
    return new_count 

def get_global_shortcut_key():
    """Get the global shortcut key from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('global_shortcut_key',))
    result = cursor.fetchone()
    shortcut_key = result[0] if result else ''
    
    conn.close()
    return shortcut_key

def set_global_shortcut_key(shortcut_key):
    """Set the global shortcut key in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
        ('global_shortcut_key', shortcut_key)
    )
    
    conn.commit()
    conn.close()
    return True

# Add new functions for AI mode timeout settings
def get_ai_timeout_settings():
    """Get the AI mode timeout settings from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('ai_timeout_enabled',))
    enabled_result = cursor.fetchone()
    enabled = enabled_result[0].lower() == 'true' if enabled_result else False
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('ai_timeout_seconds',))
    seconds_result = cursor.fetchone()
    seconds = int(seconds_result[0]) if seconds_result else 60
    
    conn.close()
    return {
        'enabled': enabled,
        'seconds': seconds
    }

def set_ai_timeout_settings(enabled, seconds):
    """Set the AI mode timeout settings in the database.
    
    Args:
        enabled: Boolean indicating if timeout is enabled
        seconds: Integer number of seconds for timeout
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
        ('ai_timeout_enabled', str(enabled).lower())
    )
    
    cursor.execute(
        'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
        ('ai_timeout_seconds', str(seconds))
    )
    
    conn.commit()
    conn.close()
    return True

# Add the missing function that's causing the error
def update_ai_timeout_setting(enabled, seconds):
    """Update the AI mode timeout settings in the database.
    
    Args:
        enabled: Boolean indicating if timeout is enabled
        seconds: Integer number of seconds for timeout
    """
    return set_ai_timeout_settings(enabled, seconds) 