#!/usr/bin/env python3
"""
Debug script to check the exact structure of tree data returned by the API
"""

import requests
import json

def debug_tree_data():
    """Debug the tree data structure"""
    base_url = "http://localhost:8000"
    
    try:
        # Get employers first
        response = requests.get(f"{base_url}/employers")
        if response.status_code == 200:
            employers = response.json()
            print(f"Found {len(employers)} employers")
            
            if employers:
                employer_id = employers[0]['id']
                print(f"\nTesting with employer ID: {employer_id}")
                
                # Get tree data
                response = requests.get(f"{base_url}/organizational-structure/{employer_id}/tree")
                if response.status_code == 200:
                    tree_data = response.json()
                    print(f"\nTree data structure:")
                    print(json.dumps(tree_data, indent=2, default=str))
                    
                    # Check if tree has the expected structure
                    if 'tree' in tree_data:
                        tree = tree_data['tree']
                        print(f"\nTree array length: {len(tree)}")
                        
                        if tree:
                            first_node = tree[0]
                            print(f"\nFirst node structure:")
                            print(json.dumps(first_node, indent=2, default=str))
                            
                            # Check for required fields
                            required_fields = ['id', 'name', 'code', 'level', 'level_order', 'worker_count', 'children']
                            missing_fields = [field for field in required_fields if field not in first_node]
                            
                            if missing_fields:
                                print(f"\n❌ Missing required fields: {missing_fields}")
                            else:
                                print(f"\n✅ All required fields present")
                                
                            # Check children structure
                            if 'children' in first_node and first_node['children']:
                                print(f"\nFirst child structure:")
                                print(json.dumps(first_node['children'][0], indent=2, default=str))
                        else:
                            print("\n⚠️  Tree array is empty")
                    else:
                        print("\n❌ No 'tree' key in response")
                else:
                    print(f"❌ Tree endpoint error: {response.status_code}")
                    print(response.text)
        else:
            print(f"❌ Employers endpoint error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_tree_data()