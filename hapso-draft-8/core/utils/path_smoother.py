from core.algorithms.base_planner import BasePlanner
from map.grid_map import GridMap

import numpy as np


class PathSmoother:
    @staticmethod
    def smooth(
        path: list[tuple[int, int]],
        grid_map: GridMap | None = None,
        remove_redundant: bool = False,
        transition: bool = False,
        min_clearance: float = 0.0,
    ) -> list[tuple[int, int]]:
        optimized = path
        if remove_redundant:
            optimized = PathSmoother._remove_collinear(optimized)
        if transition and grid_map is not None:
            obstacle_centers = grid_map.get_obstacles_as_centers()
            while True:
                new_optimized = PathSmoother._remove_transition(
                    optimized,
                    grid_map,
                    obstacle_centers,
                    min_clearance,
                )
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
    def _remove_transition(
        path: list[tuple[int, int]],
        grid_map: GridMap,
        obstacle_centers: np.ndarray,
        min_clearance: float,
    ) -> list[tuple[int, int]]:
        if len(path) <= 2:
            return path
        optimized_path = [path[0]]
        i = 1
        while i < len(path) - 1:
            prev_point = optimized_path[-1]
            next_point = path[i + 1]

            if PathSmoother._can_connect(
                prev_point,
                next_point,
                grid_map,
                obstacle_centers,
                min_clearance,
            ):
                i += 1
                continue

            optimized_path.append(path[i])
            i += 1
        optimized_path.append(path[-1])
        return optimized_path

    @staticmethod
    def _can_connect(
        start: tuple[int, int],
        end: tuple[int, int],
        grid_map: GridMap,
        obstacle_centers: np.ndarray,
        min_clearance: float,
    ) -> bool:
        line_cells = BasePlanner._fast_voxel_traversal(
            start[0], start[1], end[0], end[1]
        )

        for cell_x, cell_y in line_cells:
            if grid_map.is_obstacle(cell_x, cell_y):
                return False

        if min_clearance <= 0.0:
            return True

        return PathSmoother._has_safe_clearance(
            start,
            end,
            obstacle_centers,
            min_clearance,
        )

    @staticmethod
    def _has_safe_clearance(
        start: tuple[int, int],
        end: tuple[int, int],
        obstacle_centers: np.ndarray,
        min_clearance: float,
    ) -> bool:
        if min_clearance <= 0.0:
            return True

        if len(obstacle_centers) == 0:
            return True

        sx, sy = start
        ex, ey = end
        # use cell centers for geometric checks
        p1 = np.array([float(sx) + 0.5, float(sy) + 0.5])
        p2 = np.array([float(ex) + 0.5, float(ey) + 0.5])
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        length_sq = vx * vx + vy * vy

        if length_sq < 1e-09:
            distances = np.linalg.norm(obstacle_centers - p1, axis=1)
            return float(np.min(distances)) >= min_clearance

        segment_vector = np.array([float(vx), float(vy)])
        projection_param = np.clip(
            np.dot(obstacle_centers - p1, segment_vector) / length_sq, 0.0, 1.0
        )
        proj = p1 + projection_param[:, np.newaxis] * segment_vector
        distances = np.linalg.norm(obstacle_centers - proj, axis=1)

        return float(np.min(distances)) >= min_clearance


def optimize_path(path, remove_redundant=False, transition=False, grid_map=None):
    return PathSmoother.smooth(
        path,
        grid_map=grid_map,
        remove_redundant=remove_redundant,
        transition=transition,
    )


def remove_redundant_points(path):
    return PathSmoother._remove_collinear(path)


def remove_transition_redundant_points(path, grid_map=None):
    if grid_map is None:
        return path
    obstacle_centers = grid_map.get_obstacles_as_centers()
    return PathSmoother._remove_transition(path, grid_map, obstacle_centers, 0.0)
