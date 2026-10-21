from typing import List, Tuple


def bresenham_line(
    p1: Tuple[float, float], p2: Tuple[float, float]
) -> List[Tuple[int, int]]:
    x0, y0 = int(round(p1[0])), int(round(p1[1]))
    x1, y1 = int(round(p2[0])), int(round(p2[1]))

    cells = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    if dx > dy:
        err = dx / 2.0
        y = y0
        for x in range(x0, x1 + sx, sx):
            cells.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
    else:
        err = dy / 2.0
        x = x0
        for y in range(y0, y1 + sy, sy):
            cells.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy

    return cells
