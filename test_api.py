#!/usr/bin/env python3
"""
API testing script
"""
import requests
import json
import time

# Sleep to make sure server is running
print("Waiting for server to start...")
time.sleep(5)

BASE_URL = "http://localhost:5000"

def test_route(route, method="GET", data=None):
    url = f"{BASE_URL}{route}"
    print(f"Testing {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
        
        return response.status_code
    except Exception as e:
        print(f"Exception: {e}")
        return None

# Test routes
print("\n=== Testing API Routes ===\n")

# Test GET /api/commands
test_route("/api/commands")

# Test GET /api/active
test_route("/api/active")

# Test GET /api/openai-key
test_route("/api/openai-key")

# Test GET /api/openai-stats
test_route("/api/openai-stats")

# Test GET /api/shortcut-key  
test_route("/api/shortcut-key")

# Test GET /api/sentiment-mode
test_route("/api/sentiment-mode")

# Test GET /api/ai-timeout
test_route("/api/ai-timeout")

# Test GET /api/scripts-execution
test_route("/api/scripts-execution")

print("\n=== API Testing Complete ===\n") 