# Code Style

## Naming — Variables

- Use `snake_case`.
- Name describes **what it holds**, not its type.
- Booleans use prefix: `is_`, `has_`, `can_`, `use_`.
- Loop counters: single letter only (`i`, `j`, `k`).
  - `k` is reserved for PSO iteration index.

```python
# Good
path_length = 42.5
is_obstacle = True
use_siw = False
(start_x, start_y) = start

# Bad
pl = 42.5
obstacleFlag = True
SIW = False
(sx, sy) = start
```

## Naming — Constants

- Use `UPPER_SNAKE_CASE`.
- Define in `config.py`. Never hardcode inline.

```python
GRID_SIZE = 30
GRID_CELL_SIZE = 20
COLOR_WHITE = (255, 255, 255)
```

## Naming — Functions

- Use `snake_case`. Start with a **verb**.
- Private helpers prefix with single underscore `_`.

| Prefix       | Use case                                   |
|--------------|--------------------------------------------|
| `get_`       | Return a value, no side effect             |
| `set_`       | Mutate state, return None                  |
| `find_`      | Search and return result (may return None) |
| `build_`     | Construct and return an object             |
| `run_`       | Execute a process with side effects        |
| `is_`/`has_` | Return bool                                |
| `_`          | Private helper, not part of public API     |

```python
# Good
def find_path(start, goal): ...
def get_obstacles(): ...
def is_walkable(x, y): ...
def _reconstruct_path(node): ...

# Bad
def path(start, goal): ...
def obstacles(): ...
def walkable_check(x, y): ...
```

## Naming — Classes

- Use `PascalCase`. Name is a **noun**, not a verb.
- Abstract base classes: plain concept name + `ABC`. No `Abstract`/`Base` prefix.

```python
# Good
class GridMap: ...
class PathSmoother: ...
class InertiaWeight(ABC): ...

# Bad
class AbstractPlanner: ...
class BaseInertiaWeight: ...
```

## Naming — Files & Modules

- Use `snake_case`. Name reflects primary class or responsibility.

```
grid_map.py       ← contains GridMap
path_smoother.py  ← contains PathSmoother
pso_strategies.py ← contains InertiaWeight + SOBL
```

## Naming — Parameters

Same conventions as variables. Prefer full words, except established domain terms.

| Abbreviation | Meaning                           |
|--------------|-----------------------------------|
| `w`          | Inertia weight                    |
| `c1`, `c2`   | PSO cognitive/social coefficients |
| `k`          | Current PSO iteration             |
| `t_max`      | Max iterations                    |
| `lb`, `ub`   | Lower/upper bound                 |
| `dx`, `dy`   | Delta x, delta y                  |

---

## Import Sorting

Order: `from ... import ...` → `import ...`.
Sort all imports alphabetically (A–Z) by module name.
No groups. No comments in the import section.

```python
from algorithms.base_planner import BasePlanner
from collections import defaultdict
from map.grid_map import GridMap
from math import sqrt
from typing import Optional

import config
import numpy as np
import pygame
```

Config imports — sort alphabetically, no grouping, no comments:

```python
from config import (
    COLOR_BLACK,
    COLOR_DARK_GRAY,
    COLOR_WHITE,
    FONT_LABEL,
    FONT_TITLE,
)
```

---

## Type Hints

Always annotate public method signatures:

```python
def find_path(self, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]: ...
def is_walkable(self, x: int, y: int) -> bool: ...
```

Use `Optional` for values that can be None:

```python
def find_path(self, start, goal) -> Optional[list[tuple[int, int]]]:
    """Return None if no path exists."""
```

Annotate class attributes in `__init__` or as `ClassVar`:

```python
class PSOPlanner(BasePlanner):
    def __init__(self, grid_map: list[list[int]], n_particles: int = 20) -> None:
        self.grid_map = grid_map
        self.best_path: list[tuple[int, int]] = []
```

Private helpers with obvious types may omit annotations to reduce noise.

---

## General Rules

- NO COMMENTS, NO DOCSTRINGS.
- Use `start`/`goal`. Not `start`/`end`.
- Use `grid_map`, not `grid`.
- No `hasattr()`.
