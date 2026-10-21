lines = open('app.py').readlines()
out = []
skip = False
for line in lines:
    if '"""' in line:
        skip = not skip
        continue
    if skip or line.strip().startswith('#'):
        continue
    idx = line.find('#')
    if idx > 0:
        in_str = False
        for i in range(idx):
            if line[i] in ('"', "'"):
                in_str = not in_str
        if not in_str:
            line = line[:idx].rstrip() + '\n'
    out.append(line)
open('app.py', 'w').writelines(out)
print('OK')
