from typing import Optional, Dict, Any
from .base import BaseTTS


class MockTTSAdapter(BaseTTS):
    """
    Mock TTS adapter for testing without actual TTS library.
    Returns dummy audio for demonstration purposes.
    
    Use this when:
    - Testing the API without TTS library installed
    - Python version incompatible with TTS library
    - Quick prototyping
    """
    
    async def generate(
        self,
        text: str,
        voice_id: str,
        language: str = "en",
        speaker_wav_path: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Mock generation - returns path to a dummy audio file.
        In production, replace this with actual XTTS adapter.
        """
        import os
        import tempfile
        from pathlib import Path
        
        # Create a dummy WAV file
        output_dir = Path(tempfile.gettempdir()) / "tts_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{os.urandom(16).hex()}.wav"
        
        # Create a WAV file with actual audio data (simple tone)
        import struct
        import math
        
        sample_rate = 44100
        duration = 2.0  # 2 seconds
        frequency = 440.0  # A4 note
        amplitude = 0.3
        
        # Calculate number of samples
        num_samples = int(sample_rate * duration)
        
        # Generate audio data
        audio_data = []
        for i in range(num_samples):
            # Simple sine wave
            sample = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            # Convert to 16-bit signed integer
            sample_int = int(sample * 32767)
            audio_data.append(struct.pack('<h', sample_int))
        
        # Create WAV file
        with open(output_path, 'wb') as f:
            # RIFF header
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + num_samples * 2))  # File size
            f.write(b'WAVE')
            
            # fmt chunk
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))  # Chunk size
            f.write(struct.pack('<H', 1))   # Audio format (PCM)
            f.write(struct.pack('<H', 1))   # Number of channels
            f.write(struct.pack('<I', sample_rate))  # Sample rate
            f.write(struct.pack('<I', sample_rate * 2))  # Byte rate
            f.write(struct.pack('<H', 2))   # Block align
            f.write(struct.pack('<H', 16))  # Bits per sample
            
            # data chunk
            f.write(b'data')
            f.write(struct.pack('<I', num_samples * 2))  # Data size
            f.write(b''.join(audio_data))
        
        return str(output_path)
    
    def validate_input(self, text: str, voice_id: str) -> tuple[bool, Optional[str]]:
        """Validate text and voice_id."""
        if not text or len(text.strip()) == 0:
            return False, "Text cannot be empty"
        
        if len(text) > 5000:
            return False, f"Text exceeds maximum length of 5000 characters"
        
        return True, None
    
    def estimate_duration(self, text: str) -> float:
        """Estimate audio duration."""
        chars_per_second = 150 / 60
        return len(text) / chars_per_second
    
    def get_available_voices(self) -> list[Dict[str, Any]]:
        """Return mock voices."""
        return [
            {
                "voice_id": "mock_1",
                "name": "Rachel (Mock)",
                "accent": "American",
                "gender": "female",
                "language": "en",
                "preview_url": None
            },
            {
                "voice_id": "mock_2",
                "name": "Drew (Mock)",
                "accent": "British",
                "gender": "male",
                "language": "en",
                "preview_url": None
            }
        ]
    
    def cleanup(self):
        """Cleanup - nothing to do for mock."""
        pass


# Singleton instance
_mock_instance = None


def get_mock_adapter() -> MockTTSAdapter:
    """Get singleton mock adapter instance."""
    global _mock_instance
    if _mock_instance is None:
        _mock_instance = MockTTSAdapter()
    return _mock_instance
