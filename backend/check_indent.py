with open('app/services/report_service.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines[52:65], start=53):
    print(f'{i+53}: {repr(line)}')