import requests
import json

BASE_URL = "https://fashionstore-api-r4me.onrender.com"
API_PREFIX = "/api/v1"

test_accounts = [
    {"email": "admin@test.fashionstore.com", "password": "TestPass123!", "role": "ADMIN"},
    {"email": "manager@test.fashionstore.com", "password": "TestPass123!", "role": "MANAGER"},
    {"email": "staff@test.fashionstore.com", "password": "TestPass123!", "role": "STAFF (CASHIER)"},
    {"email": "cashier@test.fashionstore.com", "password": "TestPass123!", "role": "CASHIER"},
    {"email": "cliente@test.fashionstore.com", "password": "TestPass123!", "role": "CLIENT"},
]

print("=" * 60)
print("VERIFICANDO LOGIN Y ROLES")
print("=" * 60)

for acc in test_accounts:
    # Usar form-data como espera OAuth2
    login_data = {
        "username": acc["email"],
        "password": acc["password"]
    }
    login_url = f"{BASE_URL}{API_PREFIX}/auth/login"
    
    try:
        resp = requests.post(login_url, data=login_data, timeout=15)
        if resp.status_code == 200:
            token_data = resp.json()
            token = token_data.get("access_token")
            import base64
            payload = token.split('.')[1]
            payload += '=' * (-len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            roles = decoded.get('roles', [])
            print(f"OK {acc['email']} -> roles: {roles}")
        else:
            print(f"FAIL {acc['email']} -> {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"FAIL {acc['email']} -> Error: {e}")

print("\nDone.")