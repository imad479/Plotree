import requests
import os
import sys
from datetime import datetime, timezone

print("=== KOBO TO GITHUB SYNC DEBUG ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir()}")

# Configuration
try:
    KOBO_TOKEN = os.environ['KOBO_API_TOKEN']
    print("✅ KOBO_API_TOKEN found")
except KeyError:
    print("❌ KOBO_API_TOKEN missing!")
    sys.exit(1)

BASE_URL = "https://kf.kobotoolbox.org"

def get_all_forms():
    try:
        headers = {"Authorization": f"Token {KOBO_TOKEN}"}
        print(f"Requesting forms from: {BASE_URL}/api/v2/assets/")
        response = requests.get(f"{BASE_URL}/api/v2/assets/", headers=headers)
        print(f"API status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"API error: {response.text}")
            return []
            
        data = response.json()
        print(f"Found {data['count']} forms")
        return data['results']
    except Exception as e:
        print(f"❌ get_all_forms failed: {str(e)}")
        return []

def download_form_data(asset_uid, form_name):
    try:
        headers = {"Authorization": f"Token {KOBO_TOKEN}"}
        url = f"{BASE_URL}/api/v2/assets/{asset_uid}/data.csv"
        print(f"Downloading: {url}")
        
        response = requests.get(url, headers=headers, params={"format": "csv"})
        print(f"Download status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Download failed: {response.text}")
            return None
        
        filename = f"{form_name.replace(' ', '_')}.csv"
        print(f"Saving as: {filename}")
        
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        print(f"✅ Saved {filename} ({len(response.content)} bytes)")
        return filename
    except Exception as e:
        print(f"❌ download_form_data failed: {str(e)}")
        return None

# Main process
forms = get_all_forms()
print(f"Processing {len(forms)} forms")

for form in forms:
    form_name = form.get('name', 'unnamed_form')
    asset_uid = form.get('uid')
    
    if not asset_uid:
        print("⚠️ Skipping form without UID")
        continue
        
    print(f"\n🔄 Processing form: {form_name} ({asset_uid})")
    filename = download_form_data(asset_uid, form_name)
    
    if filename:
        print(f"📁 File created: {filename}")
        # Verify file exists
        if os.path.exists(filename):
            print(f"📝 File exists: {filename}, size: {os.path.getsize(filename)} bytes")
        else:
            print(f"❌ File not found: {filename}")

print("\nFinal directory contents:")
print(os.listdir())
print(f"✅ Sync completed at {datetime.now(timezone.utc).isoformat()}")
