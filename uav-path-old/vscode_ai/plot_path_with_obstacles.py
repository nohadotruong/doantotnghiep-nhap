import math
import random
from heapq import heappush, heappop

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def generate_obstacles(width, height, n=40, r_min=2, r_max=8, seed=None):
    if seed is not None:
        random.seed(seed)
    obs = []
    for _ in range(n):
        r = random.uniform(r_min, r_max)
        x = random.uniform(r, width - r)
        y = random.uniform(r, height - r)
        obs.append((x, y, r))
    return obs


def build_occupancy_grid(width, height, obstacles, resolution=1):
    w = int(width / resolution)
    h = int(height / resolution)
    grid = np.zeros((h, w), dtype=np.uint8)
    xs = (np.arange(w) + 0.5) * resolution
    ys = (np.arange(h) + 0.5) * resolution
    xv, yv = np.meshgrid(xs, ys)
    for (cx, cy, r) in obstacles:
        mask = (xv - cx) ** 2 + (yv - cy) ** 2 <= r * r
        grid[mask] = 1
    return grid


def neighbors(pos, grid):
    x, y = pos
    h, w = grid.shape
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                cost = math.hypot(dx, dy)
                yield (nx, ny, cost)


def heuristic(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def a_star(grid, start, goal):
    h, w = grid.shape
    sx, sy = start
    gx, gy = goal
    open_heap = []
    heappush(open_heap, (0 + heuristic(start, goal), 0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while open_heap:
        _, g, current = heappop(open_heap)
        if current == goal:
            break
        for nx, ny, move_cost in neighbors(current, grid):
            new_cost = g + move_cost
            neigh = (nx, ny)
            if neigh not in cost_so_far or new_cost < cost_so_far[neigh]:
                cost_so_far[neigh] = new_cost
                priority = new_cost + heuristic(neigh, goal)
                heappush(open_heap, (priority, new_cost, neigh))
                came_from[neigh] = current

    if goal not in came_from:
        return None
    # reconstruct
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path


def bresenham_line(p0, p1):
    x0, y0 = p0
    x1, y1 = p1
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            yield (x, y)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            yield (x, y)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    yield (x1, y1)


def line_of_sight(a, b, grid):
    for px, py in bresenham_line(a, b):
        if grid[py, px]:
            return False
    return True


def smooth_path(path, grid):
    if not path:
        return path
    new_path = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1:
            if line_of_sight(path[i], path[j], grid):
                break
            j -= 1
        new_path.append(path[j])
        i = j
    return new_path


def grid_to_world(pt, resolution=1):
    x, y = pt
    return (x + 0.5) * resolution, (y + 0.5) * resolution


def main():
    width, height = 100, 100
    resolution = 1
    obstacles = generate_obstacles(width, height, n=60, r_min=2.5, r_max=8, seed=42)
    grid = build_occupancy_grid(width, height, obstacles, resolution=resolution)

    # pick start and goal in free space
    h, w = grid.shape
    def random_free():
        while True:
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            if grid[y, x] == 0:
                return (x, y)

    start = random_free()
    goal = random_free()

    print(f"Start: {start}, Goal: {goal}")
    path = a_star(grid, start, goal)
    if path is None:
        print("No path found, try rerunning or reduce obstacles")
        return
    smooth = smooth_path(path, grid)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')

    # draw obstacles
    for (cx, cy, r) in obstacles:
        c = patches.Circle((cx, cy), r, color='gray', alpha=0.8)
        ax.add_patch(c)

    # draw occupancy as faint pixels (optional)
    # ax.imshow(grid, origin='lower', cmap='Greys', extent=[0, width, 0, height], alpha=0.15)

    # plot raw path
    wx = [grid_to_world(p, resolution)[0] for p in path]
    wy = [grid_to_world(p, resolution)[1] for p in path]
    ax.plot(wx, wy, color='orange', linewidth=1.5, label='A* path')

    # plot smoothed path
    swx = [grid_to_world(p, resolution)[0] for p in smooth]
    swy = [grid_to_world(p, resolution)[1] for p in smooth]
    ax.plot(swx, swy, color='red', linewidth=2.5, label='Smoothed')

    # start/goal
    sx, sy = grid_to_world(start, resolution)
    gx, gy = grid_to_world(goal, resolution)
    ax.scatter([sx], [sy], c='green', s=80, marker='o', label='Start')
    ax.scatter([gx], [gy], c='blue', s=80, marker='X', label='Goal')

    ax.legend()
    ax.set_title('Path with Many Obstacles')
    plt.tight_layout()
    plt.savefig('path_with_obstacles.png', dpi=200)
    print('Saved path_with_obstacles.png')
    plt.show()


if __name__ == '__main__':
    main()
