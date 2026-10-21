# Dự Án Path Planning cho UAV (Máy Bay Không Người Lái)

## Mô Tả
Dự án này cung cấp các công cụ để lập kế hoạch đường đi (path planning) cho máy bay không người lái trong môi trường có chứa chướng ngại vật.

## Cấu Trúc Dự Án
```
big-draft/
├── environment/
│   └── environment.py      # Lớp UAVEnvironment - Quản lý môi trường bay
├── node/
│   ├── __init__.py
│   └── node.py             # Lớp Node - Đại diện cho điểm trong không gian
├── requirements.txt        # Danh sách thư viện phụ thuộc
└── utils.py               # Các hàm tiện ích (cần tạo thêm)
```

## Các Thành Phần Chính

### 1. **environment.py** - Lớp UAVEnvironment
Quản lý môi trường bay của UAV:
- **`__init__(width, height, obstacles)`**: Khởi tạo môi trường với kích thước và chướng ngại vật
- **`is_inside_obstacle(x, y)`**: Kiểm tra xem điểm (x, y) có nằm trong chướng ngại vật không
- **`is_collision(p1, p2)`**: Kiểm tra xem đường thẳng từ p1 đến p2 có va chạm với chướng ngại vật không
- **`generate_random_obstacles(...)`**: Tạo chướng ngại vật ngẫu nhiên
- **`visualize(path, title, show_goal)`**: Hiển thị bản đồ, đường đi và các chướng ngại vật

### 2. **node.py** - Lớp Node
Đại diện cho một điểm trong không gian 2D:
- **`__init__(x, y, parent)`**: Khởi tạo nút tại tọa độ (x, y) với nút cha
- **`distance_to(other)`**: Tính khoảng cách Euclid đến nút khác
- **`__repr__()`**: Trả về biểu diễn chuỗi của nút

## Cần Cài Đặt
```bash
pip install -r requirements.txt
```

### Thư Viện Bắt Buộc:
- **numpy**: Xử lý mảng và toán học
- **matplotlib**: Vẽ biểu đồ và hiển thị bản đồ

## Cách Sử Dụng Cơ Bản
```python
from environment import UAVEnvironment
from node import Node

# Tạo môi trường 100x100 với 5 chướng ngại vật ngẫu nhiên
env = UAVEnvironment(100, 100, UAVEnvironment.generate_random_obstacles(100, 100, 5))

# Tạo hai nút
node1 = Node(10, 10)
node2 = Node(90, 90)

# Kiểm tra khoảng cách
print(node1.distance_to(node2))

# Kiểm tra va chạm
print(env.is_collision((node1.x, node1.y), (node2.x, node2.y)))

# Hiển thị môi trường
env.visualize(show_goal=(90, 90))
```

## Các Lỗi Đã Sửa
1. ✓ **node.py - Công thức tính khoảng cách**: Sửa từ `dx*dy + dy*dy` thành `dx*dx + dy*dy`
2. ✓ **node.py - Tên phương thức**: Sửa từ `__reqr__` thành `__repr__`

## Ghi Chú
- Chương trình giả định rằng file `utils.py` chứa các hàm: `point_in_rectangle`, `line_rectangle_collision`, `path_length`
- Cần tạo thêm file `utils.py` để chương trình chạy hoàn toàn
