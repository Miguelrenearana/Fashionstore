@echo off
cd /d "D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend"
"D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend\.venv\Scripts\python.exe" -c "with open('app/services/report_service.py') as f: lines = f.readlines(); [print(f'{i+84}: {repr(line)}') for i, line in enumerate(lines[83:95])]"
pause