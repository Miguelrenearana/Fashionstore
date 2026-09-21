import ast, glob, os

ROOT = os.getcwd()

print('=== A) routes_reports.py handler bodies verbatim ===')
p = os.path.join(ROOT, 'app', 'api', 'v1', 'routes_reports.py')
src = open(p, encoding='utf-8', errors='replace').read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef,)):
        seg = ast.get_source_segment(src, node)
        print(f'--- def {node.name} (L{node.lineno}) ---')
        for ln in seg.splitlines():
            print('   ', ln.rstrip())
        print()

print('=== B) app/schemas/report.py classes+fields ===')
p = os.path.join(ROOT, 'app', 'schemas', 'report.py')
src = open(p, encoding='utf-8', errors='replace').read()
tree = ast.parse(src)
for node in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
    print(f'class {node.name}({node.bases[0].id if node.bases else ""}):')
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign):
            tgt = stmt.target.id if isinstance(stmt.target, ast.Name) else '?'
            ann = ast.unparse(stmt.annotation)
            print(f'    {tgt}: {ann}')
    print()
