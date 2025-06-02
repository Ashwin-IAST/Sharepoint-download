import os
import requests
import msal
from urllib.parse import quote
import sys
import io
# === Fix Unicode Output for Windows ===
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# === Get filename from CLI ===
if len(sys.argv) < 2:
    print("❌ Error: No filename provided.")
    sys.exit(1)
filename = sys.argv[1]
# === Azure App Credentials (Hardcoded) ===
client_id = "46a6a5f3-e21b-48d8-9471-da2f1683d9d2"
client_secret = "Qld8Q~lu7nMY-jcV2nQk1UFyk5mNyNFzGN4iLaru"
tenant_id = "15718213-950b-4c0d-bde9-a2bed7befbe7"
# === Validation ===
if not client_id:
    print("❌ Error: client_id not set.")
    sys.exit(1)
if not client_secret:
    print("❌ Error: client_secret not set.")
    sys.exit(1)
if not tenant_id:
    print("❌ Error: tenant_id not set.")
    sys.exit(1)
# === MSAL Authentication (Client Credentials Flow) ===
authority = f"https://login.microsoftonline.com/{tenant_id}"
scopes = ["https://graph.microsoft.com/.default"]  # Required for client credentials flow
app = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=authority
)
result = app.acquire_token_for_client(scopes=scopes)
if "access_token" not in result:
    print("❌ Authentication failed.")
    print(result.get("error_description", "No error description available."))
    sys.exit(1)
headers = {"Authorization": f"Bearer {result['access_token']}"}
# === SharePoint Site Info ===
site_domain = "iastsoftware20.sharepoint.com"
site_path = "sites/Testingversions"
# === Get Site ID ===
site_info_url = f"https://graph.microsoft.com/v1.0/sites/{site_domain}:/{site_path}"
site_info_response = requests.get(site_info_url, headers=headers)
if site_info_response.status_code != 200:
    print("❌ Failed to retrieve SharePoint site info.")
    print(site_info_response.text)
    sys.exit(1)
site_id = site_info_response.json()["id"]
# === Get Drive ID ===
drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
drive_response = requests.get(drive_url, headers=headers)
if drive_response.status_code != 200:
    print("❌ Failed to get drive info.")
    print(drive_response.text)
    sys.exit(1)
drive_id = drive_response.json()["id"]
# === Prepare File Path ===
file_path_on_sharepoint = quote(filename)
script_dir = os.path.dirname(os.path.abspath(__file__))
local_path = os.path.join(script_dir, filename)
# === Download File ===
download_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{file_path_on_sharepoint}:/content"
download_response = requests.get(download_url, headers=headers)
if download_response.status_code == 200:
    with open(local_path, "wb") as file:
        file.write(download_response.content)
    print(f"✅ File downloaded successfully to: {local_path}")
    sys.exit(0)
elif download_response.status_code == 404:
    print(f"❌ File '{filename}' not found on SharePoint. Please check the name and try again.")
    sys.exit(1)
else:
    print(f"❌ Download failed. HTTP status: {download_response.status_code}")
    print(download_response.text)
    sys.exit(1)


    # this python file uses the Client secret id from Pooja Azure , No pop up happening : FULLY AUTOMATED 
    # to test it  command : python download.py "F4.1_4March2025.zip"
