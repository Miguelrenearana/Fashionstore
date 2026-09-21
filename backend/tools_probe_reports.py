import ast, glob, os

ROOT = os.getcwd()

def walk_files(base, pattern):
    return glob.glob(os.path.join(base, pattern), recursive=True)

print('=== 1) files matching routes for reports ===')
for p in walk_files(ROOT, 'app/**/routes_*report*.py'):
    print('   ', os.path.relpath(p, ROOT))

print('=== 2) who includes a reports router ===')
for p in walk_files(ROOT, 'app/**/*.py'):
    base = os.path.basename(p)
    if base in ('router.py', 'routes.py', 'main.py', '__init__.py') or p.lower().endswith('__init__.py'):
        src = open(p, encoding='utf-8', errors='replace').read()
        if 'reports' in src.lower():
            for i, line in enumerate(src.splitlines(), 1):
                if 'reports' in line.lower():
                    print(f'   [{os.path.relpath(p, ROOT)}] L{i}: {line.strip()}')

print('=== 3) decorators in each routes_reports file ===')
for p in walk_files(ROOT, 'app/**/routes_*report*.py'):
    print('###', os.path.relpath(p, ROOT))
    try:
        tree = ast.parse(open(p, encoding='utf-8', errors='replace').read())
    except SyntaxError as e:
        print('   SYNTAX ERROR:', e)
        continue
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) \
                        and dec.func.attr in ('get', 'post', 'put', 'delete', 'patch'):
                    verb = dec.func.attr.upper()
                    path = ''
                    if dec.args and isinstance(dec.args[0], ast.Constant):
                        path = dec.args[0].value
                    print(f'   {verb:<5} {path!r} -> def {node.name}')

print('=== 4) test file client calls ===')
for p in walk_files(ROOT, 'tests/*report*.py'):
    print('###', os.path.relpath(p, ROOT))
    try:
        tree = ast.parse(open(p, encoding='utf-8', errors='replace').read())
    except SyntaxError as e:
        print('   SYNTAX ERROR:', e)
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            fa = node.func
            if isinstance(fa.value, ast.Name) and fa.value.id == 'client' \
                    and fa.attr in ('get', 'post', 'put', 'delete', 'patch'):
                url = ''
                if node.args and isinstance(node.args[0], ast.Constant):
                    url = node.args[0].value
                has_json = any(k.arg == 'json' for k in node.keywords)
                print(f'   L{node.lineno}: client.{fa.attr}({url!r}, json={has_json})')

print('=== 5) report_service.py syntax ===')
sp = os.path.join(ROOT, 'app', 'services', 'report_service.py')
if os.path.exists(sp):
    src = open(sp, encoding='utf-8', errors='replace').read()
    try:
        ast.parse(src)
        print('   PARSES OK, lines=', src.count(chr(10)) + 1)
    except SyntaxError as e:
        print('   SYNTAX ERROR at line', e.lineno, '-', e.msg)
else:
    print('   MISSING')
