"""
TSP Fitness Functions

Định nghĩa các hàm mục tiêu và penalty cho bài toán TSP đa điểm
"""

import numpy as np
from utils.core import path_length, smoothness_penalty


def fitness_tsp_basic(permutation, cost_matrix, alpha=0.5, beta=0.3):
    """
    Hàm fitness cơ bản cho TSP
    
    Fitness = α·L + β·K
    
    Trong đó:
    - L: tổng độ dài đường đi thực tế
    - K: tổng độ gấp khúc (smoothness)
    
    Args:
        permutation: list, thứ tự thăm [wp1_idx, wp2_idx, ..., wpN_idx]
        cost_matrix: CostMatrix instance
        alpha, beta: hệ số trọng lượng
    
    Returns:
        float: fitness value (minimize)
    """
    
    # Tính tổng chi phí
    total_distance = 0.0
    total_smoothness = 0.0
    invalid_paths = 0
    penalty_invalid = 1000.0  # Penalty cho mỗi đường không tìm được
    
    current = 0  # start index
    for next_idx in permutation:
        if cost_matrix.is_path_valid(current, next_idx):
            total_distance += cost_matrix.get_distance(current, next_idx)
            total_smoothness += cost_matrix.get_smoothness(current, next_idx)
        else:
            # Đường không tìm được → thêm penalty lớn
            invalid_paths += 1
        current = next_idx
    
    # Nếu quá nhiều đường không tìm được, trả về fitness rất cao
    if invalid_paths > len(permutation) / 2:
        return float('inf')
    
    # Normalize để cân bằng giữa distance và smoothness
    max_distance = 500.0
    max_smoothness = 50.0
    
    L_norm = total_distance / max_distance
    K_norm = total_smoothness / max_smoothness
    
    # Thêm penalty cho đường không hợp lệ
    penalty = invalid_paths * penalty_invalid
    
    fitness = alpha * L_norm + beta * K_norm + penalty
    
    return fitness


def fitness_tsp_with_obstacle_penalty(permutation, cost_matrix, environment, full_paths=None,
                                     alpha=0.5, beta=0.25, gamma=0.25,
                                     min_safe_distance=5.0):
    """
    Hàm fitness với penalty chướng ngại vật
    
    Fitness = α·L + β·K + γ·P
    
    Trong đó:
    - L: tổng độ dài đường đi thực tế
    - K: tổng độ gấp khúc
    - P: penalty gần chướng ngại vật
    
    Args:
        permutation: list, thứ tự thăm
        cost_matrix: CostMatrix instance
        environment: UAVEnvironment instance
        full_paths: dict cache {(i,j): path} để tránh tính lại
        alpha, beta, gamma: hệ số trọng lượng
        min_safe_distance: khoảng cách an toàn với chướng ngại
    
    Returns:
        float: fitness value
    """
    
    # Tính distance và smoothness
    total_distance = 0.0
    total_smoothness = 0.0
    invalid_paths = 0
    penalty_invalid = 1000.0
    
    current = 0
    for next_idx in permutation:
        if cost_matrix.is_path_valid(current, next_idx):
            total_distance += cost_matrix.get_distance(current, next_idx)
            total_smoothness += cost_matrix.get_smoothness(current, next_idx)
        else:
            invalid_paths += 1
        current = next_idx
    
    # Nếu quá nhiều đường không hợp lệ
    if invalid_paths > len(permutation) / 2:
        return float('inf')
    
    # Tính penalty chướng ngại vật
    obstacle_penalty = 0.0
    
    current = 0
    for next_idx in permutation:
        if full_paths and (current, next_idx) in full_paths:
            path = full_paths[(current, next_idx)]
        else:
            path = cost_matrix.get_path(current, next_idx)
        
        obstacle_penalty += calculate_obstacle_penalty(
            path, environment, min_safe_distance
        )
        
        current = next_idx
    
    # Normalize
    max_distance = 500.0
    max_smoothness = 50.0
    max_penalty = 100.0
    
    L_norm = total_distance / max_distance
    K_norm = total_smoothness / max_smoothness
    P_norm = obstacle_penalty / max_penalty
    
    penalty = invalid_paths * penalty_invalid
    
    fitness = alpha * L_norm + beta * K_norm + gamma * P_norm + penalty
    
    return fitness


