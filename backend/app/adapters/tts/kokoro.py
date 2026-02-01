"""
Kokoro-82M TTS Adapter

Lightweight, CPU-optimized TTS engine using Kokoro-82M ONNX model.
Fast startup, no GPU required, no DLL issues on Windows.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import soundfile as sf

import unicodedata
import re
from kokoro_onnx import Kokoro
from .base import BaseTTS
from app.utils.text_processing import get_text_preprocessor


class KokoroTTSAdapter(BaseTTS):
    """
    Kokoro-82M adapter for text-to-speech generation.
    
    Features:
    - CPU-only inference (fast and stable)
    - Predefined voice presets
    - No voice cloning support
    - English-focused
    - Fast startup (~3-5 seconds)
    
    The model is loaded once and reused for all requests.
    """
    
    def __init__(self, voice_preset: str = "af_sky"):
        """
        Initialize Kokoro TTS adapter.
        
        Args:
            voice_preset: Default voice preset (af_sky, af_bella, am_adam, etc.)
        """
        self.voice_preset = voice_preset
        self.model = None
        # Removed immediate loading to support lazy initialization
        print(f"Kokoro TTS adapter initialized with voice preset: {voice_preset} (Model will lazy-load on first use)")
    
    def _load_model(self):
        """Load Kokoro model once during initialization."""
        try:
            print("[Kokoro] Loading Kokoro-82M model...")
            
            # Use paths relative to backend directory
            model_path = Path(__file__).parent.parent.parent.parent / "models" / "kokoro-v1.0.onnx"
            voices_path = Path(__file__).parent.parent.parent.parent / "models" / "voices-v1.0.bin"
            
            print(f"[Kokoro] Model path: {model_path}")
            print(f"[Kokoro] Voices path: {voices_path}")
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            if not voices_path.exists():
                raise FileNotFoundError(f"Voices file not found: {voices_path}")
            
            self.model = Kokoro(str(model_path), str(voices_path))
            print("[Kokoro] Model loaded successfully!")
        except Exception as e:
            print(f"[Kokoro] Failed to load model: {e}")
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
        Generate speech using Kokoro-82M.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (mapped to Kokoro presets)
            language: Language code (only 'en' supported)
            speaker_wav_path: Ignored (no voice cloning support)
            settings: Ignored (Kokoro uses preset configurations)
        
        Returns:
            Path to generated WAV file
        """
        if not self.model:
            print("[Kokoro] Lazy loading model before generation...")
            self._load_model()
            
        if not self.model:
            raise RuntimeError("Kokoro model failed to load during lazy-initialization")
        
        # Validate input
        is_valid, error = self.validate_input(text, voice_id)
        if not is_valid:
            raise ValueError(error)
        
        # Map voice_id to Kokoro preset
        voice_map = {
            "kokoro_1": "af_sky",      # Female, clear
            "kokoro_2": "am_adam",     # Male, deep
            "kokoro_3": "af_bella",    # Female, warm
            "kokoro_4": "am_michael",  # Male, professional
        }
        voice = voice_map.get(voice_id, self.voice_preset)
        
        # Fallback for old numeric IDs if they somehow come through
        if voice_id in ["1", "2", "3", "4"]:
            voice = voice_map.get(f"kokoro_{voice_id}")
        
        # Create temp output file
        output_dir = Path(tempfile.gettempdir()) / "tts_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{os.urandom(16).hex()}.wav"
        
        try:
            # Preprocess text
            clean_text = self.preprocess_text(text, language)
            
            # Sentence-aware chunking
            preprocessor = get_text_preprocessor()
            chunks = preprocessor.segment_sentences(clean_text, language)
            
            # Group small sentences
            merged_chunks = []
            current = ""
            for s in chunks:
                if len(current) + len(s) < 250:
                    current += " " + s
                else:
                    if current: merged_chunks.append(current.strip())
                    current = s
            if current: merged_chunks.append(current.strip())
            chunks = merged_chunks if merged_chunks else [clean_text]
            
            print(f"[Kokoro] Generating speech with voice '{voice}' in {len(chunks)} smart chunks...")
            
            all_samples = []
            sample_rate = 24000 # Default for Kokoro
            
            for i, chunk in enumerate(chunks):
                if len(chunks) > 1:
                    print(f"[Kokoro] Generating chunk {i+1}/{len(chunks)}...")
                
                # Generate audio for this chunk using the internal model call
                # Note: self.model is the Kokoro model instance
                samples, chunk_sr = self.model.create(
                    text=chunk,
                    voice=voice,
                    speed=1.0,
                    lang="en-us" if language == "en" else language
                )
                all_samples.append(samples)
                sample_rate = chunk_sr
            
            # Concatenate all chunks
            if len(all_samples) > 1:
                final_samples = np.concatenate(all_samples)
            else:
                final_samples = all_samples[0]
            
            # Save to WAV file
            sf.write(
                str(output_path),
                final_samples,
                sample_rate
            )
            
            print(f"[Kokoro] Audio generated successfully: {output_path}")
            
            # Apply voice age presets
            output_path = self.apply_voice_presets(str(output_path), voice_age)
            
            return str(output_path)
        
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"Kokoro TTS generation failed: {str(e)}")
    
    def validate_input(self, text: str, voice_id: str) -> tuple[bool, Optional[str]]:
        """Validate text and voice_id."""
        if not text or len(text.strip()) == 0:
            return False, "Text cannot be empty"
        
        # Increased limit because our chunking now handles long text
        if len(text) > 2000:
            return False, "Text exceeds maximum length of 2000 characters for Kokoro TTS"
        
        return True, None

    def _clean_text(self, text: str) -> str:
        """Normalize and clean text."""
        if not text:
            return ""
        text = unicodedata.normalize('NFKC', text)
        text = "".join(ch for ch in text if ch.isprintable() or ch.isspace())
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _chunk_text(self, text: str, max_chars: int = 250) -> list[str]:
        """Split text into smaller chunks for model safety."""
        if len(text) <= max_chars:
            return [text]
            
        sentences = re.split(r'([\.?!\n]+)', text)
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            part = sentences[i]
            punct = sentences[i+1] if i+1 < len(sentences) else ""
            sentence = (part + punct).strip()
            
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += (" " + sentence) if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                if len(sentence) > max_chars:
                    # Split over-long sentence by words
                    words = sentence.split(' ')
                    temp = ""
                    for w in words:
                        if len(temp) + len(w) + 1 <= max_chars:
                            temp += (" " + w) if temp else w
                        else:
                            if temp: chunks.append(temp.strip())
                            temp = w
                    current_chunk = temp
                else:
                    current_chunk = sentence
                    
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration based on character count.
        Kokoro speaks at roughly 150 characters per minute.
        """
        chars_per_second = 150 / 60  # ~2.5 chars/second
        return len(text) / chars_per_second
    
    def get_available_voices(self) -> list[Dict[str, Any]]:
        """
        Return list of available Kokoro voice presets.
        """
        return [
            {
                "voice_id": "kokoro_1",
                "name": "Sky",
                "accent": "American",
                "gender": "female",
                "language": "en",
                "preview_url": None
            },
            {
                "voice_id": "kokoro_2",
                "name": "Adam",
                "accent": "American",
                "gender": "male",
                "language": "en",
                "preview_url": None
            },
            {
                "voice_id": "kokoro_3",
                "name": "Bella",
                "accent": "American",
                "gender": "female",
                "language": "en",
                "preview_url": None
            },
            {
                "voice_id": "kokoro_4",
                "name": "Michael",
                "accent": "American",
                "gender": "male",
                "language": "en",
                "preview_url": None
            }
        ]
    
    def cleanup(self):
        """Cleanup resources (Kokoro is lightweight, minimal cleanup needed)."""
        print("[Kokoro] Cleanup complete")


# Singleton instance
_kokoro_instance = None


def get_kokoro_adapter() -> KokoroTTSAdapter:
    """
    Get singleton Kokoro adapter instance.
    Model is loaded once and reused.
    """
    global _kokoro_instance
    if _kokoro_instance is None:
        _kokoro_instance = KokoroTTSAdapter()
    return _kokoro_instance
