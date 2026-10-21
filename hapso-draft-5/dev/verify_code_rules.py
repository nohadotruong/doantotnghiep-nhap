import re
from pathlib import Path
from typing import Dict, Set


def check_file(file_path: Path) -> Dict[str, list]:
    violations = {
        'docstrings': [],
        'old_imports': [],
        'print_tags': [],
        'type_hints': [],
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
    except:
        return violations
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if stripped not in ['"""', "'''"] or len(stripped) > 3:
                violations['docstrings'].append(i)
        
        if 'from typing import' in line:
            if 'List' in line or 'Tuple' in line or 'Dict' in line:
                violations['old_imports'].append(i)
        
        if 'print(' in line:
            if not re.search(r'\[[\w_]+\]:', line) and 'print("' in line or "print('" in line or 'print(f' in line:
                if 'EVENT_HANDLER' not in line and 'PLANNER' not in line and 'MAP_SERIALIZER' not in line and 'APP' not in line and 'RENDERER' not in line:
                    if any(x in line for x in ['[F1]', '[F2]', '[F3]', '[F4]', '[F5]']):
                        violations['print_tags'].append(i)
    
    return violations


def main():
    print("=" * 70)
    print("CODE RULE VERIFICATION")
    print("=" * 70)
    
    root = Path.cwd()
    target_dirs = ['core', 'config', 'gui', 'state', 'map']
    
    py_files = []
    for target_dir in target_dirs:
        dir_path = root / target_dir
        if dir_path.exists():
            py_files.extend(dir_path.rglob('*.py'))
    
    py_files = [f for f in py_files if not f.name.startswith('test_') and f.name != 'main.py']
    py_files.sort()
    
    total_violations = 0
    files_with_violations = 0
    
    for file_path in py_files:
        rel_path = file_path.relative_to(root)
        violations = check_file(file_path)
        
        if any(violations.values()):
            files_with_violations += 1
            print(f"\n{rel_path}:")
            if violations['docstrings']:
                print(f"  - Docstrings at lines: {violations['docstrings']}")
                total_violations += len(violations['docstrings'])
            if violations['old_imports']:
                print(f"  - Old typing imports at lines: {violations['old_imports']}")
                total_violations += len(violations['old_imports'])
            if violations['print_tags']:
                print(f"  - Wrong print tags at lines: {violations['print_tags']}")
                total_violations += len(violations['print_tags'])
            if violations['type_hints']:
                print(f"  - Type hint issues at lines: {violations['type_hints']}")
                total_violations += len(violations['type_hints'])
    
    print("\n" + "=" * 70)
    print(f"Checked: {len(py_files)} files")
    print(f"Files with violations: {files_with_violations}")
    print(f"Total violations found: {total_violations}")
    
    if total_violations == 0:
        print("\n✅ ALL CODE RULES COMPLIANT!")
    else:
        print(f"\n⚠️  {total_violations} violations to fix")
    print("=" * 70)


if __name__ == '__main__':
    main()
