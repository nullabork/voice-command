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
    
    # Create commands table with phrases as JSON array if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phrases TEXT NOT NULL,  -- JSON array of phrases
        script TEXT NOT NULL,
        understand_sentiment INTEGER DEFAULT 0,  -- Boolean 0/1 for sentiment analysis
        sentiment_prefix TEXT DEFAULT ''  -- Prefix for sentiment-based commands
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
                    'INSERT INTO commands (id, phrases, script, understand_sentiment, sentiment_prefix) VALUES (?, ?, ?, ?, ?)',
                    (row[0], row[1], row[2], 0, '')
                )
        elif 'phrase' in columns:
            # Old schema backup
            cursor.execute("SELECT id, phrase, script FROM commands_backup")
            for row in cursor.fetchall():
                phrases = json.dumps([row[1]])  # Convert single phrase to JSON array
                cursor.execute(
                    'INSERT INTO commands (id, phrases, script, understand_sentiment, sentiment_prefix) VALUES (?, ?, ?, ?, ?)',
                    (row[0], phrases, row[2], 0, '')
                )
        print("Sentiment fields migration completed.")
    
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
    
    conn.commit()
    conn.close()

def get_commands():
    """Get all command mappings from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, phrases, script, understand_sentiment, sentiment_prefix FROM commands')
    commands = []
    for row in cursor.fetchall():
        cmd = dict(row)
        # Parse phrases JSON array back to Python list
        cmd['phrases'] = json.loads(cmd['phrases'])
        # Add primary phrase for compatibility
        cmd['phrase'] = cmd['phrases'][0] if cmd['phrases'] else ""
        # Convert understand_sentiment to boolean
        cmd['understand_sentiment'] = bool(cmd['understand_sentiment'])
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

def get_sentiment_commands():
    """Get commands that have sentiment analysis enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, phrases, script, sentiment_prefix FROM commands WHERE understand_sentiment = 1')
    sentiment_commands = {}
    
    for row in cursor.fetchall():
        prefix = row['sentiment_prefix'].lower()
        if prefix not in sentiment_commands:
            sentiment_commands[prefix] = []
            
        # Add command to the list for this prefix
        cmd = {
            'id': row['id'],
            'phrases': json.loads(row['phrases']),
            'script': row['script']
        }
        sentiment_commands[prefix].append(cmd)
    
    conn.close()
    return sentiment_commands

def add_command(phrases, script, understand_sentiment=False, sentiment_prefix=''):
    """Add a new command to the database.
    
    Args:
        phrases: Single string or list of phrases
        script: Command script to execute
        understand_sentiment: Whether to use sentiment analysis
        sentiment_prefix: Prefix for sentiment-based commands
    """
    # Ensure phrases is a list
    if isinstance(phrases, str):
        phrases = [phrases]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO commands (phrases, script, understand_sentiment, sentiment_prefix) VALUES (?, ?, ?, ?)',
        (json.dumps(phrases), script, 1 if understand_sentiment else 0, sentiment_prefix)
    )
    
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return command_id

def update_command(command_id, phrases, script, understand_sentiment=False, sentiment_prefix=''):
    """Update an existing command in the database.
    
    Args:
        command_id: ID of command to update
        phrases: Single string or list of phrases
        script: Command script to execute
        understand_sentiment: Whether to use sentiment analysis
        sentiment_prefix: Prefix for sentiment-based commands
    """
    # Ensure phrases is a list
    if isinstance(phrases, str):
        phrases = [phrases]
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE commands SET phrases = ?, script = ?, understand_sentiment = ?, sentiment_prefix = ? WHERE id = ?',
        (json.dumps(phrases), script, 1 if understand_sentiment else 0, sentiment_prefix, command_id)
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