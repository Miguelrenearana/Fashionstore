import re

with open('tests/test_cu25_payments.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace r.json()["reference"] with r.json()["gateway_reference"]
content = content.replace('r.json()["reference"]', 'r.json()["gateway_reference"]')

with open('tests/test_cu25_payments.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')