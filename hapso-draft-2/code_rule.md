# HAPSO — Code Rules

## Table of Contents

1. [Naming Conventions](#1-naming-conventions)
2. [Terminal Output](#2-terminal-output)
3. [Import Sorting](#3-import-sorting)
4. [Class Structure & Method Sorting](#4-class-structure--method-sorting)
5. [File & Module Organization](#5-file--module-organization)
6. [Comments & Docstrings](#6-comments--docstrings)
7. [Type Hints](#7-type-hints)

---

## 1. Naming Conventions

### 1.1. Variables

- Use `snake_case`.
- Name should describe **what it holds**, not its type.
- Boolean variables use `is_`, `has_`, `can_`, `use_` prefix.
- Loop counters: single letter only inside short loops (`i`, `j`, `k`).
  - `k` is reserved for PSO iteration index (consistent with literature).

```python
# Good
path_length = 42.5
is_obstacle = True
use_siw = False
w_min = 0.4
(start_x, start_y) = start

# Bad
pl = 42.5
obstacleFlag = True
SIW = False
(sx, sy) = start
```

### 1.2. Constants

- Use `UPPER_SNAKE_CASE`.
- Define in `config.py`, never hardcode inline.

```python
GRID_SIZE = 30
GRID_CELL_SIZE = 20
COLOR_WHITE = (255, 255, 255)
```

### 1.3. Functions

- Use `snake_case`.
- Start with a **verb** that describes the action.
- Private helpers prefix with single underscore `_`.

| Prefix       | Use case                                     |
| ------------ | -------------------------------------------- |
| `get_`       | Return a value, no side effect               |
| `set_`       | Mutate state, return None                    |
| `find_`      | Search and return result (may return None)   |
| `build_`     | Construct and return an object               |
| `run_`       | Execute a process with side effects          |
| `is_`/`has_` | Return bool                                  |
| `_`          | Private helper, not part of public interface |

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

### 1.4. Classes

- Use `PascalCase`.
- Name should be a **noun** (thing), not a verb.
- Abstract base classes do **not** use `Abstract` or `Base` prefix — use the plain concept name and mark with `ABC`.

```python
# Good
class GridMap: ...
class PathSmoother: ...
class InertiaWeight(ABC): ...
class SOBL: ...

# Bad
class GridMapClass: ...
class AbstractPlanner: ...
class BaseInertiaWeight: ...
```

### 1.5. Files & Modules

- Use `snake_case`.
- Name reflects the **primary class or responsibility** inside.

```
grid_map.py       ← contains GridMap
path_smoother.py  ← contains PathSmoother
pso_strategies.py ← contains InertiaWeight + SOBL
```

### 1.6. Parameters

- Use same conventions as variables.
- Prefer full words over abbreviations, **except** established domain terms.

| Allowed abbreviation | Meaning                           |
| -------------------- | --------------------------------- |
| `w`                  | Inertia weight                    |
| `c1`, `c2`           | PSO cognitive/social coefficients |
| `k`                  | Current PSO iteration             |
| `t_max`              | Max iterations                    |
| `lb`, `ub`           | Lower/upper bound                 |
| `dx`, `dy`           | Delta x, delta y                  |

---

## 2. Terminal Output

- Use `print("[TAG]: message")` format consistently.
- Tag is the **class or module name** in uppercase.
- Use for debug/progress only — never for return values.

```python
# Info
print("[HAPSO]: Starting hybrid search...")
print("[PSO]: Iteration 42 / 200, best fitness = 3.14")

# Warning
print("[GRID_MAP]: Warning — start equals goal.")

# Error
print("[MAP_SERIALIZER]: Error — file not found:", path)
```

- Tags follow the **file/class** doing the printing, not the caller.
- Remove all print statements before committing production features.

---

## 3. Import Sorting

### 3.1. Library & Package Imports

Order: `from ... import ...` → `import ...`.  
Sort all imports alphabetically (A–Z) by module name.  
No grouping between standard library, third-party, or local modules.

````python
from algorithms.base_planner import BasePlanner
from collections import defaultdict
from map.grid_map import GridMap
from math import sqrt
from numpy import ndarray
from typing import Optional

import config
import numpy as np
import pygame

### 3.2. Style Config Imports

Sort by **group/type** first, then A–Z within each group.
Groups (in order): `COLOR_` → `FONT_` → `SIZE_` → other.

```python
from config import (
    COLOR_BLACK,
    COLOR_DARK_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    FONT_LABEL,
    FONT_TITLE,
    SIZE_BUTTON,
    SIZE_PANEL,
)
````

### 3.3. Window / Layout Config Imports

Sort by **active-flow window order** (the order pages/panels appear in the app).

```python
from config import (
    F1_MENU_WIDTH,
    F1_MENU_HEIGHT,
    F2_MENU_WIDTH,
    F2_MENU_HEIGHT,
    F3_MENU_WIDTH,
    F3_MENU_HEIGHT,
)
```

---

## 4. Class Structure & Method Sorting

### 4.1. General Class Layout

Every class follows this top-down order:

```
1. Class-level constants / ClassVar
2. __init__
3. Public methods
4. Private methods (_)
5. Static methods / class methods
6. __repr__ / __str__ (if needed)
```

### 4.2. Planner Classes (AStar, PSOPlanner, APSO, HAPSO)

Order reflects the **execution flow** — read top to bottom = understand how the algorithm runs.

```
1. __init__
2. find_path          ← public entry point
3. Methods in the order find_path() calls them
4. _heuristic, _fitness, _reconstruct_path  ← leaf helpers, last
```

```python
class HAPSO(BasePlanner):
    def __init__(self, grid, n_particles, max_iter, ...): ...

    def find_path(self, start, goal): ...      # entry point

    def _run_astar(self, start, goal): ...     # called first in find_path
    def _run_optimizer(self, path): ...        # called second

    def _fitness(self, path): ...              # used inside _run_optimizer
    def _segment_collision_count(self, p1, p2): ...  # used inside _fitness
```

### 4.3. Util / Strategy Classes (InertiaWeight, PathSmoother, LineDrawer)

Sort **public methods A–Z**, private helpers after.

```python
class InertiaWeight:
    @staticmethod
    def aiw(...): ...

    @staticmethod
    def ldiw(...): ...

    @staticmethod
    def ndiw(...): ...

    @staticmethod
    def siw(...): ...
```

```python
class PathSmoother:
    def smooth(self, path, **options): ...      # public entry, always first

    def _remove_collinear(self, path): ...      # A < R, but smooth() is entry
    def _remove_transitive(self, path): ...
```

### 4.4. Serializer / IO Classes (MapSerializer, ResultSerializer)

Order: `load` before `save` (read before write convention).

```python
class MapSerializer:
    @staticmethod
    def load(path) -> GridMap: ...

    @staticmethod
    def save(grid_map, path): ...
```

### 4.5. Page / Renderer Classes (F1EditorPage, Renderer)

Order reflects **draw call order** in the render loop.

```
1. __init__
2. draw / render       ← top-level draw entry
3. draw_menu
4. draw_info_panel
5. draw_grid_area
6. Private helpers
```

---

## 5. File & Module Organization

### 5.1. One Responsibility Per File

A file should have **one reason to change**. If you find yourself writing "and" when describing what a file does, split it.

```
# Good
map/grid_map.py         ← "manages the grid model"
map/map_serializer.py   ← "saves and loads grid maps"

# Bad
map/grid_map.py         ← "manages the grid AND saves/loads maps"
```

### 5.2. Private Helpers Stay Close to Their Caller

Do not move a helper to a shared module until **two or more** unrelated callers need it.

```python
# _segment_collision_count is only used by PSO fitness
# → keep it in pso.py, not in a shared utils
```

### 5.3. No Circular Imports

Allowed import directions only (top → bottom):

```
gui  →  algorithms, optimization, map, analytics
algorithms  →  map
analytics  →  algorithms, map
optimization  →  (nothing from this project)
map  →  (nothing from this project)
```

---

## 6. Comments & Docstrings - NOT NOW

### 6.1. Docstrings

- All public classes and public methods get a one-line docstring.
- Use imperative mood ("Return the path", not "Returns the path").
- Complex methods add parameter and return description.

```python
def find_path(self, start: tuple, goal: tuple) -> list:
    """Find the optimal path from start to goal using A*.

    Args:
        start: (x, y) grid coordinate.
        goal:  (x, y) grid coordinate.

    Returns:
        List of (x, y) tuples, empty list if no path found.
    """
```

### 6.2. Inline Comments

- Explain **why**, not what.
- Place above the line, not trailing (unless very short).
- Use for non-obvious algorithm steps, referencing paper/formula if applicable.

```python
# Diagonal cost = sqrt(2) ≈ 1.414 (Euclidean distance)
DIAGONAL_COST = 1.414

# Clamp r away from 0 and 1 to avoid degenerate opposite points
r = max(1e-6, min(1.0 - 1e-6, r))
```

### 6.3. Section Separators (within long files only)

Use only when a file has clearly distinct sections (e.g. `pso_strategies.py`).

```python
# ---------------------------------------------------------------------------
# Inertia weight strategies
# ---------------------------------------------------------------------------

class InertiaWeight: ...

# ---------------------------------------------------------------------------
# Opposite-based learning
# ---------------------------------------------------------------------------

class SOBL: ...
```

---

## 7. Type Hints

### 7.1. Always annotate public method signatures.

```python
def find_path(self, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]: ...
def get_obstacles(self) -> list[tuple[int, int]]: ...
def is_walkable(self, x: int, y: int) -> bool: ...
```

### 7.2. Use `Optional` for values that can be None.

```python
from typing import Optional

def find_path(self, start, goal) -> Optional[list[tuple[int, int]]]:
    """Return None if no path exists."""
```

### 7.3. Class attributes annotate in `__init__` or as ClassVar.

```python
class PSOPlanner(BasePlanner):
    def __init__(self, grid: list[list[int]], n_particles: int = 20) -> None:
        self.grid = grid
        self.n_particles = n_particles
        self.best_path: list[tuple[int, int]] = []
```

### 7.4. Do not over-annotate private helpers.

Private methods with obvious types from context may omit annotations to reduce noise.

```python
def _sample_r(self):          # obvious: returns float, takes nothing
    return random.gauss(self.mu, self.sigma)
```
