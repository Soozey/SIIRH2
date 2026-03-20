#!/usr/bin/env python3
"""
Test script to verify API connectivity and basic functionality
"""

import requests
import json

def test_api_connection():
    """Test basic API connectivity"""
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/")
        print(f"✅ API Health Check: {response.status_code}")
        
        # Test employers endpoint
        response = requests.get(f"{base_url}/employers")
        if response.status_code == 200:
            employers = response.json()
            print(f"✅ Employers endpoint: {len(employers)} employers found")
            
            # If we have employers, test organizational structure
            if employers:
                employer_id = employers[0]['id']
                response = requests.get(f"{base_url}/organizational-structure/{employer_id}/tree")
                if response.status_code == 200:
                    tree_data = response.json()
                    print(f"✅ Organizational tree endpoint: {tree_data.get('total_units', 0)} units found")
                else:
                    print(f"⚠️  Organizational tree endpoint: {response.status_code}")
            else:
                print("ℹ️  No employers found to test organizational structure")
        else:
            print(f"❌ Employers endpoint: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_connection()