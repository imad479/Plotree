import requests
import os
import glob
from datetime import datetime, timezone

print("=== KOBO TO GITHUB SYNC STARTED ===")

# Configuration
KOBO_TOKEN = os.environ['KOBO_API_TOKEN']
BASE_URL = "https://kf.kobotoolbox.org"

def download_form_data(asset_uid, form_name):
    try:
        headers = {"Authorization": f"Token {KOBO_TOKEN}"}
        url = f"{BASE_URL}/api/v2/assets/{asset_uid}/data.csv"
        response = requests.get(url, headers=headers, params={"format": "csv"})
        response.raise_for_status()
        
        # Sanitize filename
        filename = f"{form_name.replace(' ', '_')}.csv"
        
        # Save CSV
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        print(f"✅ Downloaded {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error downloading {form_name}: {str(e)}")
        return None

def get_all_forms():
    try:
        headers = {"Authorization": f"Token {KOBO_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/v2/assets/", headers=headers)
        response.raise_for_status()
        return response.json()['results']
    except Exception as e:
        print(f"❌ Failed to fetch forms: {str(e)}")
        return []

# Clear previous CSVs
for f in glob.glob("*.csv"):
    os.remove(f)
    print(f"🧹 Removed old file: {f}")

# Main sync process
forms = get_all_forms()
print(f"📋 Found {len(forms)} forms")

for form in forms:
    form_name = form['name']
    asset_uid = form['uid']
    print(f"\n🔄 Processing: {form_name}")
    download_form_data(asset_uid, form_name)

print(f"\n✅ Sync completed at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("=== SYNC FINISHED ===")
