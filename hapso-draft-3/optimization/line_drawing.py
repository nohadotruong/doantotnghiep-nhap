from typing import List, Optional, Tuple


class LineDrawer:

    @staticmethod
    def compare_methods(start: Tuple[int, int], end: Tuple[int, int]) -> dict:
        return {
            "bresenham",
            LineDrawer.bresenham(start, end),
            "dda",
            LineDrawer.dda(start, end),
            "sample_line",
            LineDrawer.sample_line(start, end),
            "supercover_line",
            LineDrawer.supercover_line(start, end),
            "voxel_traversal",
            LineDrawer.voxel_traversal(start, end),
        }

    @staticmethod
    def bresenham(
        start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        (start_x, start_y) = (int(start[0]), int(start[1]))
        (end_x, end_y) = (int(end[0]), int(end[1]))
        cells = []

        dx = end_x - start_x
        dy = end_y - start_y
        discriminant = 2 * dy - dx
        line_y = start_y

        for line_x in range(start_x, end_x + 1):
            cells.append((line_x, line_y))

            if discriminant > 0:
                line_y += 1
                discriminant += 2 * (dy - dx)
            else:
                discriminant += 2 * dy

        cells = set(cells)
        cells = sorted(cells)
        return cells

    @staticmethod
    def dda(start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        (start_x, start_y) = (int(start[0]), int(start[1]))
        (end_x, end_y) = (int(end[0]), int(end[1]))
        cells = []

        dx = end_x - start_x
        dy = end_y - start_y

        steps = max(abs(dx), abs(dy))

        x_inc = dx / steps
        y_inc = dy / steps

        line_x = start_x
        line_y = start_y

        for _ in range(steps + 1):
            cells.append((round(line_x), round(line_y)))
            line_x += x_inc
            line_y += y_inc

        cells = set(cells)
        cells = sorted(cells)
        return cells

    # @staticmethod
    # def line_vs_aabb(
    #     start: Tuple[int, int], end: Tuple[int, int], obstalces: List
    # ) -> List[Tuple[int, int]]:
    #     (x1, y1) = (int(start[0]), int(start[1]))
    #     (x2, y2) = (int(end[0]), int(end[1]))
    #     cells = []

    @staticmethod
    def sample_line(
        start: Tuple[int, int], end: Tuple[int, int], step=0.1
    ) -> List[Tuple[int, int]]:
        (start_x, start_y) = (int(start[0]), int(start[1]))
        (end_x, end_y) = (int(end[0]), int(end[1]))
        cells = []
        interpolation_t = 0.0

        while interpolation_t <= 1.0:
            line_x = start_x + interpolation_t * (end_x - start_x)
            line_y = start_y + interpolation_t * (end_y - start_y)

            cell = (int(line_x), int(line_y))
            cells.append(cell)

            interpolation_t += step

        cells = set(cells)
        cells = sorted(cells)
        return cells

    @staticmethod
    def supercover_line(start: Tuple[int, int], end: Tuple[int, int]):
        (start_x, start_y) = (int(start[0]), int(start[1]))
        (end_x, end_y) = (int(end[0]), int(end[1]))
        cells = []

        dx = end_x - start_x
        dy = end_y - start_y

        step_count_x = abs(dx)
        step_count_y = abs(dy)

        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1

        current_x, current_y = start_x, start_y
        index_x, index_y = 0, 0

        cells = [(current_x, current_y)]

        while index_x < step_count_x or index_y < step_count_y:
            if (1 + 2 * index_x) * step_count_y == (1 + 2 * index_y) * step_count_x:
                current_x += step_x
                current_y += step_y
                index_x += 1
                index_y += 1

            elif (1 + 2 * index_x) * step_count_y < (1 + 2 * index_y) * step_count_x:
                current_x += step_x
                index_x += 1

            else:
                current_y += step_y
                index_y += 1

            cells.append((current_x, current_y))

        cells = set(cells)
        cells = sorted(cells)
        return cells

    @staticmethod
    def voxel_traversal(
        start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        (start_x, start_y) = (int(start[0]), int(start[1]))
        (end_x, end_y) = (int(end[0]), int(end[1]))
        cells = []

        dx = end_x - start_x
        dy = end_y - start_y

        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1

        traversal_delta_x = abs(1 / dx) if dx != 0 else float("inf")
        traversal_delta_y = abs(1 / dy) if dy != 0 else float("inf")

        current_x = int(start_x)
        current_y = int(start_y)

        if dx > 0:
            t_max_x = (current_x + 1 - start_x) / dx
        else:
            t_max_x = (start_x - current_x) / -dx

        if dy > 0:
            t_max_y = (current_y + 1 - start_y) / dy
        else:
            t_max_y = (start_y - current_y) / -dy

        while (current_x, current_y) != (int(end_x), int(end_y)):
            cells.append((current_x, current_y))

            if t_max_x < t_max_y:
                current_x += step_x
                t_max_x += traversal_delta_x
            else:
                current_y += step_y
                t_max_y += traversal_delta_y

        cells.append((int(end_x), int(end_y)))
        cells = set(cells)
        cells = sorted(cells)
        return cells
