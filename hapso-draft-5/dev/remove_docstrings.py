import ast
import sys
from pathlib import Path
from typing import List, Tuple


class DocstringRemover(ast.NodeVisitor):
    def __init__(self):
        self.docstring_ranges: List[Tuple[int, int]] = []
    
    def visit_Module(self, node: ast.Module) -> None:
        if (node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, (ast.Str, ast.Constant))):
            first = node.body[0]
            if isinstance(first.value, (ast.Str, ast.Constant)):
                self.docstring_ranges.append((first.lineno, first.end_lineno or first.lineno))
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_docstring(node)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_docstring(node)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check_docstring(node)
        self.generic_visit(node)
    
    def _check_docstring(self, node) -> None:
        if (node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, (ast.Str, ast.Constant))):
            first = node.body[0]
            if isinstance(first.value, (ast.Str, ast.Constant)):
                self.docstring_ranges.append((first.lineno, first.end_lineno or first.lineno))


def remove_docstrings_from_file(file_path: Path) -> Tuple[int, int]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        if not source.strip():
            return 0, 0
        
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"  WARNING Parse error in {file_path}: {e}")
            return 0, 1
        
        remover = DocstringRemover()
        remover.visit(tree)
        
        if not remover.docstring_ranges:
            return 0, 0
        
        docstring_ranges = sorted(remover.docstring_ranges, reverse=True)
        lines = source.splitlines(keepends=True)
        
        for start_line, end_line in docstring_ranges:
            start_idx = start_line - 1
            end_idx = end_line
            del lines[start_idx:end_idx]
        
        new_source = ''.join(lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_source)
        
        return len(docstring_ranges), 0
    
    except IOError as e:
        print(f"  ERROR IO error in {file_path}: {e}")
        return 0, 2


def should_process_file(file_path: Path) -> bool:
    if file_path.name == 'main.py':
        return False
    if file_path.name.startswith('test_') or file_path.name.endswith('_test.py'):
        return False
    if '__pycache__' in file_path.parts:
        return False
    return True


def scan_and_remove_docstrings(root_path: Path) -> None:
    print("=" * 70)
    print("Docstring Removal Tool")
    print("=" * 70)
    
    target_dirs = ['core', 'config', 'gui', 'state', 'map']
    
    py_files: List[Path] = []
    for target_dir in target_dirs:
        dir_path = root_path / target_dir
        if dir_path.exists():
            py_files.extend(dir_path.rglob('*.py'))
    
    py_files = [f for f in py_files if should_process_file(f)]
    py_files.sort()
    
    if not py_files:
        print("No Python files found to process!")
        return
    
    print(f"Found {len(py_files)} files to process\n")
    
    total_docstrings_removed = 0
    files_processed = 0
    errors = 0
    
    for file_path in py_files:
        rel_path = file_path.relative_to(root_path)
        docstrings_count, error_code = remove_docstrings_from_file(file_path)
        
        if error_code == 0:
            files_processed += 1
            total_docstrings_removed += docstrings_count
            status = f"{docstrings_count} removed" if docstrings_count > 0 else "no docstrings"
            print(f"  {str(rel_path):<50} {status}")
        else:
            errors += 1
            print(f"  {str(rel_path):<50} ERROR")
    
    print("\n" + "=" * 70)
    print(f"Processed: {files_processed}/{len(py_files)}")
    print(f"Total docstrings removed: {total_docstrings_removed}")
    print(f"Errors: {errors}")
    print("=" * 70)


if __name__ == '__main__':
    root = Path.cwd()
    if not root.exists():
        print(f"Error: Path does not exist: {root}")
        sys.exit(1)
    scan_and_remove_docstrings(root)
