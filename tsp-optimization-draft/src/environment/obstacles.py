"""
Module: Obstacles
Purpose: Define and manage obstacles in the environment
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import List, Tuple, Union


class Obstacle(ABC):
    """Base class for obstacles"""

    @abstractmethod
    def contains_point(self, point: np.ndarray) -> bool:
        """Check if point is inside obstacle"""
        pass

    @abstractmethod
    def distance_to_point(self, point: np.ndarray) -> float:
        """Calculate distance from obstacle to point"""
        pass

    @abstractmethod
    def collides_with_line(
        self, p1: np.ndarray, p2: np.ndarray, clearance: float = 0.0
    ) -> bool:
        """Check if line segment collides with obstacle"""
        pass


class CircleObstacle(Obstacle):
    """Circular obstacle"""

    def __init__(self, center: Union[List, np.ndarray], radius: float):
        """
        Initialize circular obstacle

        Args:
            center: Center coordinates [x, y]
            radius: Radius of circle
        """
        self.center = np.array(center, dtype=float)
        self.radius = float(radius)

    def contains_point(self, point: np.ndarray) -> bool:
        """Check if point is inside circle"""
        dist = np.linalg.norm(point - self.center)
        return dist < self.radius

    def distance_to_point(self, point: np.ndarray) -> float:
        """Distance from point to obstacle surface"""
        dist = np.linalg.norm(point - self.center)
        return max(0.0, dist - self.radius)

    def collides_with_line(
        self, p1: np.ndarray, p2: np.ndarray, clearance: float = 0.0
    ) -> bool:
        """Check line segment collision with circle"""
        # Vector from p1 to p2
        v = p2 - p1
        # Vector from p1 to circle center
        w = self.center - p1

        # Find closest point on line segment to circle center
        c1 = np.dot(w, v)
        if c1 <= 0:
            closest_point = p1
        else:
            c2 = np.dot(v, v)
            if c1 >= c2:
                closest_point = p2
            else:
                closest_point = p1 + (c1 / c2) * v

        # Distance from circle center to closest point
        dist = np.linalg.norm(self.center - closest_point)
        return dist < (self.radius + clearance)


class RectangleObstacle(Obstacle):
    """Rectangular obstacle (axis-aligned)"""

    def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """
        Initialize rectangular obstacle

        Args:
            x_min, x_max: X bounds
            y_min, y_max: Y bounds
        """
        self.x_min = min(x_min, x_max)
        self.x_max = max(x_min, x_max)
        self.y_min = min(y_min, y_max)
        self.y_max = max(y_min, y_max)
        self.center = np.array(
            [(self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2]
        )

    def contains_point(self, point: np.ndarray) -> bool:
        """Check if point is inside rectangle"""
        return (
            self.x_min <= point[0] <= self.x_max
            and self.y_min <= point[1] <= self.y_max
        )

    def distance_to_point(self, point: np.ndarray) -> float:
        """Distance from point to rectangle"""
        dx = max(self.x_min - point[0], 0, point[0] - self.x_max)
        dy = max(self.y_min - point[1], 0, point[1] - self.y_max)
        return np.sqrt(dx**2 + dy**2)

    def collides_with_line(
        self, p1: np.ndarray, p2: np.ndarray, clearance: float = 0.0
    ) -> bool:
        """Check line segment collision with rectangle"""
        # Expand rectangle by clearance
        x_min = self.x_min - clearance
        x_max = self.x_max + clearance
        y_min = self.y_min - clearance
        y_max = self.y_max + clearance

        # Check if line segment intersects expanded rectangle
        # Using parametric line equation: P(t) = p1 + t*(p2-p1)

        d = p2 - p1
        p = p1

        # Check against all four boundaries
        t_min, t_max = 0.0, 1.0

        for i in range(2):
            if abs(d[i]) < 1e-10:
                # Line is parallel to slab
                if p[i] < [x_min, y_min][i] or p[i] > [x_max, y_max][i]:
                    return False
            else:
                t1 = ([x_min, y_min][i] - p[i]) / d[i]
                t2 = ([x_max, y_max][i] - p[i]) / d[i]

                if t1 > t2:
                    t1, t2 = t2, t1

                t_min = max(t_min, t1)
                t_max = min(t_max, t2)

                if t_min > t_max:
                    return False

        return True


class Environment:
    """2D environment with obstacles"""

    def __init__(self, bounds: Tuple[float, float, float, float]):
        """
        Initialize environment

        Args:
            bounds: (x_min, x_max, y_min, y_max)
        """
        self.x_min, self.x_max, self.y_min, self.y_max = bounds
        self.obstacles: List[Obstacle] = []

    def add_obstacle(self, obstacle: Obstacle) -> None:
        """Add obstacle to environment"""
        self.obstacles.append(obstacle)

    def add_circle_obstacle(
        self, center: Union[List, np.ndarray], radius: float
    ) -> None:
        """Add circular obstacle"""
        self.add_obstacle(CircleObstacle(center, radius))

    def add_rectangle_obstacle(
        self, x_min: float, x_max: float, y_min: float, y_max: float
    ) -> None:
        """Add rectangular obstacle"""
        self.add_obstacle(RectangleObstacle(x_min, x_max, y_min, y_max))

    def is_collision_free(self, point: np.ndarray, clearance: float = 0.0) -> bool:
        """Check if point is collision-free"""
        # Check bounds
        if (
            point[0] < self.x_min + clearance
            or point[0] > self.x_max - clearance
            or point[1] < self.y_min + clearance
            or point[1] > self.y_max - clearance
        ):
            return False

        # Check obstacles
        for obstacle in self.obstacles:
            if obstacle.distance_to_point(point) < clearance:
                return False

        return True

    def is_path_collision_free(
        self, p1: np.ndarray, p2: np.ndarray, clearance: float = 0.0
    ) -> bool:
        """Check if path segment is collision-free"""
        # Check start and end points
        if not self.is_collision_free(p1, clearance):
            return False
        if not self.is_collision_free(p2, clearance):
            return False

        # Check collision with obstacles
        for obstacle in self.obstacles:
            if obstacle.collides_with_line(p1, p2, clearance):
                return False

        return True

    def get_distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        """Get actual distance between two points (accounting for obstacles)"""
        # For now, return Euclidean distance
        # This could be replaced with actual shortest path distance
        return np.linalg.norm(p2 - p1)
