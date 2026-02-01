import os
from huggingface_hub import snapshot_download

TOKEN = "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"

print("🚀 Starting download of ai4bharat/indic-parler-tts...")
print("Checking authentication...")

try:
    # Download model snapshot
    path = snapshot_download(
        repo_id="ai4bharat/indic-parler-tts",
        token=TOKEN,
        local_files_only=False
    )
    print(f"✅ Model downloaded successfully to: {path}")
    
except Exception as e:
    print(f"❌ Download failed: {e}")
    if "401" in str(e) or "403" in str(e):
        print("\n⚠️ Authentication Error! Please ensure you have accepted the model terms at:")
        print("https://huggingface.co/ai4bharat/indic-parler-tts")
    elif "offline" in str(e):
        print("\n⚠️ Network Error! Check your internet connection.")
