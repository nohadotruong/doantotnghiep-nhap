# Error Handling

## Terminal Output Format

Use `print("[TAG]: message")` consistently.
Tag = class or module name in **UPPERCASE**.
Use for debug/progress only — never for return values.

```python
# Info
print("[HAPSO]: Starting hybrid search...")
print("[PSO]: Iteration 42 / 200, best fitness = 3.14")

# Warning
print("[GRID_MAP]: Warning — start equals goal.")

# Error
print("[MAP_SERIALIZER]: Error — file not found:", path)
```

- Tag follows the **file/class** doing the printing, not the caller.
- Remove all print statements before committing production features.

---

## Rules

- No `try`/`except`.
- No `raise`.
- No `hasattr()`.
- Use `print()` for all error and warning reporting.
