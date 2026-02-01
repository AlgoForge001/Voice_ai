import os
import sys
from huggingface_hub import snapshot_download

TOKEN = "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"

print("🚀 Starting FULL download of ai4bharat/indic-parler-tts...")
print(f"Token: {TOKEN[:5]}...")

try:
    # Login explicitly (optional but good for debugging)
    from huggingface_hub import login
    login(token=TOKEN)
    print("✅ Logged in successfully via script")

    # Download model snapshot
    path = snapshot_download(
        repo_id="ai4bharat/indic-parler-tts",
        token=TOKEN,
        local_files_only=False,
        resume_download=True
    )
    print(f"\n✅ Model downloaded successfully to: {path}")
    
    # Verify critical files exist
    files = os.listdir(path)
    print(f"Files in directory: {len(files)}")
    if "config.json" in files and "pytorch_model.bin" in files:
        print("✅ Core files verified!")
    else:
        print("⚠️ Core files missing!", files)
        
except Exception as e:
    print(f"\n❌ Download failed: {e}")
    import traceback
    traceback.print_exc()
