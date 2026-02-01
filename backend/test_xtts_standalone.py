"""
Test script to verify XTTS v2 can generate audio despite torchcodec errors
"""
import warnings
warnings.filterwarnings('ignore')

try:
    from TTS.api import TTS
    import os
    
    print("Initializing TTS model...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    print("Model loaded successfully!")
    
    # Test generation
    speaker_wav = r"app\voices\rachel.wav"
    if os.path.exists(speaker_wav):
        print(f"Using speaker file: {speaker_wav}")
        output_path = "test_output.wav"
        
        tts.tts_to_file(
            text="This is a test of the TTS system",
            speaker_wav=speaker_wav,
            language="en",
            file_path=output_path
        )
        
        if os.path.exists(output_path):
            print(f"SUCCESS! Audio generated: {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
        else:
            print("FAILED: Output file not created")
    else:
        print(f"ERROR: Speaker file not found: {speaker_wav}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
