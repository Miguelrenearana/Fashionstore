import psycopg2

conn = psycopg2.connect('postgresql://neondb_owner:npg_5pQFxYiPyZ7K@ep-shiny-glade-ayttwkf2.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require')
cur = conn.cursor()

# Obtener IDs de roles
cur.execute("SELECT id, name FROM rol WHERE name IN ('ADMIN', 'MANAGER', 'STAFF', 'CASHIER', 'CLIENT')")
roles = {name: id for id, name in cur.fetchall()}
print("Roles:", roles)

# Obtener IDs de usuarios de prueba
emails = [
    'admin@test.fashionstore.com',
    'manager@test.fashionstore.com',
    'staff@test.fashionstore.com',
    'cashier@test.fashionstore.com',
    'cliente@test.fashionstore.com'
]

for email in emails:
    cur.execute("SELECT id FROM usuario WHERE email = %s", (email,))
    user = cur.fetchone()
    if user:
        print(f"Usuario {email}: id={user[0]}")
    else:
        print(f"Usuario {email}: NO ENCONTRADO")

# Asignar roles
role_mapping = {
    'admin@test.fashionstore.com': 'ADMIN',
    'manager@test.fashionstore.com': 'MANAGER',
    'staff@test.fashionstore.com': 'CASHIER',
    'cashier@test.fashionstore.com': 'CASHIER',
    'cliente@test.fashionstore.com': 'CLIENT',
}

for email, role_name in role_mapping.items():
    user_id = None
    cur.execute("SELECT id FROM usuario WHERE email = %s", (email,))
    user = cur.fetchone()
    if user:
        user_id = user[0]
        role_id = roles[role_name]
        # Verificar si ya tiene el rol
        cur.execute("SELECT 1 FROM usuario_rol WHERE user_id = %s AND role_id = %s", (user_id, role_id))
        if not cur.fetchone():
            cur.execute("INSERT INTO usuario_rol (user_id, role_id) VALUES (%s, %s)", (user_id, role_id))
            print(f"Asignado {role_name} a {email} (user_id={user_id})")
        else:
            print(f"{email} ya tiene rol {role_name}")

conn.commit()

# Verificar
cur.execute("""
    SELECT u.email, r.name 
    FROM usuario u 
    JOIN usuario_rol ur ON u.id = ur.user_id 
    JOIN rol r ON ur.role_id = r.id 
    WHERE u.email LIKE '%@test.fashionstore.com'
    ORDER BY u.email
""")
user_roles = cur.fetchall()
print("\nUsuarios de prueba con roles:")
for ur in user_roles:
    print(f"  - {ur[0]} -> {ur[1]}")

cur.close()
conn.close()
print("Done.")