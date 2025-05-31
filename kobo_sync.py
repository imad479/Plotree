import requests
import os
import json
from datetime import datetime, timezone

print("=== Kobo Sync Script ===")
print("Environment variables:", os.environ.keys())

# Configuration
KOBO_TOKEN = os.environ.get('KOBO_API_TOKEN')
BASE_URL = "https://kf.kobotoolbox.org"

if not KOBO_TOKEN:
    print("❌ ERROR: KOBO_API_TOKEN not found in environment")
    exit(1)
    
print("✅ KOBO_API_TOKEN found")

# Get forms
try:
    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/v2/assets/", headers=headers)
    print(f"API Status: {response.status_code}")
    
    if response.status_code == 200:
        forms = response.json().get('results', [])
        print(f"Found {len(forms)} forms")
        
        # Process first form only for test
        if forms:
            form = forms[0]
            asset_uid = form['uid']
            form_name = form['name'].replace(' ', '_')
            
            # Download data
            csv_url = f"{BASE_URL}/api/v2/assets/{asset_uid}/data.csv"
            csv_response = requests.get(csv_url, headers=headers)
            
            if csv_response.status_code == 200:
                filename = f"{form_name}.csv"
                with open(filename, 'wb') as f:
                    f.write(csv_response.content)
                print(f"✅ Created {filename} ({len(csv_response.content)} bytes)")
                print("::set-output name=filename::" + filename)
            else:
                print(f"❌ CSV download failed: {csv_response.status_code}")
        else:
            print("⚠️ No forms found")
    else:
        print(f"❌ API request failed: {response.text}")
except Exception as e:
    print(f"🔥 Critical error: {str(e)}")
