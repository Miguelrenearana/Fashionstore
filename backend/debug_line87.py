import sys
sys.path.insert(0, r'D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend')
with open('app/services/report_service.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines[83:95], start=84):
    print(f'{i+84}: {repr(lines[i])}')