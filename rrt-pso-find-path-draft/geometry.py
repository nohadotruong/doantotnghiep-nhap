"""
Core Geometric Functions for RRT-PSO Path Planning

Functions (no OOP):
- Collision detection: point in rectangle, line intersections
- Path calculations: distance, length, curvature, straightness
"""

import numpy as np
import math


# ============================================================================
# COLLISION DETECTION FUNCTIONS
# ============================================================================

def point_in_rectangle(px, py, rx, ry, rw, rh):
    """
    Check if point (px, py) is inside rectangle [rx, ry, rw, rh].
    
    Args:
        px, py (float): point coordinates
        rx, ry (float): rectangle left-bottom corner
        rw, rh (float): rectangle width and height
    
    Returns:
        bool: True if point inside, False otherwise
    """
    return (rx <= px <= rx + rw) and (ry <= py <= ry + rh)


def line_segment_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Check if two line segments intersect using CCW method.
    
    Segments: (x1,y1)-(x2,y2) and (x3,y3)-(x4,y4)
    """
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    
    return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and \
           ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)


def line_rectangle_collision(x1, y1, x2, y2, rx, ry, rw, rh):
    """
    Check if line segment (x1,y1)-(x2,y2) collides with rectangle.
    """
    # Check if endpoints are inside
    if point_in_rectangle(x1, y1, rx, ry, rw, rh) or \
       point_in_rectangle(x2, y2, rx, ry, rw, rh):
        return True
    
    # Check intersection with 4 edges
    return (line_segment_intersection(x1, y1, x2, y2, rx, ry, rx + rw, ry) or
            line_segment_intersection(x1, y1, x2, y2, rx, ry + rh, rx + rw, ry + rh) or
            line_segment_intersection(x1, y1, x2, y2, rx, ry, rx, ry + rh) or
            line_segment_intersection(x1, y1, x2, y2, rx + rw, ry, rx + rw, ry + rh))


# ============================================================================
# DISTANCE FUNCTIONS
# ============================================================================

def distance(p1, p2):
    """
    Calculate Euclidean distance between two points.
    
    Args:
        p1, p2: tuples (x, y) or lists/arrays
    
    Returns:
        float: distance
    """
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# ============================================================================
# PATH METRICS
# ============================================================================

def path_length(path):
    """
    Calculate total length of a path.
    
    Args:
        path (list): list of (x, y) coordinates
    
    Returns:
        float: total path length
    """
    if len(path) < 2:
        return 0
    
    path_array = np.array(path)
    diffs = path_array[1:] - path_array[:-1]
    distances = np.linalg.norm(diffs, axis=1)
    return float(np.sum(distances))


def path_curvature(path):
    """
    Calculate total curvature (sum of turning angles at waypoints).
    
    Lower = straighter path, Higher = more bends.
    
    Args:
        path (list): list of (x, y) coordinates
    
    Returns:
        float: total curvature (sum of angles in radians)
    """
    if len(path) < 3:
        return 0
    
    path_array = np.array(path)
    
    # Incoming and outgoing vectors at each intermediate point
    v1 = path_array[1:-1] - path_array[:-2]
    v2 = path_array[2:] - path_array[1:-1]
    
    # vector magnitudes
    len1 = np.linalg.norm(v1, axis=1)
    len2 = np.linalg.norm(v2, axis=1)
    
    # Cosine of angle between vectors
    dot = np.sum(v1 * v2, axis=1)
    cos_angle = dot / (len1 * len2 + 1e-10)
    cos_angle = np.clip(cos_angle, -1, 1)
    
    # Sum of angles
    angles = np.arccos(cos_angle)
    return float(np.sum(np.abs(angles)))


def path_straightness(path):
    """
    Calculate average deviation from straight line (start→goal).
    
    Lower = closer to direct path, Higher = more deviation.
    
    Args:
        path (list): list of (x, y) coordinates
    
    Returns:
        float: average perpendicular distance from straight line
    """
    if len(path) < 3:
        return 0
    
    path_array = np.array(path)
    start = path_array[0]
    goal = path_array[-1]
    
    line_vec = goal - start
    line_len = np.linalg.norm(line_vec)
    
    if line_len == 0:
        return 0
    
    line_unit_vec = line_vec / line_len
    total_distance = 0.0
    
    # Distance from each intermediate point to the straight line
    for i in range(1, len(path_array) - 1):
        point = path_array[i]
        point_vec = point - start
        
        # Project point onto line
        proj_len = np.dot(point_vec, line_unit_vec)
        proj_point = start + proj_len * line_unit_vec
        
        # Perpendicular distance
        distance = np.linalg.norm(point - proj_point)
        total_distance += distance
    
    num_waypoints = max(1, len(path_array) - 2)
    return float(total_distance / num_waypoints)
