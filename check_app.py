import ast, re
with open('app.py','r',encoding='utf-8') as f: src=f.read()
try:
    ast.parse(src)
    print('SYNTAX OK')
except SyntaxError as e:
    print('ERROR line', e.lineno, ':', e.msg)
funcs = re.findall(r'^def (\w+)', src, re.MULTILINE)
from collections import Counter
dups = [f for f,c in Counter(funcs).items() if c>1]
print('Duplicates:', dups if dups else 'None')
print('Total lines:', src.count('\n'))
