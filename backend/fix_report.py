import sys
sys.path.insert(0, r'D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend')
with open('app/services/report_service.py', 'r') as f:
    content = f.read()

# Fix the indentation error in get_sales_indicators
content = content.replace(
    '''query = self.db.query(Sale).filter(
            Sale.paid_at >= start_date,
            Sale.paid_at <= end_date,
            Sale.status == SaleStatus.PAID,
        }
        }
        if branch_id:''',
    '''query = self.db.query(Sale).filter(
            Sale.paid_at >= start_date,
            Sale.paid_at <= end_date,
            Sale.status == SaleStatus.PAID,
        )
        if branch_id:''')

with open('app/services/report_service.py', 'w') as f:
    f.write(content)
print('Fixed')