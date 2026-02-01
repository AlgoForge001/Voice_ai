import requests
import json
import time

# Test TTS generation
base_url = "http://localhost:8000/api/v1"

print("Testing TTS generation...")

# Test data
payload = {
    "text": "Hello, this is a test of the text to speech system.",
    "voice_id": "1",
    "settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

print(f"\n1. Sending TTS generation request...")
print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(f"{base_url}/tts/generate", json=payload)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 202:
        job_data = response.json()
        job_id = job_data['job_id']
        print(f"\n2. Job created: {job_id}")
        print(f"   Initial status: {job_data['status']}")
        
        # Poll for completion
        print(f"\n3. Polling for job completion...")
        max_attempts = 30
        for i in range(max_attempts):
            time.sleep(2)
            status_response = requests.get(f"{base_url}/tts/jobs/{job_id}")
            status_data = status_response.json()
            print(f"   Attempt {i+1}: Status = {status_data['status']}")
            
            if status_data['status'] == 'completed':
                print(f"\n✅ SUCCESS! Audio generated.")
                print(f"   Audio URL: {status_data.get('audio_url')}")
                print(f"   Character count: {status_data.get('character_count')}")
                break
            elif status_data['status'] == 'failed':
                print(f"\n❌ FAILED!")
                print(f"   Error: {status_data.get('error_message')}")
                break
        else:
            print(f"\n⏱️ Timeout waiting for job completion")
    else:
        print(f"\n❌ Request failed with status {response.status_code}")
        print(f"   Error: {response.text}")

except Exception as e:
    print(f"\n❌ Exception occurred: {e}")
    import traceback
    traceback.print_exc()
