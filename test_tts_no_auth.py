import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("TESTING TTS WITHOUT AUTH")
print("=" * 60)

# Step 1: Test Generate
print("\n1. Testing TTS Generate (No Token)...")
tts_data = {
    "text": "This is a test message to verify the TTS system is working.",
    "voice_id": "1",
    "language": "en"
}

try:
    # Note: No headers!
    response = requests.post(f"{BASE_URL}/tts/generate", json=tts_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    if response.status_code == 202:
        job = response.json()
        job_id = job.get('job_id')
        print(f"   ✅ TTS job created successfully!")
        print(f"   Job ID: {job_id}")
        
        # Step 2: Poll for status
        print(f"\n2. Polling for job status (Job: {job_id})...")
        for i in range(10):
            time.sleep(1)
            status_resp = requests.get(f"{BASE_URL}/tts/jobs/{job_id}")
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                status = status_data.get('status')
                print(f"   Attempt {i+1}: Status = {status}")
                if status == 'completed':
                    print(f"   ✅ Job completed!")
                    print(f"   Audio URL: {status_data.get('audio_url')}")
                    break
                elif status == 'failed':
                    print(f"   ❌ Job failed: {status_data.get('error_message')}")
                    break
            else:
                print(f"   ⚠️ Error checking status: {status_resp.status_code}")
    else:
        print(f"   ❌ TTS Generation failed: {response.text}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("=" * 60)
