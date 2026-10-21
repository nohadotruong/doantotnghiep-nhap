from typing import List, Tuple
import math


class PathMetrics:
    V_M = 1.0
    T_P = 0.2
    V_I = math.pi

    @staticmethod
    def calculate_metrics(
        path: List[Tuple[int, int]], execution_time: float = 0.0
    ) -> dict:
        min_d = PathMetrics.calculate_path_length(path)
        min_p = PathMetrics.calculate_path_points(path)
        min_i = PathMetrics.calculate_turning_amplitude(path)
        min_c = execution_time
        min_t = (
            min_d / PathMetrics.V_M
            + min_p * PathMetrics.T_P
            + min_i / PathMetrics.V_I
            + min_c
        )
        return {
            "min_d": min_d,
            "min_p": min_p,
            "min_i": min_i,
            "min_c": min_c,
            "min_t": min_t,
            "time_movement": min_d / PathMetrics.V_M,
            "time_decision": min_p * PathMetrics.T_P,
            "time_turning": min_i / PathMetrics.V_I,
            "time_algorithm": min_c,
        }

    @staticmethod
    def calculate_path_length(path: List[Tuple[int, int]]) -> float:
        if not path or len(path) < 2:
            return 0.0
        total_distance = 0.0
        for i in range(len(path) - 1):
            (x1, y1) = path[i]
            (x2, y2) = path[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            distance = math.sqrt(dx * dx + dy * dy)
            total_distance += distance
        return total_distance

    @staticmethod
    def calculate_path_points(path: List[Tuple[int, int]]) -> int:
        return len(path) if path else 0

    @staticmethod
    def calculate_turning_amplitude(path: List[Tuple[int, int]]) -> float:
        if not path or len(path) < 3:
            return 0.0
        total_angle = 0.0
        for i in range(1, len(path) - 1):
            (x1, y1) = path[i - 1]
            (x2, y2) = path[i]
            (x3, y3) = path[i + 1]
            angle = PathMetrics._calculate_angle_difference(x1, y1, x2, y2, x3, y3)
            total_angle += angle
        return total_angle

    @staticmethod
    def format_metrics(metrics: dict) -> List[str]:
        lines = [
            f"Path Length (minD): {metrics['min_d']:.2f} units",
            f"Waypoints (minP): {metrics['min_p']}",
            f"Turning Angle (minI): {math.degrees(metrics['min_i']):.2f} deg",
            f"Algorithm Time (minC): {metrics['min_c']:.4f}s",
            "",
            "Time Components:",
            f"  Linear Movement: {metrics['time_movement']:.4f}s",
            f"  Waypoint Decisions: {metrics['time_decision']:.4f}s",
            f"  Turning: {metrics['time_turning']:.4f}s",
            f"  Algorithm Compute: {metrics['time_algorithm']:.4f}s",
            "",
            f"Total Time (minT): {metrics['min_t']:.4f}s",
        ]
        return lines

    @staticmethod
    def _calculate_angle_difference(
        x1: int, y1: int, x2: int, y2: int, x3: int, y3: int
    ) -> float:
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x3 - x2
        dy2 = y3 - y2
        if dx1 == 0 and dy1 == 0:
            return 0.0
        if dx2 == 0 and dy2 == 0:
            return 0.0
        if dx1 == 0:
            slope1 = float("inf") if dy1 > 0 else float("-inf")
        else:
            slope1 = dy1 / dx1
        if dx2 == 0:
            slope2 = float("inf") if dy2 > 0 else float("-inf")
        else:
            slope2 = dy2 / dx2
        if slope1 == float("inf") or slope1 == float("-inf"):
            angle1 = math.pi / 2 if slope1 > 0 else -math.pi / 2
        else:
            angle1 = math.atan(slope1)
        if slope2 == float("inf") or slope2 == float("-inf"):
            angle2 = math.pi / 2 if slope2 > 0 else -math.pi / 2
        else:
            angle2 = math.atan(slope2)
        angle_diff = angle1 - angle2
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        return abs(angle_diff)
