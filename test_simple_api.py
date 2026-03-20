#!/usr/bin/env python3
"""
Test simple pour diagnostiquer les erreurs API
"""

import requests
import json

def test_search():
    try:
        response = requests.get("http://localhost:8000/api/matricules/search?query=DURAND")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_search()