def calculate_obstacle_penalty(path, environment, min_safe_distance=5.0):
    """
    Tính penalty nếu đường đi quá gần chướng ngại vật
    
    Penalty = tổng 1/distance cho các điểm gần chướng ngại
    (cộng dồn các điểm vi phạm khoảng cách an toàn)
    
    Args:
        path: list of (x, y) points
        environment: UAVEnvironment instance
        min_safe_distance: khoảng cách an toàn tối thiểu
    
    Returns:
        float: penalty score (càng lớn càng tệ)
    """
    
    if not path or len(path) == 0:
        return 0.0
    
    penalty = 0.0
    
    for point in path:
        min_dist = calculate_min_distance_to_obstacles(point, environment)
        
        if min_dist < min_safe_distance:
            # Điểm gần chướng ngại → cộng penalty
            # Dùng 1/distance để penalty lớn hơn khi gần hơn
            penalty += 1.0 / (min_dist + 0.1)
    
    return penalty


def calculate_min_distance_to_obstacles(point, environment):
    """
    Tính khoảng cách tối thiểu từ điểm đến bất kỳ chướng ngại vật nào
    
    Args:
        point: (x, y) tuple
        environment: UAVEnvironment instance
    
    Returns:
        float: khoảng cách tối thiểu, hoặc infinity nếu bên ngoài môi trường
    """
    
    px, py = point
    
    # Kiểm tra ngoài ranh giới
    if px < 0 or px > environment.width or py < 0 or py > environment.height:
        return 0.0  # Ngoài ranh giới → penalty tối đa
    
    min_distance = float('inf')
    
    for ox, oy, ow, oh in environment.obstacles:
        # Tính khoảng cách từ điểm đến hình chữ nhật
        closest_x = max(ox, min(px, ox + ow))
        closest_y = max(oy, min(py, oy + oh))
        
        dx = px - closest_x
        dy = py - closest_y
        distance = np.sqrt(dx**2 + dy**2)
        
        min_distance = min(min_distance, distance)
    
    return min_distance if min_distance != float('inf') else environment.width


def calculate_expected_max_values(cost_matrix):
    """
    Tính các giá trị max dự kiến để dùng cho normalize
    
    Hữu ích khi muốn calibrate hệ số alpha, beta, gamma
    
    Returns:
        dict: {'max_distance': ..., 'max_smoothness': ...}
    """
    distances = []
    smoothnesses = []
    
    for data in cost_matrix.cost_data.values():
        if data['success']:
            if data['distance'] != float('inf'):
                distances.append(data['distance'])
            smoothnesses.append(data['smoothness'])
    
    return {
        'max_distance': max(distances) if distances else 1.0,
        'mean_distance': np.mean(distances) if distances else 1.0,
        'max_smoothness': max(smoothnesses) if smoothnesses else 1.0,
        'mean_smoothness': np.mean(smoothnesses) if smoothnesses else 1.0,
    }


def benchmark_fitness_functions(cost_matrix, environment, num_samples=100):
    """
    So sánh hiệu suất các hàm fitness khác nhau trên ngẫu nhiên permutation
    
    Dùng để hiểu rõ hành vi của fitness function
    
    Args:
        cost_matrix: CostMatrix instance
        environment: UAVEnvironment instance
        num_samples: số sample random permutation
    
    Returns:
        dict: thống kê so sánh
    """
    
    n_waypoints = cost_matrix.n - 1  # -1 vì first là start
    
    fitness_basic_values = []
    fitness_obstacle_values = []
    
    for _ in range(num_samples):
        # Random permutation
        perm = list(np.random.permutation(range(1, cost_matrix.n)))
        
        f_basic = fitness_tsp_basic(perm, cost_matrix)
        f_obstacle = fitness_tsp_with_obstacle_penalty(
            perm, cost_matrix, environment
        )
        
        if f_basic != float('inf'):
            fitness_basic_values.append(f_basic)
        if f_obstacle != float('inf'):
            fitness_obstacle_values.append(f_obstacle)
    
    print("\n[Fitness Benchmark]")
    if fitness_basic_values:
        print(f"  Basic fitness: min={min(fitness_basic_values):.4f}, "
              f"max={max(fitness_basic_values):.4f}, "
              f"mean={np.mean(fitness_basic_values):.4f}")
    
    if fitness_obstacle_values:
        print(f"  With obstacle: min={min(fitness_obstacle_values):.4f}, "
              f"max={max(fitness_obstacle_values):.4f}, "
              f"mean={np.mean(fitness_obstacle_values):.4f}")
    
    return {
        'basic': {
            'values': fitness_basic_values,
            'min': min(fitness_basic_values) if fitness_basic_values else None,
            'max': max(fitness_basic_values) if fitness_basic_values else None,
            'mean': np.mean(fitness_basic_values) if fitness_basic_values else None,
        },
        'obstacle': {
            'values': fitness_obstacle_values,
            'min': min(fitness_obstacle_values) if fitness_obstacle_values else None,
            'max': max(fitness_obstacle_values) if fitness_obstacle_values else None,
            'mean': np.mean(fitness_obstacle_values) if fitness_obstacle_values else None,
        }
    }
