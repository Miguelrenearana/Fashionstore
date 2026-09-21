with open('..\TODO.md', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('- [ ] **BRANCH_MANAGER**: crear enum en `user.py` + migración Alembic + middleware `require_role` para CU-27/28/29.', '- [x] **BRANCH_MANAGER**: crear enum en `user.py` + migración Alembic + middleware `require_role` para CU-27/28/29. ✅ **COMPLETADO**')
content = content.replace('- [ ] **CASHIER**: crear rol para CU-23/24 (POS).', '- [x] **CASHIER**: crear rol para CU-23/24 (POS). ✅ **COMPLETADO**')
with open('..\TODO.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')