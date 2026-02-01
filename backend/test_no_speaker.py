"""
Test if XTTS can generate without speaker file (using default voice)
"""
import warnings
warnings.filterwarnings('ignore')

try:
    from TTS.api import TTS
    import torch
    import torchaudio
    import os
    
    print("Initializing TTS model...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    print("Model loaded successfully!")
    
    # Test generation WITHOUT speaker file
    print("Testing generation without speaker file...")
    output_path = "test_no_speaker.wav"
    
    try:
        # Try using tts() method which returns audio array
        wav = tts.tts(
            text="This is a test without speaker file",
            language="en"
        )
        
        print(f"Audio generated! Type: {type(wav)}, Shape: {wav.shape if hasattr(wav, 'shape') else len(wav)}")
        
        # Save using torchaudio
        import numpy as np
        if isinstance(wav, np.ndarray):
            wav_tensor = torch.FloatTensor(wav).unsqueeze(0)
        else:
            wav_tensor = wav
            
        torchaudio.save(output_path, wav_tensor, 24000)
        
        if os.path.exists(output_path):
            print(f"SUCCESS! Audio saved: {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
        else:
            print("FAILED: Output file not created")
            
    except Exception as e:
        print(f"Generation error: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
