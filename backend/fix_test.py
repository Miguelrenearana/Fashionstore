import re

with open('tests/test_cu25_payments.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the duplicate class definition
content = content.replace(
    'class TestCU25PaymentStaticQR:\n    """Tests for CU-25: Procesar pago electrónico con Static QR Gateway"""\n\n    class TestCU25PaymentStaticQR:\n    """Tests for CU-25: Procesar pago electrónico con Static QR Gateway"""',
    'class TestCU25PaymentStaticQR:\n    """Tests for CU-25: Procesar pago electrónico con Static QR Gateway"""'
)

with open('tests/test_cu25_payments.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed')