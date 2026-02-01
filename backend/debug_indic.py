import sys
import os

# Fix for OpenMP error
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

try:
    print("Attempting to import IndicParler adapter...")
    from app.adapters.tts.indicparler import get_indicparler_adapter
    
    print("Attempting to load IndicParler adapter...")
    adapter = get_indicparler_adapter()
    print("IndicParler adapter loaded successfully:", adapter)
    
    print("Attempting to generate Hindi text...")
    # Very short text to test generation
    text = "नमस्ते दुनिया"
    voices = adapter.get_available_voices()
    print(f"Found {len(voices)} voices")
    
    # Don't actually generate if it's too heavy, just check initialization

except Exception as e:
    print("\nCRITICAL ERROR:")
    import traceback
    traceback.print_exc()
