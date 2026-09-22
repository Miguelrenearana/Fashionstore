import requests
import json

BASE_URL = "https://fashionstore-api-r4me.onrender.com"
API_PREFIX = "/api/v1"

# Headers for JSON content
headers = {
    "Content-Type": "application/json",
}

def register_user(email, password, first_name="Test", last_name="User", role_clients=None):
    """Register a new user and return the user data."""
    register_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "phone": "+525512345678"
    }
    
    register_url = f"{BASE_URL}{API_PREFIX}/auth/register"
    print(f"🔄 Registrando: {email}...")
    
    try:
        resp = requests.post(register_url, json=register_data, headers=headers, timeout=15)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 201:
            user_data = resp.json()
            print(f"   ✅ Usuario creado: {user_data.get('email')}")
            print(f"   Rol: {user_data.get('role')}")
            return user_data
        elif resp.status_code == 400:
            error_data = resp.json()
            print(f"   ⚠️ Error: {error_data.get('detail', 'Email already registered?')}")
        else:
            print(f"   ❌ Error inesperado: {resp.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        return None

def login_user(email, password):
    """Login and return auth token."""
    login_data = {
        "email": email,
        "password": password
    }
    
    login_url = f"{BASE_URL}{API_PREFIX}/auth/login"
    print(f"🔑 Iniciando sesión: {email}...")
    
    try:
        resp = requests.post(login_url, json=login_data, headers=headers, timeout=15)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            token_data = resp.json()
            token = token_data.get("access_token")
            print(f"   ✅ Token obtenido: {token[:20]}...")
            return token
        else:
            print(f"   ❌ Login fallido: {resp.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        return None

# Roles a crear
roles_config = [
    {
        "email": "admin@fashionstore.test",
        "password": "TestPass123!",
        "first_name": "Admin",
        "last_name": "User",
        "role": "ADMIN"
    },
    {
        "email": "manager@fashionstore.test", 
        "password": "TestPass123!",
        "first_name": "Manager",
        "last_name": "User",
        "role": "MANAGER"
    },
    {
        "email": "staff@fashionstore.test",
        "password": "TestPass123!",
        "first_name": "Staff",
        "last_name": "User",
        "role": "STAFF"
    },
    {
        "email": "cliente@fashionstore.test",
        "password": "TestPass123!",
        "first_name": "Cliente",
        "last_name": "User",
        "role": "CLIENT"
    }
]

print("=" * 60)
print("CREANDO CUENTAS DE PRUEBA PARA FASHIONSTORE")
print("=" * 60)
print()

# Registrar todos los usuarios
created_users = []
for config in roles_config:
    user = register_user(
        email=config["email"],
        password=config["password"],
        first_name=config["first_name"],
        last_name=config["last_name"]
    )
    if user:
        created_users.append(user)
    print()

# Iniciar sesión en todas las cuentas
print("=" * 60)
print("INICIANDO SESIÓN EN TODAS LAS CUENTAS")
print("=" * 60)
print()

for user in created_users:
    email = user["email"]
    token = login_user(email, "TestPass123!")
    print(f"   {email}: {'✅ OK' if token else '❌ FAIL'}")
    print()

print("=" * 60)
print("RESUMEN DE CUENTAS CREADAS")
print("=" * 60)
print()
print("Credenciales para probar en la página Web:")
print()
for user in created_users:
    print(f"  • Email: {user['email']}")
    print(f"    Contraseña: TestPass123!")
    print(f"    Rol: {user.get('role', 'desconocido')}")
    print()
print("🌐 URL Web: https://fashionstore-api-r4me.onrender.com")
print("📱 Mobile: Usar la app Flutter con API endpoint anterior")