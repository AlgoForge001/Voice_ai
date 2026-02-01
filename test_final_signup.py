import requests

url = "http://localhost:8000/api/v1/auth/signup"
data = {
    "email": "finaltest@example.com",
    "password": "password123",
    "name": "Final Test"
}

print("Testing signup...")
print(f"Email: {data['email']}")
print(f"Password: {data['password']}")
print(f"Password length: {len(data['password'])} characters")

response = requests.post(url, json=data)
print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 201:
    print("\n✅ ✅ ✅ SUCCESS! Signup worked!")
    result = response.json()
    token = result.get('token')
    user = result.get('user')
    print(f"\nToken: {token[:70]}...")
    print(f"User: {user}")
    print(f"\n🎉 YOU CAN NOW USE THIS IN BROWSER:")
    print(f"localStorage.setItem('auth_token', '{token}');")
else:
    print(f"\n❌ FAILED!")
    print(f"Error: {response.text}")
