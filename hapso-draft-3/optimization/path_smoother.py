from .line_drawing import LineDrawer


class PathSmoother:
    COLLINEARITY_TOLERANCE = 1e-09

    def __init__(self, grid_map: "GridMap") -> None:
        self.grid_map = grid_map

    def smooth(
        self, path: list, remove_redundant: bool = True, remove_transitive: bool = True
    ) -> list:
        if len(path) <= 2:
            return path

        if remove_redundant:
            path = self.remove_redundant_points(path)

        if remove_transitive:
            path = self.remove_transitive_redundant_points(path)

        return path

    def remove_redundant_points(self, path: list) -> list:
        if len(path) <= 2:
            return path

        optimized_path = [path[0]]
        index = 1

        while index < len(path) - 1:
            prev_point = optimized_path[-1]
            curr_point = path[index]
            next_point = path[index + 1]

            (prev_x, prev_y) = prev_point
            (curr_x, curr_y) = curr_point
            (next_x, next_y) = next_point

            vector1_x = curr_x - prev_x
            vector1_y = curr_y - prev_y
            vector2_x = next_x - prev_x
            vector2_y = next_y - prev_y

            if (
                not abs(vector1_x * vector2_y - vector1_y * vector2_x)
                < self.COLLINEARITY_TOLERANCE
            ):
                optimized_path.append(curr_point)

            index += 1

        optimized_path.append(path[-1])
        return optimized_path

    def remove_transitive_redundant_points(self, path: list) -> list:
        if len(path) <= 2:
            return path

        optimized_path = [path[0]]
        index = 1

        while index < len(path) - 1:
            prev_point = optimized_path[-1]
            curr_point = path[index]
            next_point = path[index + 1]

            (prev_x, prev_y) = prev_point
            (next_x, next_y) = next_point

            line_cells = LineDrawer.voxel_traversal((prev_x, prev_y), (next_x, next_y))
            has_obstacle_on_direct_path = False

            for cell_pos_x, cell_pos_y in line_cells:
                if self.grid_map.is_obstacle(cell_pos_x, cell_pos_y):
                    has_obstacle_on_direct_path = True
                    break

            if has_obstacle_on_direct_path:
                line_to_curr = LineDrawer.voxel_traversal(
                    (prev_x, prev_y), (curr_point[0], curr_point[1])
                )
                prev_to_curr_clear = all(
                    (
                        not self.grid_map.is_obstacle(cell_x, cell_y)
                        for (cell_x, cell_y) in line_to_curr
                    )
                )

                if prev_to_curr_clear:
                    optimized_path.append(curr_point)
                else:
                    optimized_path.append(path[index - 1])
                    optimized_path.append(curr_point)

            index += 1

        optimized_path.append(path[-1])
        return optimized_path
