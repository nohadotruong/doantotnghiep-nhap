# Nhập các thư viện cần thiết
import math  # Thư viện toán học (cần dùng hàm sqrt)
import numpy as np  # Thư viện xử lý mảng và toán học


# ============================================================================
# Hàm kiểm tra xem một điểm có nằm bên trong hình chữ nhật không
# ============================================================================
def point_in_rectangle(px, py, rx, ry, rw, rh):
    """
    Kiểm tra xem điểm (px, py) có nằm bên trong hình chữ nhật không
    
    Tham số:
        px, py: Tọa độ của điểm
        rx, ry: Tọa độ góc trái dưới của hình chữ nhật
        rw, rh: Chiều rộng và chiều cao của hình chữ nhật
    
    Trả về: True nếu điểm nằm trong hình chữ nhật, False nếu không
    """
    # Kiểm tra xem px nằm trong khoảng [rx, rx+rw] và py nằm trong khoảng [ry, ry+rh]
    return (rx <= px <= rx + rw) and (ry <= py <= ry + rh)


# ============================================================================
# Hàm kiểm tra va chạm giữa đường thẳng và hình chữ nhật
# ============================================================================
def line_rectangle_collision(x1, y1, x2, y2, rx, ry, rw, rh, num_samples=20):
    """
    Kiểm tra xem đoạn thẳng từ (x1,y1) đến (x2,y2) có giao với hình chữ nhật không
    
    Tham số:
        x1, y1: Tọa độ điểm bắt đầu
        x2, y2: Tọa độ điểm kết thúc
        rx, ry: Tọa độ góc trái dưới của hình chữ nhật
        rw, rh: Chiều rộng và chiều cao của hình chữ nhật
        num_samples: Số lượng điểm để kiểm tra trên đoạn thẳng
    
    Trả về: True nếu có va chạm, False nếu không
    """
    # Tạo các giá trị t từ 0 đến 1, chia đoạn thẳng thành num_samples điểm
    t_values = np.linspace(0, 1, num_samples)

    # Tính tọa độ x của các điểm trên đoạn thẳng: x = x1 + t*(x2-x1)
    points_x = x1 + t_values * (x2 - x1)
    # Tính tọa độ y của các điểm trên đoạn thẳng: y = y1 + t*(y2-y1)
    points_y = y1 + t_values * (y2 - y1)

    # Lặp qua các cặp tọa độ (px, py) trên đoạn thẳng
    for px, py in zip(points_x, points_y):
        # Kiểm tra nếu điểm này nằm trong hình chữ nhật
        if point_in_rectangle(px, py, rx, ry, rw, rh):
            return True  # Có va chạm

    return False  # Không có va chạm


# ============================================================================
# Hàm tính độ dài của đường đi
# ============================================================================
def path_length(path):
    """
    Tính tổng độ dài của đường đi (tổng khoảng cách giữa các điểm liên tiếp)
    
    Tham số:
        path: Danh sách các điểm (tọa độ) tạo thành đường đi
    
    Trả về: Độ dài tổng cộng của đường đi
    """
    # Nếu đường đi có ít hơn 2 điểm, không thể tính độ dài
    if len(path) < 2:
        return 0

    # Chuyển danh sách điểm thành mảng numpy để dễ tính toán
    path_array = np.array(path)
    # Tính vector hiệu giữa các điểm liên tiếp: path[1:] - path[:-1]
    diffs = path_array[1:] - path_array[:-1]
    # Tính norm (độ dài) của mỗi vector (khoảng cách giữa 2 điểm)
    distances = np.linalg.norm(diffs, axis=1)

    # Trả về tổng tất cả các khoảng cách (chuyển thành float để dễ sử dụng)
    return float(np.sum(distances))


# ============================================================================
# Hàm tính độ trơn của đường đi (dựa trên góc giữa các vector liên tiếp)
# ============================================================================
def smoothness_penalty(path):
    """
    Tính độ phạt mượt mà (smoothness penalty) - càng lớn tức đường đi càng gấp khúc
    
    Tham số:
        path: Danh sách các điểm tạo thành đường đi
    
    Trả về: Tổng độ lớn các góc thay đổi hướng (tính bằng radian)
    """
    # Nếu đường đi có ít hơn 3 điểm, không thể tính độ trơn
    if len(path) < 3:
        return 0

    # Chuyển danh sách điểm thành mảng numpy
    path_array = np.array(path)
    # Tính vector v1 từ điểm i đến điểm i+1
    v1 = path_array[1:-1] - path_array[:-2]
    # Tính vector v2 từ điểm i+1 đến điểm i+2
    v2 = path_array[2:] - path_array[1:-1]
    
    # Tính độ dài (norm) của mỗi vector v1
    len1 = np.linalg.norm(v1, axis=1)
    # Tính độ dài (norm) của mỗi vector v2
    len2 = np.linalg.norm(v2, axis=1)

    # Tính tích vô hướng (dot product) giữa v1 và v2
    dot = np.sum(v1 * v2, axis=1)
    # Tính cosin của góc: cos(angle) = (v1·v2) / (|v1| * |v2|)
    cos_angle = dot / (len1 * len2 + 1e-10)  # Cộng 1e-10 để tránh chia cho 0
    # Giới hạn cos_angle trong khoảng [-1, 1] để tránh lỗi khi tính arccos
    cos_angle = np.clip(cos_angle, -1, 1)
    # Tính góc từ cosin: angle = arccos(cos_angle)
    angles = np.arccos(cos_angle)

    # Trả về tổng giá trị tuyệt đối của tất cả các góc
    return float(np.sum(np.abs(angles)))


