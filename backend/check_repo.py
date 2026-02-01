import requests
from huggingface_hub import list_repo_files

TOKEN = "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"

print("Listing files in ai4bharat/indic-parler-tts...")
try:
    files = list_repo_files(
        repo_id="ai4bharat/indic-parler-tts",
        token=TOKEN
    )
    print("Files found:", len(files))
    for f in files:
        print(f" - {f}")
except Exception as e:
    print(f"❌ Failed to list files: {e}")

print("\nAttempting raw download of config.json...")
try:
    url = "https://huggingface.co/ai4bharat/indic-parler-tts/resolve/main/config.json"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Download successful!")
        print(response.text[:200])
    else:
        print(f"❌ Download failed: {response.text}")
except Exception as e:
    print(f"❌ Request failed: {e}")
