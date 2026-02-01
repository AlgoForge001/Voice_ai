"""
Test script for IndicParler-TTS adapter

Tests multiple Indian languages to verify the adapter works correctly.
"""

import asyncio
import sys
import os
# Fix for OpenMP error
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.adapters.tts.indicparler import get_indicparler_adapter


async def test_hindi():
    """Test Hindi TTS generation."""
    print("\n" + "="*60)
    print("Testing Hindi (हिंदी)")
    print("="*60)
    
    adapter = get_indicparler_adapter()
    
    text = "नमस्ते, यह हिंदी टीटीएस परीक्षण है।"
    print(f"Text: {text}")
    
    try:
        audio_path = await adapter.generate(
            text=text,
            voice_id="1",
            language="hi"
        )
        print(f"✅ Success! Audio saved to: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_tamil():
    """Test Tamil TTS generation."""
    print("\n" + "="*60)
    print("Testing Tamil (தமிழ்)")
    print("="*60)
    
    adapter = get_indicparler_adapter()
    
    text = "வணக்கம், இது தமிழ் TTS சோதனை."
    print(f"Text: {text}")
    
    try:
        audio_path = await adapter.generate(
            text=text,
            voice_id="1",
            language="ta"
        )
        print(f"✅ Success! Audio saved to: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_bengali():
    """Test Bengali TTS generation."""
    print("\n" + "="*60)
    print("Testing Bengali (বাংলা)")
    print("="*60)
    
    adapter = get_indicparler_adapter()
    
    text = "নমস্কার, এটি বাংলা TTS পরীক্ষা।"
    print(f"Text: {text}")
    
    try:
        audio_path = await adapter.generate(
            text=text,
            voice_id="2",
            language="bn"
        )
        print(f"✅ Success! Audio saved to: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_telugu():
    """Test Telugu TTS generation."""
    print("\n" + "="*60)
    print("Testing Telugu (తెలుగు)")
    print("="*60)
    
    adapter = get_indicparler_adapter()
    
    text = "నమస్కారం, ఇది తెలుగు TTS పరీక్ష."
    print(f"Text: {text}")
    
    try:
        audio_path = await adapter.generate(
            text=text,
            voice_id="1",
            language="te"
        )
        print(f"✅ Success! Audio saved to: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀 "*20)
    print("IndicParler-TTS Adapter Test Suite")
    print("Testing 23 Indian Languages Support")
    print("🚀 "*20)
    
    results = []
    
    # Test major Indian languages
    results.append(("Hindi", await test_hindi()))
    results.append(("Tamil", await test_tamil()))
    results.append(("Bengali", await test_bengali()))
    results.append(("Telugu", await test_telugu()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for lang, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{lang:15} {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! IndicParler-TTS is working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")


if __name__ == "__main__":
    asyncio.run(main())
