with open('app/services/report_service.py', 'r') as f:
    content = f.read()

# Fix the query block
content = content.replace(
    'query = self.db.query(Sale).filter(\n            Sale.paid_at >= start_date,\n            Sale.paid_at <= end_date,\n            Sale.status == SaleStatus.PAID,\n        }\n        }\n        if branch_id:',
    'query = self.db.query(Sale).filter(\n            Sale.paid_at >= start_date,\n            Sale.paid_at <= end_date,\n            Sale.status == SaleStatus.PAID,\n        )\n        if branch_id:'
)

with open('app/services/report_service.py', 'w') as f:
    f.write(content)
print('Fixed')