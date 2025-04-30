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
    
    # Create commands table with phrases as JSON array if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phrases TEXT NOT NULL,  -- JSON array of phrases
        script TEXT NOT NULL
    )
    ''')
    
    # Migrate data if needed
    if needs_migration:
        cursor.execute("SELECT id, phrase, script FROM commands_backup")
        for row in cursor.fetchall():
            phrases = json.dumps([row[1]])  # Convert single phrase to JSON array
            cursor.execute(
                'INSERT INTO commands (id, phrases, script) VALUES (?, ?, ?)',
                (row[0], phrases, row[2])
            )
        print("Migration completed.")
    
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
    
    conn.commit()
    conn.close()

def get_commands():
    """Get all command mappings from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, phrases, script FROM commands')
    commands = []
    for row in cursor.fetchall():
        cmd = dict(row)
        # Parse phrases JSON array back to Python list
        cmd['phrases'] = json.loads(cmd['phrases'])
        # Add primary phrase for compatibility
        cmd['phrase'] = cmd['phrases'][0] if cmd['phrases'] else ""
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

def add_command(phrases, script):
    """Add a new command to the database.
    
    Args:
        phrases: Single string or list of phrases
        script: Command script to execute
    """
    # Ensure phrases is a list
    if isinstance(phrases, str):
        phrases = [phrases]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO commands (phrases, script) VALUES (?, ?)',
        (json.dumps(phrases), script)
    )
    
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return command_id

def update_command(command_id, phrases, script):
    """Update an existing command in the database.
    
    Args:
        command_id: ID of command to update
        phrases: Single string or list of phrases
        script: Command script to execute
    """
    # Ensure phrases is a list
    if isinstance(phrases, str):
        phrases = [phrases]
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE commands SET phrases = ?, script = ? WHERE id = ?',
        (json.dumps(phrases), script, command_id)
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