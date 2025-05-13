#!/usr/bin/env python
import sys
import platform
import subprocess
import os

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def install_requirements():
    # Install all non-problematic packages first
    print("Installing main dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", 
                "--ignore-installed", "pyaudio"])
    
    # Handle PyAudio based on platform
    system = platform.system().lower()
    print(f"Detected system: {system}")
    
    try:
        if system == "windows":
            print("Installing PyAudio using pipwin (recommended for Windows)...")
            run_command([sys.executable, "-m", "pip", "install", "pipwin"])
            run_command([sys.executable, "-m", "pipwin", "install", "pyaudio"])
        elif system == "darwin":  # macOS
            print("For macOS, make sure you have portaudio installed via brew:")
            print("  brew install portaudio")
            print("Installing PyAudio...")
            run_command([sys.executable, "-m", "pip", "install", "pyaudio"])
        elif system == "linux":
            print("Attempting to install PyAudio...")
            try:
                run_command([sys.executable, "-m", "pip", "install", "pyaudio"])
            except:
                print("PyAudio installation failed. Try:")
                print("  sudo apt-get install python3-pyaudio")
                print("  or")
                print("  sudo apt-get install portaudio19-dev && pip install pyaudio")
        
        print("PyAudio installation completed successfully!")
        
    except Exception as e:
        print(f"Error installing PyAudio: {e}")
        print("\nAlternative options:")
        print("1. Install manually following instructions in requirements.txt")
        print("2. Consider using sounddevice as an alternative:")
        choice = input("Would you like to install sounddevice instead? (y/n): ")
        if choice.lower() == 'y':
            run_command([sys.executable, "-m", "pip", "install", "sounddevice"])
            print("You'll need to modify the code to use sounddevice instead of PyAudio.")

if __name__ == "__main__":
    print(f"Python version: {platform.python_version()}")
    install_requirements() 