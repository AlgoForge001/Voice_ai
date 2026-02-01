import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("TESTING COMPLETE AUTH FLOW")
print("=" * 60)

# Step 1: Signup
print("\n1. Testing Signup...")
signup_data = {
    "email": "testuser123@example.com",
    "password": "password123",
    "name": "Test User"
}

try:
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        token = data.get("token")
        user = data.get("user")
        print(f"   ✅ Signup successful!")
        print(f"   User: {user.get('email')}")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"   ❌ Signup failed: {response.text}")
        # Try login instead
        print("\n   Trying login instead...")
        response = requests.post(f"{BASE_URL}/auth/login", json={"email": signup_data["email"], "password": signup_data["password"]})
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"   ✅ Login successful!")
            print(f"   Token: {token[:50]}...")
        else:
            print(f"   ❌ Login also failed: {response.text}")
            exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Test /auth/me
print("\n2. Testing /auth/me...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        user = response.json()
        print(f"   ✅ Auth verified!")
        print(f"   User: {user.get('email')}")
        print(f"   Plan: {user.get('plan')}")
        print(f"   Credits: {user.get('credits')}")
    else:
        print(f"   ❌ Auth failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 3: Test TTS Generate
print("\n3. Testing TTS Generate...")
tts_data = {
    "text": "Hello world, this is a test",
    "voice_id": "1",
    "language": "en"
}

try:
    response = requests.post(f"{BASE_URL}/tts/generate", json=tts_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 202:
        job = response.json()
        print(f"   ✅ TTS job created!")
        print(f"   Job ID: {job.get('job_id')}")
        print(f"   Status: {job.get('status')}")
    else:
        print(f"   ❌ TTS failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nYour token for testing in browser:")
print(token)
print("\nPaste this in browser console:")
print(f"localStorage.setItem('auth_token', '{token}');")
print("=" * 60)
