with open('TODO.md', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('- [ ] CU-33 Consultar reportes e indicadores (+ UML)', '- [x] CU-33 Consultar reportes e indicadores (+ UML) ✅ **COMPLETADO**')
content = content.replace('- [ ] CU-34 Consultar bitácora y trazabilidad del sistema (+ UML)', '- [x] CU-34 Consultar bitácora y trazabilidad del sistema (+ UML) ✅ **COMPLETADO**')
content = content.replace('- [ ] CU-35 Consultar información consolidada de ventas e inventario (+ UML)', '- [x] CU-35 Consultar información consolidada de ventas e inventario (+ UML) ✅ **COMPLETADO**')
with open('TODO.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')