"""
Database module for voice command application.
"""
import sqlite3

# Database setup
DB_PATH = 'voicecommand.db'

def init_db():
    """Initialize the SQLite database with required tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create commands table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phrase TEXT NOT NULL,
        script TEXT NOT NULL
    )
    ''')
    
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
    
    cursor.execute('SELECT * FROM commands')
    commands = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return commands

def get_command_mappings():
    """Get command phrase to script mappings for recognition matching."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT phrase, script FROM commands')
    commands = {row['phrase'].lower(): row['script'] for row in cursor.fetchall()}
    
    conn.close()
    return commands

def add_command(phrase, script):
    """Add a new command to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO commands (phrase, script) VALUES (?, ?)',
        (phrase, script)
    )
    
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return command_id

def update_command(command_id, phrase, script):
    """Update an existing command in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE commands SET phrase = ?, script = ? WHERE id = ?',
        (phrase, script, command_id)
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