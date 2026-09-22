import psycopg2

conn = psycopg2.connect('postgresql+psycopg://neondb_owner:npg_5pQFxYiPyZ7K@ep-shiny-glade-ayttwkf2.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
cur = conn.cursor()

# Verificar roles
cur.execute('SELECT id, name FROM rol ORDER BY name')
roles = cur.fetchall()
print('Roles en la BD:')
for r in roles:
    print(f'  - {r[1]} (id: {r[0]})')

# Verificar usuarios
cur.execute('SELECT id, email, is_active, is_verified FROM usuario ORDER BY email')
users = cur.fetchall()
print('\nUsuarios en la BD:')
for u in users:
    print(f'  - Email: {u[1]}, Activo: {u[2]}, Verificado: {u[3]}')

# Verificar relación usuario-rol
cur.execute('''
    SELECT u.email, r.name 
    FROM usuario u 
    JOIN usuario_rol ur ON u.id = ur.user_id 
    JOIN rol r ON ur.role_id = r.id 
    ORDER BY u.email, r.name
''')
user_roles = cur.fetchall()
print('\nUsuarios por rol:')
for ur in user_roles:
    print(f'  - {ur[0]} -> {ur[1]}')

cur.close()
conn.close()