"""
IndicParler-TTS Adapter

AI4Bharat's state-of-the-art TTS for 23 Indian languages.
Uses Parler-TTS architecture with fine-grained control over voice characteristics.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import torch
import soundfile as sf
import unicodedata
import re

from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
from .base import BaseTTS
from app.utils.text_processing import get_text_preprocessor


# Language mapping for 23 Indian languages
INDIAN_LANGUAGES = {
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'or': 'Odia',
    'as': 'Assamese',
    'ur': 'Urdu',
    'sa': 'Sanskrit',
    'ks': 'Kashmiri',
    'ne': 'Nepali',
    'sd': 'Sindhi',
    'bo': 'Bodo',
    'doi': 'Dogri',
    'kok': 'Konkani',
    'mai': 'Maithili',
    'mni': 'Manipuri',
    'sat': 'Santali',
    'en': 'English'
}


class IndicParlerTTSAdapter(BaseTTS):
    """
    IndicParler-TTS adapter for Indian languages.
    
    Features:
    - 23 Indian languages + English
    - Fine-grained voice control via text descriptions
    - State-of-the-art quality for Indic languages
    - CPU and GPU support
    
    The model is loaded once and reused for all requests.
    """
    
    def __init__(self, model_name: str = "ai4bharat/indic-parler-tts"):
        """
        Initialize IndicParler-TTS adapter.
        
        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.description_tokenizer = None
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # Removed immediate loading to support lazy initialization
        print(f"IndicParler-TTS adapter initialized on {self.device} (Model will lazy-load on first use)")
    
    def _load_model(self):
        """Load IndicParler model and tokenizers."""
        try:
            print(f"[IndicParler] Loading model from {self.model_name}...")
            print(f"[IndicParler] Using device: {self.device}")
            
            # Explicitly download model using huggingface_hub
            # This is more reliable than transformers' internal download
            from huggingface_hub import snapshot_download
            
            try:
                model_path = snapshot_download(
                    repo_id=self.model_name,
                    token=True  # Use logged-in token
                )
                print(f"[IndicParler] Model downloaded/found at: {model_path}")
            except Exception as e:
                print(f"[IndicParler] Download failed: {e}")
                # Fallback to model name if download fails (let transformers try)
                model_path = self.model_name
            
            print("DEBUG: Importing ParlerTTSForConditionalGeneration...")
            from parler_tts import ParlerTTSForConditionalGeneration
            print("DEBUG: Loading model from pretrained...")
            self.model = ParlerTTSForConditionalGeneration.from_pretrained(
                model_path,
                attn_implementation="eager"  # Use eager attention (sdpa not supported)
            ).to(self.device)
            print("DEBUG: Model loaded to device.")
            
            # Enable eval mode for inference optimizations
            self.model.eval()
            
            # NOTE: torch.compile() disabled - compilation overhead (2+ minutes) is worse than benefit
            # The first inference after compilation takes extremely long on CPU
            # Other optimizations (inference_mode, larger chunks) provide sufficient speedup
            # 
            # # Try to compile model for faster CPU inference (PyTorch 2.0+)
            # try:
            #     import torch._dynamo
            #     if hasattr(torch, 'compile') and self.device == "cpu":
            #         print("[IndicParler] Compiling model for CPU optimization...")
            #         self.model = torch.compile(self.model, mode="reduce-overhead")
            #         print("[IndicParler] Model compilation successful!")
            # except Exception as compile_err:
            #     print(f"[IndicParler] Model compilation skipped: {compile_err}")
            
            
            # Load tokenizers
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.description_tokenizer = AutoTokenizer.from_pretrained(
                self.model.config.text_encoder._name_or_path
            )
            
            print("[IndicParler] Model loaded successfully!")
            print(f"[IndicParler] Supported languages: {len(INDIAN_LANGUAGES)}")
            
        except OSError as e:
            if "restricted" in str(e) or "gated" in str(e):
                print(f"[IndicParler] Authentication Error: {e}")
                print("PLEASE ENSURE YOU ACCEPTED THE MODEL TERMS AT: https://huggingface.co/ai4bharat/indic-parler-tts")
            raise
        except Exception as e:
            print(f"[IndicParler] Failed to load model: {e}")
            raise
    
    def _get_voice_description(
        self, 
        voice_id: str, 
        language: str, 
        voice_age: str = "adult",
        prosody_preset: str = "neutral"
    ) -> str:
        """
        Generate voice description for IndicParler.
        """
        # Normalize voice_id if it comes with a prefix
        lookup_id = voice_id
        if voice_id.startswith("indic_"):
            # Format: indic_hi_1 -> 1
            parts = voice_id.split('_')
            if len(parts) >= 3:
                lookup_id = parts[-1]

        # Base presets
        voice_descriptions = {
            "1": "A female speaker delivers clear and expressive speech",
            "2": "A male speaker with a deep voice delivers clear speech",
            "3": "A female speaker with a warm voice delivers slightly expressive speech",
            "4": "A male speaker delivers professional and clear speech",
        }
        
        base_desc = voice_descriptions.get(lookup_id, voice_descriptions["1"])
        
        # Style modifiers
        style_map = {
            "neutral": "with a moderate speed and pitch.",
            "storytelling": "with a warmer, highly expressive voice and slightly slower pace.",
            "calm": "with a soft, soothing voice and slow delivery.",
            "news": "with an authoritative, professional voice and fast-paced delivery."
        }
        
        style_desc = style_map.get(prosody_preset, style_map["neutral"])
        desc = f"{base_desc} {style_desc}"
        
        # Append age modifiers for simulation
        if voice_age == "child":
            desc += " The voice sounds like a young child."
        elif voice_age == "elder":
            desc += " The voice sounds like an elderly person with a slight rasp."
            
        desc += " The recording is of high quality."
        return desc
    
    def _clean_text(self, text: str) -> str:
        """
        Normalize and clean Indic text.
        - Unicode NFKC normalization
        - Remove non-printable characters
        - Normalize whitespace
        """
        if not text:
            return ""
            
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Remove non-printable characters except basic whitespace
        text = "".join(ch for ch in text if ch.isprintable() or ch.isspace())
        
        # Normalize whitespace (replace tabs/newlines with spaces, then collapse)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _chunk_text(self, text: str, max_chars: int = 150) -> list[str]:
        """
        Split text into smaller chunks for stable generation.
        Uses sentence boundaries where possible.
        """
        if len(text) <= max_chars:
            return [text]
            
        # Simple sentence splitter for Indic languages (supporting |, ., ?, !)
        sentences = re.split(r'([।\.?!\n]+)', text)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            part = sentences[i]
            punct = sentences[i+1] if i+1 < len(sentences) else ""
            
            sentence = part + punct
            
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If a single sentence is too long, split it by spaces
                if len(sentence) > max_chars:
                    words = sentence.split(' ')
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= max_chars:
                            temp_chunk += (word + " ")
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    current_chunk = temp_chunk
                else:
                    current_chunk = sentence
                    
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return [c for c in chunks if c]

    async def generate(
        self,
        text: str,
        voice_id: str,
        language: str = "hi",
        voice_age: str = "adult",
        prosody_preset: str = "neutral",
        speaker_wav_path: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate speech using IndicParler-TTS.
        
        Args:
            text: Text to convert to speech (in target language)
            voice_id: Voice identifier (1-4)
            language: Language code (hi, ta, te, bn, etc.)
            speaker_wav_path: Ignored (IndicParler uses text descriptions)
            settings: Optional settings (can include custom voice description)
        
        Returns:
            Path to generated WAV file
        """
        if not self.model:
            print("[IndicParler] Lazy loading model before generation...")
            self._load_model()
        
        if not self.model:
            raise RuntimeError("IndicParler model failed to load during lazy-initialization")
        
        # Validate input
        is_valid, error = self.validate_input(text, voice_id)
        if not is_valid:
            raise ValueError(error)
        
        # Normalize language (e.g., 'hi-IN' -> 'hi')
        if language and '-' in language:
            language = language.split('-')[0]
        if language and '_' in language:
            language = language.split('_')[0]
        language = (language or "hi").lower()

        # Validate language
        if language not in INDIAN_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(INDIAN_LANGUAGES.keys())}")
        
        # Create temp output file
        output_dir = Path(tempfile.gettempdir()) / "tts_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{os.urandom(16).hex()}.wav"
        
        try:
            # Complete preprocessing pipeline (Normalization + Smart Pauses)
            clean_text = self.preprocess_text(text, language)
            print(f"[IndicParler] Preprocessed Text: {clean_text[:50]}...")
            
            # Sentence-aware chunking
            preprocessor = get_text_preprocessor()
            chunks = preprocessor.segment_sentences(clean_text, language)
            
            # Group small sentences to avoid excessive overhead
            merged_chunks = []
            current = ""
            for s in chunks:
                if len(current) + len(s) < 300: # Optimized chunk size (increased from 180)
                    current += " " + s
                else:
                    if current: merged_chunks.append(current.strip())
                    current = s
            if current: merged_chunks.append(current.strip())
            chunks = merged_chunks
            
            print(f"[IndicParler] Processing in {len(chunks)} smart chunks...")
            
            all_audio = []
            
            # Get voice description with style
            if settings and 'voice_description' in settings:
                description = settings['voice_description']
            else:
                description = self._get_voice_description(voice_id, language, voice_age, prosody_preset)

            # Tokenize description once
            description_input_ids = self.description_tokenizer(
                description, 
                return_tensors="pt"
            ).to(self.device)

            for i, chunk in enumerate(chunks):
                if len(chunks) > 1:
                    print(f"[IndicParler] Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                
                prompt_input_ids = self.tokenizer(
                    chunk, 
                    return_tensors="pt"
                ).to(self.device)
                
                # Generate audio with optimized inference mode
                with torch.inference_mode():
                    generation = self.model.generate(
                        input_ids=description_input_ids.input_ids,
                        attention_mask=description_input_ids.attention_mask,
                        prompt_input_ids=prompt_input_ids.input_ids,
                        prompt_attention_mask=prompt_input_ids.attention_mask
                    )
                
                # Convert to numpy and collect
                audio_arr = generation.cpu().numpy().squeeze()
                all_audio.append(audio_arr)
            
            # Concatenate chunks
            if len(all_audio) > 1:
                import numpy as np
                final_audio = np.concatenate(all_audio)
            else:
                final_audio = all_audio[0]

            # Save to WAV file
            sf.write(
                str(output_path),
                final_audio,
                self.model.config.sampling_rate
            )
            
            print(f"[IndicParler] Audio generated successfully! ({len(final_audio)} samples)")
            
            # Apply voice age presets
            output_path = self.apply_voice_presets(str(output_path), voice_age)
            
            return str(output_path)
        
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"IndicParler TTS generation failed: {str(e)}")
    
    def validate_input(self, text: str, voice_id: str) -> tuple[bool, Optional[str]]:
        """Validate text and voice_id."""
        if not text or len(text.strip()) == 0:
            return False, "Text cannot be empty"
        
        # IndicParler can handle longer text than Kokoro
        if len(text) > 1000:
            return False, "Text exceeds maximum length of 1000 characters"
        
        return True, None
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration based on character count.
        Indian languages speak at roughly 120-150 characters per minute.
        """
        chars_per_second = 135 / 60  # ~2.25 chars/second
        return len(text) / chars_per_second
    
    def get_available_voices(self) -> list[Dict[str, Any]]:
        """
        Return list of available voices for all Indian languages.
        """
        voices = []
        
        # Add voices for each language
        for lang_code, lang_name in INDIAN_LANGUAGES.items():
            voices.extend([
                {
                    "voice_id": f"indic_{lang_code}_1",
                    "name": f"{lang_name} Female",
                    "language": lang_code,
                    "gender": "female",
                    "accent": "Indian",
                    "preview_url": None
                },
                {
                    "voice_id": f"indic_{lang_code}_2",
                    "name": f"{lang_name} Male",
                    "language": lang_code,
                    "gender": "male",
                    "accent": "Indian",
                    "preview_url": None
                }
            ])
        
        return voices
    
    def cleanup(self):
        """Cleanup resources."""
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        if self.description_tokenizer:
            del self.description_tokenizer
            self.description_tokenizer = None
        
        # Clear CUDA cache if using GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print("[IndicParler] Cleanup complete")


# Singleton instance
_indicparler_instance = None


def get_indicparler_adapter() -> IndicParlerTTSAdapter:
    """
    Get singleton IndicParler adapter instance.
    Model is loaded once and reused.
    """
    global _indicparler_instance
    if _indicparler_instance is None:
        _indicparler_instance = IndicParlerTTSAdapter()
    return _indicparler_instance