# ============================================================================
# Hàm tính khoảng cách tối thiểu từ một điểm đến một chướng ngại vật
# ============================================================================
def calculate_min_distance_to_obstacle(point, obstacle):
    """
    Tính khoảng cách tối thiểu từ một điểm đến gần nhất của chướng ngại vật hình chữ nhật
    
    Tham số:
        point: Tuple (px, py) - tọa độ của điểm
        obstacle: Tuple (ox, oy, ow, oh) - tọa độ và kích thước chướng ngại vật
    
    Trả về: Khoảng cách dương nếu điểm ở ngoài, âm khoảng cách nếu điểm ở trong chướng ngại vật
    """
    px, py = point  # Tách tọa độ điểm
    ox, oy, ow, oh = obstacle  # Tách thông tin chướng ngại vật

    # Tìm điểm gần nhất trên chướng ngại vật so với điểm đã cho
    # closest_x = tọa độ x của điểm gần nhất trên hình chữ nhật
    closest_x = max(ox, min(px, ox + ow))
    # closest_y = tọa độ y của điểm gần nhất trên hình chữ nhật
    closest_y = max(oy, min(py, oy + oh))

    # Tính vector từ điểm gần nhất đến điểm đã cho
    dx = px - closest_x
    dy = py - closest_y
    # Tính khoảng cách Euclid
    distance = math.sqrt(dx**2 + dy**2)

    # Kiểm tra nếu điểm nằm bên trong chướng ngại vật
    if ox <= px <= ox + ow and oy <= py <= oy + oh:
        # Trả về âm của khoảng cách để chỉ rằng điểm ở trong
        return -distance

    # Trả về khoảng cách dương nếu ở ngoài
    return distance


# ============================================================================
# Hàm tính độ an toàn của đường đi
# ============================================================================
def calculate_path_safety(path, obstacles, safety_margin=0.5):
    """
    Tính độ an toàn của đường đi dựa trên khoảng cách đến các chướng ngại vật
    
    Tham số:
        path: Danh sách các điểm tạo thành đường đi
        obstacles: Danh sách các chướng ngại vật
        safety_margin: Khoảng cách an toàn tối thiểu (mặc định = 0.5)
    
    Trả về: Tuple (safety_score, min_distance, is_safe)
        - safety_score: Điểm an toàn (0-100), càng cao càng an toàn
        - min_distance: Khoảng cách tối thiểu đến chướng ngại vật
        - is_safe: Boolean - True nếu an toàn, False nếu không
    """
    # Kiểm tra nếu không có đường đi hoặc chướng ngại vật
    if not path or not obstacles:
        return 100, float("inf"), True

    # Khởi tạo khoảng cách tối thiểu là vô cực
    min_distance = float("inf")

    # Lặp qua mỗi điểm trên đường đi
    for point in path:
        # Lặp qua mỗi chướng ngại vật
        for obstacle in obstacles:
            # Tính khoảng cách từ điểm hiện tại đến chướng ngại vật
            distance = calculate_min_distance_to_obstacle(point, obstacle)
            # Cập nhật khoảng cách tối thiểu nếu tìm thấy cái gần hơn
            min_distance = min(min_distance, distance)

    # Kiểm tra nếu điểm nằm bên trong chướng ngại vật (khoảng cách âm)
    if min_distance < 0:
        safety_score = 0  # Điểm an toàn = 0 (không an toàn)
        is_safe = False  # Đánh dấu không an toàn
    # Kiểm tra nếu khoảng cách nhỏ hơn an toàn margin nhưng không âm
    elif min_distance < safety_margin:
        # Tính điểm an toàn theo tỷ lệ: (khoảng cách / safety_margin) * 100
        safety_score = max(0, (min_distance / safety_margin) * 100)
        is_safe = False  # Vẫn không an toàn
    # Nếu khoảng cách lớn hơn safety margin
    else:
        # Tính điểm an toàn, giới hạn tối đa = 100
        safety_score = min(100, (min_distance / (safety_margin * 3)) * 100)
        is_safe = True  # An toàn

    return safety_score, min_distance, is_safe
