from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.utils.text_processing import get_text_preprocessor


class BaseTTS(ABC):
    """
    Abstract base class for TTS engines.
    This allows swapping TTS providers without changing business logic.
    
    To add a new TTS engine:
    1. Create a new class inheriting from BaseTTS
    2. Implement all abstract methods
    3. Update the factory in tts_service.py
    """
    
    # Prosody Preset Definitions
    PROSODY_PRESETS = {
        "neutral": {
            "description": "Clear and balanced speech.",
            "rate_bias": 1.0,
            "pitch_bias": 1.0,
            "pause_factor": 1.0
        },
        "storytelling": {
            "description": "Expressive, warm, and slightly slower with meaningful pauses.",
            "rate_bias": 0.9,
            "pitch_bias": 1.05,
            "pause_factor": 1.5
        },
        "calm": {
            "description": "Soft, soothing, and slow delivery.",
            "rate_bias": 0.85,
            "pitch_bias": 0.95,
            "pause_factor": 1.3
        },
        "news": {
            "description": "Professional, authoritative, and fast-paced.",
            "rate_bias": 1.1,
            "pitch_bias": 1.0,
            "pause_factor": 0.8
        }
    }

    def preprocess_text(self, text: str, language: str = "en") -> str:
        """
        Helper to run standard preprocessing across adapters.
        """
        preprocessor = get_text_preprocessor()
        return preprocessor.preprocess(text, language)

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
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier
            language: Language code (e.g., 'en', 'es')
            voice_age: Voice age preset ('adult', 'child', 'elder')
            speaker_wav_path: Path to speaker WAV for voice cloning
            settings: Additional settings (stability, similarity_boost, etc.)
        
        Returns:
            Path to generated audio file (WAV format)
        """
        pass
    
    def apply_voice_presets(self, wav_path: str, voice_age: str) -> str:
        """
        Apply pitch and speed modifications to simulate child/elder voices.
        Uses sample rate manipulation for robust, zero-dependency shifting.
        """
        if voice_age == "adult" or not voice_age:
            return wav_path

        try:
            from pydub import AudioSegment
            import os
            
            audio = AudioSegment.from_wav(wav_path)
            
            # Simple shifting via sample rate metadata
            # This changes both pitch AND speed proportionally.
            # Child: +25% sample rate -> Higher pitch & Faster
            # Elder: -20% sample rate -> Lower pitch & Slower
            
            if voice_age == "child":
                new_sample_rate = int(audio.frame_rate * 1.25)
            elif voice_age == "elder":
                new_sample_rate = int(audio.frame_rate * 0.80)
            else:
                return wav_path

            # Apply shift
            # This 'cheats' by telling the player the samples are at a different rate
            # without actually resampling the data.
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
            
            # Reset metadata to standard 24k so players/browsers don't get confused
            # but keep the shifted sound.
            audio = audio.set_frame_rate(24000)

            # Save modified audio
            preset_path = wav_path.replace(".wav", f"_{voice_age}.wav")
            audio.export(preset_path, format="wav")
            
            # Cleanup original
            if os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass
                    
            return preset_path
            
        except Exception as e:
            print(f"[BaseTTS] Failed to apply voice preset {voice_age}: {e}")
            return wav_path

    @abstractmethod
    def validate_input(self, text: str, voice_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate input before generation.
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration in seconds.
        
        Args:
            text: Input text
        
        Returns:
            Estimated duration in seconds
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> list[Dict[str, Any]]:
        """
        Get list of available voices.
        
        Returns:
            List of voice dictionaries with id, name, accent, gender
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        Cleanup resources (models, temp files, etc.)
        """
        pass
