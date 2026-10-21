"""
╔════════════════════════════════════════════════════════════════════════════════╗
║             Core Utilities - Kiểm Tra Va Chạm & Tính Toán Đường               ║
║                      (Nền tảng cho RRT/PSO/Evaluation)                        ║
╚════════════════════════════════════════════════════════════════════════════════╝

🎯 CÔNG DỤNG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Module cơ bản cung cấp:
1️⃣ Kiểm tra va chạm (collision detection):
   - point_in_rectangle(): kiểm tra điểm vs vật cản
   - line_rectangle_collision(): kiểm tra đoạn thẳng vs vật cản
   - line_segment_intersection(): kiểm tra giao điểm 2 đoạn thẳng

2️⃣ Tính toán đường đi (path utilities):
   - path_length(): tính độ dài đường
   - smoothness_penalty(): tính mức độ gấp khúc

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 DEPENDENCIES:
- NumPy: Tính toán hiệu suất cao (10-100x nhanh hơn pure Python)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import numpy as np


def point_in_rectangle(px, py, rx, ry, rw, rh):
    """
    Kiểm tra xem một điểm có nằm bên trong hình chữ nhật (vật cản) không
    
    Args:
        px, py (float): tọa độ điểm
        rx, ry (float): tọa độ góc trái dưới của hình chữ nhật
        rw, rh (float): chiều rộng và chiều cao
    
    Returns:
        bool: True nếu điểm nằm trong vật cản
    """
    return (rx <= px <= rx + rw) and (ry <= py <= ry + rh)


def line_rectangle_collision(x1, y1, x2, y2, rx, ry, rw, rh):
    """
    Kiểm tra xem đoạn đường có va chạm với hình chữ nhật không
    
    Args:
        x1, y1 (float): tọa độ điểm bắt đầu của đoạn đường
        x2, y2 (float): tọa độ điểm kết thúc của đoạn đường
        rx, ry (float): tọa độ góc trái dưới của hình chữ nhật
        rw, rh (float): chiều rộng và chiều cao
    
    Returns:
        bool: True nếu va chạm
    """
    # Kiểm tra nếu một trong hai điểm nằm trong vật cản
    if point_in_rectangle(x1, y1, rx, ry, rw, rh) or \
       point_in_rectangle(x2, y2, rx, ry, rw, rh):
        return True
    
    # Kiểm tra giao điểm với 4 cạnh
    return (line_segment_intersection(x1, y1, x2, y2, rx, ry, rx + rw, ry) or
            line_segment_intersection(x1, y1, x2, y2, rx, ry + rh, rx + rw, ry + rh) or
            line_segment_intersection(x1, y1, x2, y2, rx, ry, rx, ry + rh) or
            line_segment_intersection(x1, y1, x2, y2, rx + rw, ry, rx + rw, ry + rh))


def line_rectangle_collision_by_points(x1, y1, x2, y2, rx, ry, rw, rh, num_samples=20):
    """
    Kiểm tra va chạm bằng cách chia điểm trên đoạn thẳng
    
    Args:
        x1, y1, x2, y2 (float): tọa độ điểm bắt đầu và kết thúc
        rx, ry, rw, rh (float): vị trí và kích thước hình chữ nhật
        num_samples (int): số điểm để chia trên đoạn (mặc định: 20)
    
    Returns:
        bool: True nếu va chạm
    """
    t_values = np.linspace(0, 1, num_samples)
    points_x = x1 + t_values * (x2 - x1)
    points_y = y1 + t_values * (y2 - y1)
    
    for px, py in zip(points_x, points_y):
        if point_in_rectangle(px, py, rx, ry, rw, rh):
            return True
    
    return False


def line_segment_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Kiểm tra xem hai đoạn thẳng có giao nhau không (phương pháp CCW)
    
    Args:
        x1, y1, x2, y2 (float): tọa độ 2 điểm của đoạn thẳng 1
        x3, y3, x4, y4 (float): tọa độ 2 điểm của đoạn thẳng 2
    
    Returns:
        bool: True nếu 2 đoạn giao nhau
    """
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    
    return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and \
           ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)


