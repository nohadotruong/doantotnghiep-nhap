import math
import numpy as np


def point_in_rectangle(px, py, rx, ry, rw, rh):
    return (rx <= px <= rx + rw) and (ry <= py <= ry + rh)


def line_rectangle_collision(x1, y1, x2, y2, rx, ry, rw, rh, num_samples=20):
    t_values = np.linspace(0, 1, num_samples)

    points_x = x1 + t_values * (x2 - x1)
    points_y = y1 + t_values * (y2 - y1)

    for px, py in zip(points_x, points_y):
        if point_in_rectangle(px, py, rx, ry, rw, rh):
            return True

    return False


def path_length(path):
    if len(path) < 2:
        return 0

    path_array = np.array(path)
    diffs = path_array[1:] - path_array[:-1]
    distances = np.linalg.norm(diffs, axis=1)

    return float(np.sum(distances))


def smoothness_penalty(path):
    if len(path) < 3:
        return 0

    path_array = np.array(path)
    v1 = path_array[1:-1] - path_array[:-2]
    v2 = path_array[2:] - path_array[1:-1]
    len1 = np.linalg.norm(v1, axis=1)
    len2 = np.linalg.norm(v2, axis=1)

    dot = np.sum(v1 * v2, axis=1)
    cos_angle = dot / (len1 * len2 + 1e-10)
    cos_angle = np.clip(cos_angle, -1, 1)
    angles = np.arccos(cos_angle)

    return float(np.sum(np.abs(angles)))


def calculate_min_distance_to_obstacle(point, obstacle):
    px, py = point
    ox, oy, ow, oh = obstacle

    closest_x = max(ox, min(px, ox + ow))
    closest_y = max(oy, min(py, oy + oh))

    dx = px - closest_x
    dy = py - closest_y
    distance = math.sqrt(dx**2 + dy**2)

    if ox <= px <= ox + ow and oy <= py <= oy + oh:
        return -distance

    return distance


def calculate_path_safety(path, obstacles, safety_margin=0.5):
    if not path or not obstacles:
        return 100, float("inf"), True

    min_distance = float("inf")

    for point in path:
        for obstacle in obstacles:
            distance = calculate_min_distance_to_obstacle(point, obstacle)

    if min_distance < 0:
        safety_score = 0
        is_safe = False
    elif min_distance < safety_margin:
        safety_score = max(0, (min_distance / safety_margin) * 100)
        is_safe = False
    else:
        safety_score = min(100, (min_distance / (safety_margin * 3)) * 100)
        is_safe = True

    return safety_score, min_distance, is_safe
