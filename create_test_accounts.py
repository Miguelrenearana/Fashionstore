import requests
import json

BASE_URL = "https://fashionstore-api-r4me.onrender.com"
API_PREFIX = "/api/v1"

headers = {
    "Content-Type": "application/json",
}

def register_user(email, password, first_name="Test", last_name="User", phone="+525512345678"):
    """Register a new user and return the user data."""
    register_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone
    }
    
    register_url = f"{BASE_URL}{API_PREFIX}/auth/register"
    print(f"Registrando: {email}...")
    
    try:
        resp = requests.post(register_url, json=register_data, headers=headers, timeout=15)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 201:
            user_data = resp.json()
            print(f"   Usuario creado: {user_data.get('email')}")
            return user_data
        elif resp.status_code == 400:
            error_data = resp.json()
            print(f"   Ya existe o error: {error_data.get('detail', 'Error')}")
        else:
            print(f"   Error inesperado: {resp.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   Error de conexion: {e}")
        return None

def login_user(email, password):
    """Login and return auth token."""
    login_data = {
        "email": email,
        "password": password
    }
    
    login_url = f"{BASE_URL}{API_PREFIX}/auth/login"
    print(f"Login: {email}...")
    
    try:
        resp = requests.post(login_url, json=login_data, headers=headers, timeout=15)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            token_data = resp.json()
            token = token_data.get("access_token")
            print(f"   Token: {token[:30]}...")
            return token
        else:
            print(f"   Login fallido: {resp.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   Error de conexion: {e}")
        return None

# Cuentas de prueba a crear (usando dominio válido)
test_accounts = [
    {"email": "admin@test.fashionstore.com", "password": "TestPass123!", "first_name": "Admin", "last_name": "Test", "role": "ADMIN"},
    {"email": "manager@test.fashionstore.com", "password": "TestPass123!", "first_name": "Manager", "last_name": "Test", "role": "MANAGER"},
    {"email": "staff@test.fashionstore.com", "password": "TestPass123!", "first_name": "Staff", "last_name": "Test", "role": "STAFF"},
    {"email": "cashier@test.fashionstore.com", "password": "TestPass123!", "first_name": "Cashier", "last_name": "Test", "role": "CASHIER"},
    {"email": "cliente@test.fashionstore.com", "password": "TestPass123!", "first_name": "Cliente", "last_name": "Test", "role": "CLIENT"},
]

print("=" * 60)
print("CREANDO CUENTAS DE PRUEBA")
print("=" * 60)

created = []
for acc in test_accounts:
    user = register_user(
        email=acc["email"],
        password=acc["password"],
        first_name=acc["first_name"],
        last_name=acc["last_name"]
    )
    if user:
        created.append(acc)
    print()

print("=" * 60)
print("VERIFICANDO LOGIN")
print("=" * 60)

for acc in created:
    token = login_user(acc["email"], acc["password"])
    print(f"   {acc['email']}: {'OK' if token else 'FAIL'}")
    print()

print("=" * 60)
print("CREDENCIALES PARA PROBAR")
print("=" * 60)
for acc in test_accounts:
    print(f"  {acc['email']} / {acc['password']} ({acc['role']})")