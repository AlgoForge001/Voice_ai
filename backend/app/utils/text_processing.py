import re
import unicodedata
from typing import List

class TextPreprocessor:
    """
    Advanced text preprocessing for TTS to improve naturalness.
    Supports Hindi, Urdu, and English specifically.
    """
    
    # Silence/Pause constants for various engines
    # For IndicParler, punctuation often handles pauses, but we can exaggerate them
    SHORT_PAUSE = " , "
    MEDIUM_PAUSE = " ... "
    LONG_PAUSE = "\n\n"

    def __init__(self):
        # Punctuation to pause mapping
        self.pause_mapping = {
            ",": self.SHORT_PAUSE,
            ";": self.SHORT_PAUSE,
            ":": self.MEDIUM_PAUSE,
            ".": self.MEDIUM_PAUSE,
            "!": self.MEDIUM_PAUSE,
            "?": self.MEDIUM_PAUSE,
            "।": self.MEDIUM_PAUSE, # Hindi Poorna Viram
            "\n": self.LONG_PAUSE
        }

    def normalize(self, text: str, language: str = "en") -> str:
        """
        Normalize script and remove noise.
        """
        if not text:
            return ""
            
        # Unicode normalization (NFKC fixes many Devanagari/Nastaliq issues)
        text = unicodedata.normalize('NFKC', text)
        
        # Remove noisy symbols but keep punctuation that helps TTS
        # Keep alphanumeric, basic whitespace, and standard punctuation
        text = "".join(ch for ch in text if ch.isalnum() or ch.isspace() or ch in ".,!?।;:\n \"'()")
        
        # Language-specific script cleanup
        if language == "hi":
            # Ensure correct Devanagari range or common fixes
            pass
        elif language == "ur":
            # Urdu specific normalization if needed
            pass
            
        return text.strip()

    def segment_sentences(self, text: str, language: str = "en") -> List[str]:
        """
        Language-aware sentence segmentation.
        """
        if not text:
            return []
            
        # Define sentence endings including Hindi Poorna Viram (।)
        # Using a regex that preserves the delimiter
        delimiters = r'([\.।!?\n]+)'
        parts = re.split(delimiters, text)
        
        sentences = []
        for i in range(0, len(parts)-1, 2):
            sentences.append((parts[i] + parts[i+1]).strip())
        
        # Handle trailing part without delimiter
        if len(parts) % 2 != 0 and parts[-1].strip():
            sentences.append(parts[-1].strip())
            
        return [s for s in sentences if s]

    def insert_intelligent_pauses(self, text: str) -> str:
        """
        Replace standard punctuation with slightly exaggerated pauses 
        to improve rhythm and reduce robotic flow.
        """
        processed = text
        # We don't want to replace everything or we break the model's own prosody.
        # But we can add slight spacing.
        
        # Ensure space after commas and full stops
        processed = re.sub(r'([,;])', r'\1 ', processed)
        processed = re.sub(r'([\.।!?])', r'\1  ', processed)
        
        # Collapse multiple spaces
        processed = re.sub(r' +', ' ', processed)
        
        return processed.strip()

    def preprocess(self, text: str, language: str = "en") -> str:
        """
        Complete preprocessing pipeline.
        """
        normalized = self.normalize(text, language)
        with_pauses = self.insert_intelligent_pauses(normalized)
        return with_pauses

# Singleton instance
_preprocessor = None

def get_text_preprocessor() -> TextPreprocessor:
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = TextPreprocessor()
    return _preprocessor
