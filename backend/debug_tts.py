import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

try:
    print("Attempting to import get_tts_adapter...")
    from app.adapters.tts.factory import get_tts_adapter
    
    print("Attempting to load adapter...")
    adapter = get_tts_adapter()
    print("Adapter loaded successfully:", adapter)
    
    print("Attempting to get voices...")
    voices = adapter.get_available_voices()
    print(f"Found {len(voices)} voices")

except Exception as e:
    print("\nCRITICAL ERROR:")
    import traceback
    traceback.print_exc()
