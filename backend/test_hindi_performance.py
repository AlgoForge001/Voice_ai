"""
Quick performance test for Hindi TTS generation.
Tests the optimized IndicParler adapter.
"""
import time
import asyncio
from app.adapters.tts.indicparler import get_indicparler_adapter

async def test_hindi_performance():
    print("=" * 60)
    print("Hindi TTS Performance Test")
    print("=" * 60)
    
    # Test text (Hindi)
    test_text = "नमस्ते, यह एक परीक्षण है। हम हिंदी में बोल रहे हैं।"
    
    print(f"\nTest text: {test_text}")
    print(f"Text length: {len(test_text)} characters")
    
    # Get adapter (should be preloaded)
    print("\n[1/3] Getting IndicParler adapter...")
    start_time = time.time()
    adapter = get_indicparler_adapter()
    adapter_time = time.time() - start_time
    print(f"✓ Adapter ready in {adapter_time:.2f}s")
    
    # Check if model is already loaded
    if adapter.model is None:
        print("\n[2/3] Model not preloaded, loading now...")
        load_start = time.time()
        adapter._load_model()
        load_time = time.time() - load_start
        print(f"✓ Model loaded in {load_time:.2f}s")
    else:
        print("\n[2/3] Model already preloaded ✓")
        load_time = 0
    
    # Generate audio
    print("\n[3/3] Generating audio...")
    gen_start = time.time()
    try:
        audio_path = await adapter.generate(
            text=test_text,
            voice_id="1",
            language="hi",
            voice_age="adult",
            prosody_preset="neutral"
        )
        gen_time = time.time() - gen_start
        print(f"✓ Audio generated in {gen_time:.2f}s")
        print(f"✓ Output: {audio_path}")
        
        # Calculate total time
        total_time = adapter_time + load_time + gen_time
        print("\n" + "=" * 60)
        print("RESULTS:")
        print("=" * 60)
        print(f"Adapter initialization: {adapter_time:.2f}s")
        print(f"Model loading:          {load_time:.2f}s")
        print(f"Audio generation:       {gen_time:.2f}s")
        print(f"TOTAL TIME:             {total_time:.2f}s")
        print("=" * 60)
        
        # Performance assessment
        if total_time < 10:
            print("✓ EXCELLENT: Generation completed in under 10 seconds!")
        elif total_time < 20:
            print("✓ GOOD: Generation completed in under 20 seconds")
        else:
            print("⚠ SLOW: Generation took longer than expected")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hindi_performance())
    exit(0 if success else 1)
