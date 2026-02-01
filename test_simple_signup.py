import requests

url = "http://localhost:8000/api/v1/auth/signup"
data = {
    "email": "simpletest@example.com",
    "password": "pass123",
    "name": "Simple Test"
}

print("Testing signup with simple password...")
print(f"Password length: {len(data['password'])} characters")

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    print("\n✅ SUCCESS! Signup worked!")
    token = response.json().get('token')
    print(f"Token: {token[:50]}...")
else:
    print(f"\n❌ FAILED: {response.text}")
