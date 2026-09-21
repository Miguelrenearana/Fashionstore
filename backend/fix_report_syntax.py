import sys

filepath = r"D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend\app\services\report_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old = '''query = self.db.query(Sale).filter(
            Sale.paid_at >= start_date,
            Sale.paid_at <= end_date,
            Sale.status == SaleStatus.PAID,
        }
        }
        if branch_id:'''

new = '''query = self.db.query(Sale).filter(
            Sale.paid_at >= start_date,
            Sale.paid_at <= end_date,
            Sale.status == SaleStatus.PAID,
        )
        if branch_id:'''

if old in content:
    content = content.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("FIXED indentation")
else:
    print("PATTERN NOT FOUND - printing lines 51-60")
    lines = content.split("\n")
    for i, l in enumerate(lines[50:60], start=51):
        print(f"{i}: {repr(l)}")
