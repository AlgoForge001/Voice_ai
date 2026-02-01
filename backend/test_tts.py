import asyncio
from app.adapters.tts.mock import get_mock_adapter
from app.adapters.storage.local import get_storage_adapter

async def test_tts():
    print("Testing TTS generation...")
    
    # Test TTS adapter
    tts_adapter = get_mock_adapter()
    print("TTS adapter created")
    
    # Generate audio
    wav_path = await tts_adapter.generate(
        text="Hello world",
        voice_id="1",
        language="en",
        settings={}
    )
    print(f"Audio generated: {wav_path}")
    
    # Test storage adapter
    storage = get_storage_adapter()
    print("Storage adapter created")
    
    # Upload file
    audio_url = await storage.upload_file(
        wav_path,
        "test/test.mp3"
    )
    print(f"File uploaded: {audio_url}")

if __name__ == "__main__":
    asyncio.run(test_tts())