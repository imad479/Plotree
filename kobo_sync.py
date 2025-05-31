import requests
import os
import glob
from datetime import datetime, timezone

print("=== STARTING KOBO SYNC ===")

# Configuration
KOBO_TOKEN = os.environ['KOBO_API_TOKEN']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
BASE_URL = "https://kf.kobotoolbox.org"

def get_forms():
    try:
        headers = {"Authorization": f"Token {KOBO_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/v2/assets/", headers=headers)
        response.raise_for_status()
        return response.json()['results']
    except Exception as e:
        print(f"ERROR FETCHING FORMS: {str(e)}")
        exit(1)

def download_form(asset_uid, form_name):
    try:
        headers = {"Authorization": f"Token {KOBO_TOKEN}"}
        response = requests.get(
            f"{BASE_URL}/api/v2/assets/{asset_uid}/data.csv", 
            headers=headers,
            params={"format": "csv"}
        )
        response.raise_for_status()
        
        filename = f"{form_name.replace(' ', '_').lower()}_data.csv"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {filename} ({len(response.content)} bytes)")
        return filename
    except Exception as e:
        print(f"ERROR DOWNLOADING {form_name}: {str(e)}")
        return None

def main():
    forms = get_forms()
    print(f"Found {len(forms)} forms")
    
    # Clear previous CSV files
    for f in glob.glob("*_data.csv"):
        os.remove(f)
        print(f"Removed old file: {f}")
    
    for form in forms:
        form_name = form['name']
        asset_uid = form['uid']
        print(f"\nProcessing: {form_name} ({asset_uid})")
        download_form(asset_uid, form_name)
    
    print("\nSync completed at", datetime.now(timezone.utc).isoformat())

if __name__ == "__main__":
    main()
