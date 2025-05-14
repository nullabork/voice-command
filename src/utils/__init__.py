"""
Utility functions for the voice command application.
"""
import os
import sys

def get_project_root():
    """Get the absolute path to the project root directory."""
    # First try to find the root by looking for key project files
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Check if we're in the project root by looking for key files
    root_indicators = ['main.py', 'app.py', 'voicecommand.db']
    
    # Print current directory for debugging
    print(f"Current directory: {current_dir}")
    print(f"Files in current directory: {os.listdir(current_dir)}")
    
    # If any of the root indicators are found, we're in the right place
    if any(os.path.exists(os.path.join(current_dir, indicator)) for indicator in root_indicators):
        return current_dir
    
    # If not found in the expected location, try the current working directory
    cwd = os.getcwd()
    if any(os.path.exists(os.path.join(cwd, indicator)) for indicator in root_indicators):
        return cwd
    
    # Fall back to the directory where the script is run from
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if any(os.path.exists(os.path.join(script_dir, indicator)) for indicator in root_indicators):
        return script_dir
    
    # Last resort, just use the current working directory
    print(f"Warning: Could not identify project root, using: {cwd}")
    return cwd

def resolve_path(relative_path):
    """Resolve a path relative to the project root."""
    root = get_project_root()
    full_path = os.path.join(root, relative_path)
    print(f"Resolving path: {relative_path} to {full_path}")
    return full_path