def path_length(path):
    """
    Tính độ dài tổng cộng của một đường đi
    
    Args:
        path (list): danh sách tọa độ [(x1,y1), (x2,y2), ..., (xn,yn)]
    
    Returns:
        float: tổng độ dài của đường đi
    """
    if len(path) < 2:
        return 0
    
    path_array = np.array(path)
    diffs = path_array[1:] - path_array[:-1]
    distances = np.linalg.norm(diffs, axis=1)
    
    return float(np.sum(distances))


def smoothness_penalty(path):
    """
    Tính mức độ "gấp khúc" của đường đi (penalty score)
    - Giá trị nhỏ = đường mựa, giá trị lớn = đường gấp khúc
    
    Args:
        path (list): danh sách tọa độ [(x1,y1), (x2,y2), ...]
    
    Returns:
        float: tổng penalty (góc gấp khúc)
    """
    if len(path) < 3:
        return 0
    
    path_array = np.array(path)
    
    # Vector vào và rời khỏi mỗi điểm giữa
    v1 = path_array[1:-1] - path_array[:-2]
    v2 = path_array[2:] - path_array[1:-1]
    
    # Độ dài vector
    len1 = np.linalg.norm(v1, axis=1)
    len2 = np.linalg.norm(v2, axis=1)
    
    # Tính cosine của góc giữa 2 vector
    dot = np.sum(v1 * v2, axis=1)
    cos_angle = dot / (len1 * len2 + 1e-10)
    cos_angle = np.clip(cos_angle, -1, 1)
    
    # Tính góc và cộng tổng
    angles = np.arccos(cos_angle)
    
    return float(np.sum(np.abs(angles)))

def calculate_path_safety(path, obstacles, safety_margin=0.5):
    """
    Tính độ an toàn của một path dựa trên khoảng cách đến chướng ngại vật.
    
    Args:
        path: Danh sách các điểm trên path [(x1, y1), (x2, y2), ...]
        obstacles: Danh sách các chướng ngại vật (vòng tròn hoặc hộp)
                   Ví dụ: [{'center': (x, y), 'radius': r}, ...]
        safety_margin: Khoảng cách an toàn tối thiểu (mặc định: 0.5)
    
    Returns:
        safety_score: Điểm an toàn (0-100), cao hơn là an toàn hơn
        min_distance: Khoảng cách lближ nhất đến chướng ngại vật
        is_safe: True nếu path an toàn, False nếu va chạm
    """
    if not path or not obstacles:
        return 100, float('inf'), True
    
    min_distance = float('inf')
    
    # Kiểm tra khoảng cách từ mỗi điểm trên path đến chướng ngại vật
    for point in path:
        for obstacle in obstacles:
            distance = calculate_min_distance_to_obstacle(point, obstacle)
            min_distance = min(min_distance, distance)
    
    # Tính điểm an toàn
    if min_distance < 0:  # Va chạm
        safety_score = 0
        is_safe = False
    elif min_distance < safety_margin:
        # Nguy hiểm nhưng chưa va chạm
        safety_score = max(0, (min_distance / safety_margin) * 100)
        is_safe = False
    else:
        # An toàn
        safety_score = min(100, (min_distance / (safety_margin * 3)) * 100)
        is_safe = True
    
    return safety_score, min_distance, is_safe


def calculate_min_distance_to_obstacle(point, obstacle):
    """
    Tính khoảng cách từ một điểm đến chướng ngại vật.
    
    Args:
        point: (x, y)
        obstacle: {'center': (cx, cy), 'radius': r}
    
    Returns:
        Khoảng cách từ điểm đến biên chướng ngại vật
    """
    import math
    
    px, py = point
    ox, oy, ow, oh = obstacle
    
    # Tìm điểm gần nhất trên hình chữ nhật
    closest_x = max(ox, min(px, ox + ow))
    closest_y = max(oy, min(py, oy + oh))
    
    # Tính khoảng cách
    dx = px - closest_x
    dy = py - closest_y
    distance = math.sqrt(dx**2 + dy**2)
    
    # Nếu điểm nằm trong hình chữ nhật, trả về khoảng cách âm
    if ox <= px <= ox + ow and oy <= py <= oy + oh:
        return -distance
    
    return distance
