import requests
import csv
import os
from datetime import datetime
import pytz

# Configuration
KOBO_TOKEN = os.environ['KOBO_API_TOKEN']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO_OWNER = "imad479"
REPO_NAME = "Plotree"
BRANCH = "main"

# KoboToolbox API Endpoints
BASE_URL = "https://kf.kobotoolbox.org"
FORMS_URL = f"{BASE_URL}/api/v2/assets"
DATA_URL = lambda asset_uid: f"{BASE_URL}/api/v2/assets/{asset_uid}/data.csv"

def get_all_forms():
    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    response = requests.get(FORMS_URL, headers=headers)
    response.raise_for_status()
    return response.json()['results']

def download_form_data(asset_uid, form_name):
    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    params = {"format": "csv"}
    response = requests.get(DATA_URL(asset_uid), headers=headers, params=params)
    response.raise_for_status()
    
    # Sanitize filename
    filename = f"{form_name.replace(' ', '_').lower()}_data.csv"
    
    # Write to CSV
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

def commit_to_github(filename):
    # GitHub API setup
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get file SHA if exists
    sha = None
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            sha = response.json().get('sha')
    except:
        pass
    
    # Prepare commit
    with open(filename, 'rb') as f:
        content = f.read()
    
    payload = {
        "message": f"Auto-sync: {datetime.now(pytz.utc).isoformat()}",
        "content": content.decode('base64') if isinstance(content, bytes) else content,
        "branch": BRANCH,
        "sha": sha
    }
    
    response = requests.put(api_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    forms = get_all_forms()
    print(f"Found {len(forms)} forms")
    
    for form in forms:
        form_name = form['name']
        asset_uid = form['uid']
        print(f"Processing: {form_name}")
        
        try:
            filename = download_form_data(asset_uid, form_name)
            commit_result = commit_to_github(filename)
            print(f"Synced {filename} to GitHub")
        except Exception as e:
            print(f"Failed to sync {form_name}: {str(e)}")

if __name__ == "__main__":
    main()
