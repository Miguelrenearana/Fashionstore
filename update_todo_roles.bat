@echo off
cd /d "D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa"
python -c "
with open('TODO.md', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('- [ ] **Rol BRANCH_MANAGER**: crear enum en `user.py` + migracion Alembic + middleware `require_role` para CU-27/28/29.', '- [x] **Rol BRANCH_MANAGER**: crear enum en `user.py` + migracion Alembic + middleware `require_role` para CU-27/28/29. ✅ **COMPLETADO**')
content = content.replace('- [ ] **CASHIER**: crear rol para CU-23/24 (POS).', '- [x] **CASHIER**: crear rol para CU-23/24 (POS). ✅ **COMPLETADO**')
with open('TODO.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
"