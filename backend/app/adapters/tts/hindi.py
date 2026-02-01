"""
Hindi TTS Adapter using Coqui TTS VITS model

Supports Hindi language with good quality voices.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import soundfile as sf

from TTS.api import TTS
from .base import BaseTTS


class HindiTTSAdapter(BaseTTS):
    """
    Hindi TTS adapter using Coqui TTS VITS model.
    
    Features:
    - Native Hindi support
    - Good quality voices
    - CPU-friendly
    - Fast inference
    """
    
    def __init__(self):
        """Initialize Hindi TTS adapter."""
        self.model = None
        self._load_model()
        print("Hindi TTS adapter initialized")
    
    def _load_model(self):
        """Load Hindi VITS model."""
        try:
            print("[Hindi TTS] Loading Hindi VITS model...")
            # Use Hindi VITS model from Coqui
            self.model = TTS(model_name="tts_models/hi/vits/hindi_male")
            print("[Hindi TTS] Model loaded successfully!")
        except Exception as e:
            print(f"[Hindi TTS] Failed to load model: {e}")
            # Fallback to multilingual model
            try:
                self.model = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
                print("[Hindi TTS] Loaded multilingual model as fallback")
            except Exception as e2:
                print(f"[Hindi TTS] All models failed: {e2}")
                raise
    
    async def generate(
        self,
        text: str,
        voice_id: str,
        language: str = "hi",
        speaker_wav_path: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Hindi speech.
        
        Args:
            text: Hindi text to convert to speech
            voice_id: Voice identifier (ignored for now)
            language: Language code (should be 'hi')
            speaker_wav_path: Optional speaker reference
            settings: Additional settings
        
        Returns:
            Path to generated WAV file
        """
        if not self.model:
            raise RuntimeError("Hindi TTS model not loaded")
        
        # Validate input
        is_valid, error = self.validate_input(text, voice_id)
        if not is_valid:
            raise ValueError(error)
        
        # Create temp output file
        output_dir = Path(tempfile.gettempdir()) / "tts_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{os.urandom(16).hex()}.wav"
        
        try:
            print(f"[Hindi TTS] Generating speech for Hindi text...")
            
            # Generate audio
            self.model.tts_to_file(
                text=text,
                file_path=str(output_path)
            )
            
            print(f"[Hindi TTS] Audio generated successfully: {output_path}")
            return str(output_path)
        
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"Hindi TTS generation failed: {str(e)}")
    
    def validate_input(self, text: str, voice_id: str) -> tuple[bool, Optional[str]]:
        """Validate text and voice_id."""
        if not text or len(text.strip()) == 0:
            return False, "Text cannot be empty"
        
        if len(text) > 1000:
            return False, "Text exceeds maximum length of 1000 characters"
        
        return True, None
    
    def estimate_duration(self, text: str) -> float:
        """Estimate audio duration."""
        # Hindi speaks at roughly 120 characters per minute
        chars_per_second = 120 / 60  # ~2 chars/second
        return len(text) / chars_per_second
    
    def get_available_voices(self) -> list[Dict[str, Any]]:
        """Return list of available Hindi voices."""
        return [
            {
                "voice_id": "hi_1",
                "name": "Hindi Male",
                "accent": "Indian",
                "gender": "male",
                "language": "hi",
                "preview_url": None
            }
        ]
    
    def cleanup(self):
        """Cleanup resources."""
        if self.model:
            del self.model
            self.model = None
        print("[Hindi TTS] Cleanup complete")


# Singleton instance
_hindi_instance = None


def get_hindi_adapter() -> HindiTTSAdapter:
    """Get singleton Hindi adapter instance."""
    global _hindi_instance
    if _hindi_instance is None:
        _hindi_instance = HindiTTSAdapter()
    return _hindi_instance
