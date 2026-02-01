"""
Test if we can load speaker wav manually and pass it to XTTS
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
    
    # Load speaker wav manually using torchaudio
    speaker_wav_path = r"app\voices\rachel.wav"
    print(f"Loading speaker wav: {speaker_wav_path}")
    
    # Load using torchaudio (doesn't require torchcodec)
    waveform, sample_rate = torchaudio.load(speaker_wav_path)
    print(f"Speaker wav loaded: shape={waveform.shape}, sr={sample_rate}")
    
    # Test generation with speaker wav path
    print("Testing generation with speaker wav...")
    output_path = "test_with_speaker.wav"
    
    try:
        # Try using the path directly
        wav = tts.tts(
            text="This is a test with speaker file",
            speaker_wav=speaker_wav_path,
            language="en"
        )
        
        print(f"Audio generated! Type: {type(wav)}, Length: {len(wav)}")
        
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
