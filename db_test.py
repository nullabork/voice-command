#!/usr/bin/env python3
"""
Database connectivity test script
"""
import os

print(f"Working directory: {os.getcwd()}")
print(f"Files in working directory: {os.listdir('.')}")

from src.utils import get_project_root, resolve_path
from src.db.db import init_db, get_commands

# Initialize the database
print("Initializing database...")
init_db()

# Try to get commands
print("Fetching commands...")
commands = get_commands()

print(f"Found {len(commands)} commands in the database")
for cmd in commands:
    print(f"Command: {cmd['id']} - Phrases: {cmd['phrases']}")

print("Database test completed successfully!") 