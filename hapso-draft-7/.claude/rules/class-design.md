# Class Design

## Default Parameters in `__init__`

All configurable parameters are defined with default values **inside `__init__`**.
When instantiating a class from outside, **do not pass any arguments** — use the defaults as-is.
If a value needs changing, modify the default in `__init__`, not at the call site.

```python
# Good — defaults live in __init__
class PSOPlanner(BasePlanner):
    def __init__(self, grid_map: list[list[int]], n_particles: int = 30,
                 max_iter: int = 200, w: float = 0.7,
                 c1: float = 1.5, c2: float = 1.5) -> None:
        self.grid_map = grid_map
        self.n_particles = n_particles
        self.max_iter = max_iter

# Good — instantiate with no tuning arguments
planner = PSOPlanner(grid_map)

# Bad — tuning parameters set at the call site
planner = PSOPlanner(grid_map, n_particles=50, w=0.4)
```

---

## General Class Layout

Every class follows this top-down order:

```
1. Class-level constants / ClassVar
2. __init__
3. Public methods
4. Private methods (_)
5. Static methods / class methods
6. __repr__ / __str__ (if needed)
```

---

## Planner Classes (AStar, PSOPlanner, APSO, HAPSO)

Order reflects **execution flow** — read top to bottom = understand how the algorithm runs.

```
1. __init__
2. find_path          ← public entry point
3. Methods in call order from find_path()
4. Leaf helpers last  ← _heuristic, _fitness, _reconstruct_path
```

```python
class HAPSO(BasePlanner):
    def __init__(self, grid_map, n_particles: int = 30, max_iter: int = 200) -> None: ...

    def find_path(self, start, goal): ...

    def _run_astar(self, start, goal): ...
    def _run_optimizer(self, path): ...

    def _fitness(self, path): ...
    def _segment_collision_count(self, p1, p2): ...
```

---

## Util / Strategy Classes (InertiaWeight, PathSmoother, LineDrawer)

Public methods sorted A–Z. Private helpers after.

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
    def smooth(self, path, **options): ...   # entry point, always first

    def _remove_collinear(self, path): ...
    def _remove_transitive(self, path): ...
```

---

## Serializer / IO Classes

Order: `load` before `save` (read before write).

```python
class MapSerializer:
    @staticmethod
    def load(path) -> GridMap: ...

    @staticmethod
    def save(grid_map, path): ...
```

---

## Page / Renderer Classes

Order reflects **draw call order** in the render loop.

```
1. __init__
2. draw / render
3. draw_menu
4. draw_info_panel
5. draw_grid_area
6. Private helpers
```
