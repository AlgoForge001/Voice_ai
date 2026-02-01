"""
Multi-language TTS Adapter Factory

Automatically selects the best TTS adapter based on language.
Optimized for Indian languages with IndicParler-TTS.
"""

from app.config import get_settings
from .base import BaseTTS

settings = get_settings()

# Define language groups
INDIAN_LANGUAGES = [
    'hi', 'bn', 'ta', 'te', 'mr', 'gu', 'kn', 'ml',
    'pa', 'or', 'as', 'ur', 'sa', 'ks', 'ne', 'sd',
    'bo', 'doi', 'kok', 'mai', 'mni', 'sat'
]

EAST_ASIAN_LANGUAGES = ['ja', 'ko', 'zh']


def normalize_language(language: str) -> str:
    """
    Normalize language codes (e.g., 'hi-IN' -> 'hi', 'Hindi' -> 'hi').
    """
    if not language:
        return "en"
    
    # Clean up string
    lang = language.strip().lower()
    
    # Handle locale-based codes (hi-IN, en-US)
    if '-' in lang:
        lang = lang.split('-')[0]
    if '_' in lang:
        lang = lang.split('_')[0]
        
    # Map common language names to codes
    name_map = {
        'hindi': 'hi',
        'bengali': 'bn',
        'tamil': 'ta',
        'telugu': 'te',
        'marathi': 'mr',
        'gujarati': 'gu',
        'kannada': 'kn',
        'malayalam': 'ml',
        'punjabi': 'pa',
        'english': 'en'
    }
    
    return name_map.get(lang, lang)


def get_tts_adapter(language: str = None) -> BaseTTS:
    """
    Get TTS adapter based on configuration and language.
    """
    # Normalize language code
    normalized_lang = normalize_language(language) if language else None
    
    # If language is specified, route to language-specific adapter
    if normalized_lang:
        # Indian languages → IndicParler (best quality)
        if normalized_lang in INDIAN_LANGUAGES:
            from .indicparler import get_indicparler_adapter
            return get_indicparler_adapter()
        
        # East Asian languages → Kokoro (fast)
        elif normalized_lang in EAST_ASIAN_LANGUAGES:
            from .kokoro import get_kokoro_adapter
            return get_kokoro_adapter()
        
        # English → Kokoro (faster than IndicParler)
        elif normalized_lang == 'en':
            from .kokoro import get_kokoro_adapter
            return get_kokoro_adapter()
    
    # Fallback to configured engine
    engine = settings.TTS_ENGINE.lower()
    
    if engine == "indicparler":
        from .indicparler import get_indicparler_adapter
        return get_indicparler_adapter()
    
    elif engine == "kokoro":
        from .kokoro import get_kokoro_adapter
        return get_kokoro_adapter()
    
    elif engine == "xtts":
        from .xtts_v2 import get_xtts_adapter
        return get_xtts_adapter()
    
    elif engine == "hindi":
        from .hindi import get_hindi_adapter
        return get_hindi_adapter()
    
    else:
        from .kokoro import get_kokoro_adapter
        return get_kokoro_adapter()

def get_all_available_voices():
    """
    Get a consolidated list of all voices from all adapters.
    Optimized to be fast by using singleton instances that are already lazy-loaded.
    """
    all_voices = []
    
    # Get voices from each engine
    # Note: These calls are fast because adapters use lazy model loading now
    try:
        from .kokoro import get_kokoro_adapter
        all_voices.extend(get_kokoro_adapter().get_available_voices())
    except Exception as e:
        print(f"[Factory] Error loading Kokoro voices: {e}")
        
    try:
        from .indicparler import get_indicparler_adapter
        all_voices.extend(get_indicparler_adapter().get_available_voices())
    except Exception as e:
        print(f"[Factory] Error loading IndicParler voices: {e}")
        
    try:
        from .xtts_v2 import get_xtts_adapter
        all_voices.extend(get_xtts_adapter().get_available_voices())
    except Exception as e:
        print(f"[Factory] Error loading XTTS voices: {e}")
        
    return all_voices
