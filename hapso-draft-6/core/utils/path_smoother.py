class PathSmoother:
    @staticmethod
    def smooth(
        path: list[tuple[int, int]],
        grid_map: object | None = None,
        remove_redundant: bool = False,
        remove_transitive: bool = False,
    ) -> list[tuple[int, int]]:
        optimized = path
        if remove_redundant:
            optimized = PathSmoother._remove_collinear(optimized)
        if remove_transitive and grid_map is not None:
            while True:
                new_optimized = PathSmoother._remove_transitive(optimized, grid_map)
                if len(new_optimized) == len(optimized):
                    break
                optimized = new_optimized
        return optimized

    @staticmethod
    def _remove_collinear(path: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if len(path) <= 2:
            return path
        optimized_path = [path[0]]
        i = 1
        while i < len(path) - 1:
            x_prev, y_prev = optimized_path[-1]
            x_curr, y_curr = path[i]
            x_next, y_next = path[i + 1]
            v1_x = x_curr - x_prev
            v1_y = y_curr - y_prev
            v2_x = x_next - x_prev
            v2_y = y_next - y_prev
            cross_product = v1_x * v2_y - v1_y * v2_x
            is_collinear = abs(cross_product) < 1e-09
            if not is_collinear:
                optimized_path.append((x_curr, y_curr))
            i += 1
        optimized_path.append(path[-1])
        return optimized_path

    @staticmethod
    def _remove_transitive(
        path: list[tuple[int, int]], grid_map: object
    ) -> list[tuple[int, int]]:
        if len(path) <= 2:
            return path
        optimized_path = [path[0]]
        i = 1
        while i < len(path) - 1:
            prev_point = optimized_path[-1]
            curr_point = path[i]
            next_point = path[i + 1]
            x_prev, y_prev = prev_point
            x_next, y_next = next_point

            line_cells = PathSmoother._bresenham_line(x_prev, y_prev, x_next, y_next)

            has_obstacle_on_direct_path = False
            for cell_x, cell_y in line_cells:
                if grid_map.is_obstacle(cell_x, cell_y):
                    has_obstacle_on_direct_path = True
                    break
            if has_obstacle_on_direct_path:
                line_to_curr = PathSmoother._bresenham_line(
                    x_prev, y_prev, curr_point[0], curr_point[1]
                )
                prev_to_curr_clear = all(
                    (not grid_map.is_obstacle(cx, cy) for cx, cy in line_to_curr)
                )
                if prev_to_curr_clear:
                    optimized_path.append(curr_point)
                else:
                    optimized_path.append(path[i - 1])
                    optimized_path.append(curr_point)
            i += 1
        optimized_path.append(path[-1])
        return optimized_path

    @staticmethod
    def _bresenham_line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points


def optimize_path(path, remove_redundant=False, remove_transitive=False, grid_map=None):
    return PathSmoother.smooth(
        path,
        grid_map=grid_map,
        remove_redundant=remove_redundant,
        remove_transitive=remove_transitive,
    )


def remove_redundant_points(path):
    return PathSmoother._remove_collinear(path)


def remove_transitive_redundant_points(path, grid_map=None):
    if grid_map is None:
        return path
    return PathSmoother._remove_transitive(path, grid_map)
