@echo off
cd /d "D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend"
"D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend\.venv\Scripts\python.exe" -c "with open('app/services/report_service.py', 'r') as f: lines = f.readlines(); [print(f'{i+53}: {repr(line)}') for i, line in enumerate(lines[52:65])]"
pause