import re
from pathlib import Path
from typing import List, Tuple


def extract_imports(content: str) -> Tuple[List[str], List[str], int, int]:
    lines = content.split('\n')
    from_imports = []
    import_stmts = []
    start_idx = None
    end_idx = None
    in_imports = False
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            if in_imports and start_idx is not None:
                end_idx = i - 1
                break
            i += 1
            continue
        
        if line.startswith('from ') and ' import ' in line:
            if start_idx is None:
                start_idx = i
            in_imports = True
            from_imports.append(lines[i].rstrip())
            i += 1
        elif line.startswith('import '):
            if start_idx is None:
                start_idx = i
            in_imports = True
            import_stmts.append(lines[i].rstrip())
            i += 1
        elif in_imports:
            end_idx = i - 1
            break
        else:
            i += 1
    
    if in_imports and end_idx is None:
        end_idx = i - 1
    
    return from_imports, import_stmts, start_idx or 0, end_idx or 0


def sort_imports(from_imports: List[str], import_stmts: List[str]) -> List[str]:
    sorted_from = sorted(from_imports, key=lambda x: x.lower())
    sorted_import = sorted(import_stmts, key=lambda x: x.lower())
    return sorted_from + sorted_import


def fix_imports_in_file(file_path: Path) -> bool:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    from_imports, import_stmts, start_idx, end_idx = extract_imports(content)
    
    if start_idx == 0 and end_idx == 0:
        return False
    
    if not from_imports and not import_stmts:
        return False
    
    lines = content.split('\n')
    sorted_imports = sort_imports(from_imports, import_stmts)
    
    new_lines = lines[:start_idx] + sorted_imports + lines[end_idx + 1:]
    new_content = '\n'.join(new_lines)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False


def process_all_files(root_path: Path):
    print("=" * 70)
    print("Import Sorting Tool")
    print("=" * 70)
    
    target_dirs = ['core', 'config', 'gui', 'state', 'map']
    py_files = []
    for target_dir in target_dirs:
        dir_path = root_path / target_dir
        if dir_path.exists():
            py_files.extend(dir_path.rglob('*.py'))
    
    py_files = [f for f in py_files if f.name != 'main.py' and not f.name.startswith('test_')]
    py_files.sort()
    
    print(f"Found {len(py_files)} files to process\n")
    
    fixed = 0
    for file_path in py_files:
        rel_path = file_path.relative_to(root_path)
        if fix_imports_in_file(file_path):
            fixed += 1
            print(f"  {str(rel_path):<50} FIXED")
        else:
            print(f"  {str(rel_path):<50} ok")
    
    print("\n" + "=" * 70)
    print(f"Files fixed: {fixed}/{len(py_files)}")
    print("=" * 70)


if __name__ == '__main__':
    root = Path.cwd()
    process_all_files(root)
