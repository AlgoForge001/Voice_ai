import torch
import torchaudio
import warnings
import sys
import os
import io

# CRITICAL: Suppress ALL Windows DLL errors before importing anything else
# This prevents libtorchcodec errors from crashing the application
os.environ['TORCH_FORCE_WEIGHTS_ONLY_LOAD'] = '0'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Suppress all warnings related to torchcodec
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*torchcodec.*')
warnings.filterwarnings('ignore', message='.*libtorchcodec.*')
warnings.filterwarnings('ignore', message='.*torchaudio.*')

# CRITICAL: Set torchaudio backend to soundfile to avoid torchcodec DLL issues on Windows
try:
    torchaudio.set_audio_backend("soundfile")
    print("torchaudio backend set to soundfile")
except Exception as e:
    print(f"Warning: Could not set torchaudio backend: {e}")

# Redirect stderr temporarily during TTS import to suppress DLL errors
class SuppressStderr:
    def __enter__(self):
        self.original_stderr = sys.stderr
        sys.stderr = io.StringIO()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self.original_stderr
        return False

# Import TTS with stderr suppression to hide DLL warnings
print("Loading TTS library (suppressing Windows DLL warnings)...")
with SuppressStderr():
    try:
        from TTS.api import TTS
    except Exception as e:
        # If import fails even with suppression, try without
        from TTS.api import TTS
print("TTS library loaded successfully")
from typing import Optional, Dict, Any
import tempfile
from pathlib import Path
from .base import BaseTTS
from app.config import get_settings

settings = get_settings()


class XTTSv2Adapter(BaseTTS):
    """
    XTTS v2 adapter for text-to-speech generation.
    
    Features:
    - CPU and GPU support
    - Voice cloning with speaker WAV
    - Multi-language support
    - Thread-safe model loading
    
    The model is loaded once and reused for all requests.
    """
    
    def __init__(self):
        self.device = "cuda" if settings.USE_GPU and torch.cuda.is_available() else "cpu"
        self.model = None
        # Removed immediate loading to support lazy initialization
        print(f"XTTS v2 adapter initialized on {self.device} (Model will lazy-load on first use)")
    
    def _load_model(self):
        """Load XTTS v2 model. Called once during initialization."""
        try:
            print(f"Loading XTTS v2 model on {self.device}...")
            
            # Suppress stderr during model loading to hide Windows DLL errors
            with SuppressStderr():
                self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            
            print("XTTS v2 model loaded successfully")
        except Exception as e:
            print(f"Error loading XTTS v2 model: {e}")
            raise
    
    async def generate(
        self,
        text: str,
        voice_id: str,
        language: str = "en",
        voice_age: str = "adult",
        prosody_preset: str = "neutral",
        speaker_wav_path: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate speech using XTTS v2.
        
        Returns path to generated WAV file.
        """
        if not self.model:
            print("[XTTS] Lazy loading model before generation...")
            self._load_model()
            
        if not self.model:
            raise RuntimeError("XTTS model failed to load during lazy-initialization")
        
        # Validate input
        is_valid, error = self.validate_input(text, voice_id)
        if not is_valid:
            raise ValueError(error)
        
        # Create temp output file
        output_dir = Path(tempfile.gettempdir()) / "tts_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{os.urandom(16).hex()}.wav"
        
        try:
            # Preprocess text
            clean_text = self.preprocess_text(text, language)
            
            # Map prosody preset to XTTS parameters if possible
            # XTTS doesn't have direct prosody controls in the API easily, 
            # but we can adjust speed via post-processing if needed.
            # For now, we use the preprocessed text with pauses.
            
            print(f"Using speaker reference: {speaker_wav_path}")

            # Use tts() instead of tts_to_file() to avoid torchcodec issues
            # This returns audio as a numpy array
            wav = self.model.tts(
                text=clean_text,
                speaker_wav=speaker_wav_path,
                language=language
            )
            
            # Convert to tensor and save using soundfile (doesn't require torchcodec)
            import numpy as np
            import soundfile as sf
            
            if isinstance(wav, np.ndarray):
                wav_array = wav
            elif isinstance(wav, torch.Tensor):
                wav_array = wav.cpu().numpy()
            else:
                wav_array = np.array(wav)
            
            # Ensure correct shape for soundfile (samples,) or (samples, channels)
            if wav_array.ndim > 1:
                wav_array = wav_array.squeeze()
            
            # Save using soundfile which doesn't require torchcodec
            sf.write(
                str(output_path),
                wav_array,
                24000  # XTTS v2 sample rate
            )
            
            # Apply voice age presets
            output_path = self.apply_voice_presets(str(output_path), voice_age)
            
            return str(output_path)
        
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"TTS generation failed: {str(e)}")
    
    def validate_input(self, text: str, voice_id: str) -> tuple[bool, Optional[str]]:
        """Validate text and voice_id."""
        if not text or len(text.strip()) == 0:
            return False, "Text cannot be empty"
        
        if len(text) > settings.MAX_CHARS_PER_REQUEST:
            return False, f"Text exceeds maximum length of {settings.MAX_CHARS_PER_REQUEST} characters"
        
        # Add profanity/abuse detection here if needed
        
        return True, None
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration based on character count.
        Rough estimate: ~150 characters per minute of speech.
        """
        chars_per_second = 150 / 60  # ~2.5 chars/second
        return len(text) / chars_per_second
    
    def get_available_voices(self) -> list[Dict[str, Any]]:
        """
        Return list of available voices.
        
        For XTTS v2, voices are defined by speaker WAV files.
        In production, maintain a database of voice profiles.
        """
        # Mock voices for now - replace with actual voice database
        return [
            {
                "voice_id": "xtts_1",
                "name": "Rachel",
                "accent": "American",
                "gender": "female",
                "language": "en",
                "preview_url": None
            },
            {
                "voice_id": "xtts_2",
                "name": "Drew",
                "accent": "British",
                "gender": "male",
                "language": "en",
                "preview_url": None
            },
            {
                "voice_id": "xtts_3",
                "name": "Clyde",
                "accent": "American",
                "gender": "male",
                "language": "en",
                "preview_url": None
            },
            {
                "voice_id": "xtts_4",
                "name": "Mimi",
                "accent": "Australian",
                "gender": "female",
                "language": "en",
                "preview_url": None
            }
        ]
    
    def cleanup(self):
        """Cleanup model and free GPU memory."""
        if self.model:
            del self.model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.model = None


# Singleton instance
_xtts_instance = None


def get_xtts_adapter() -> XTTSv2Adapter:
    """
    Get singleton XTTS adapter instance.
    Model is loaded once and reused.
    """
    global _xtts_instance
    if _xtts_instance is None:
        _xtts_instance = XTTSv2Adapter()
    return _xtts_instance
