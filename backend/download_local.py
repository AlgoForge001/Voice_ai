import os
from huggingface_hub import snapshot_download

TOKEN = "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"
LOCAL_DIR = os.path.abspath("models/indic_parler")

print(f"🚀 Starting download to LOCAL directory: {LOCAL_DIR}")
print("This avoids system cache/symlink issues.")

try:
    os.makedirs(LOCAL_DIR, exist_ok=True)
    
    # Download directly to local folder
    path = snapshot_download(
        repo_id="ai4bharat/indic-parler-tts",
        token=TOKEN,
        local_dir=LOCAL_DIR,
        local_dir_use_symlinks=False,  # CRITICAL for Windows without Dev Mode
        resume_download=True
    )
    print(f"\n✅ Model downloaded successfully to: {path}")
    
    # Verification
    files = os.listdir(path)
    print(f"Files found: {len(files)}")
    
except Exception as e:
    print(f"\n❌ Download failed: {e}")
    import traceback
    traceback.print_exc()
