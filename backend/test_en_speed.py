import os
import time
import asyncio
import sys
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, str(Path(__file__).parent))

from app.adapters.tts.kokoro import get_kokoro_adapter

async def test_english():
    print("Loading Kokoro...")
    start_load = time.time()
    adapter = get_kokoro_adapter()
    print(f"Kokoro Load Time: {time.time() - start_load:.2f}s")
    
    text = "Hello, this is a test of English TTS speed. It should be much faster than Hindi."
    print(f"Generating English (Kokoro): {text}")
    
    start_gen = time.time()
    path = await adapter.generate(text, "hf_bella")
    duration = time.time() - start_gen
    
    print(f"English Generation Time: {duration:.2f}s")
    return duration

if __name__ == "__main__":
    asyncio.run(test_english())
