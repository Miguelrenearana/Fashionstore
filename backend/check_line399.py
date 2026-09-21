import sys
sys.path.insert(0, r'D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend')
with open('app/services/report_service.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines[390:410], start=390):
    print(f'{i+390}: {repr(lines[i])}')