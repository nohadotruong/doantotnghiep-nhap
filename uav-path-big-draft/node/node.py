# Nhập thư viện toán học để sử dụng hàm sqrt
import math


# Định nghĩa lớp Node - đại diện cho một điểm (nút) trong không gian
class Node:
    # Phương thức khởi tạo - tạo một nút mới
    def __init__(self, x, y, parent=None):
        self.x = x  # Tọa độ X của nút
        self.y = y  # Tọa độ Y của nút
        self.parent = parent  # Tham chiếu đến nút cha (dùng để xây dựng cây đường đi)

    # Phương thức tính khoảng cách Euclid từ nút hiện tại đến một nút khác
    def distance_to(self, other):
        dx = self.x - other.x  # Tính hiệu tọa độ X
        dy = self.y - other.y  # Tính hiệu tọa độ Y

        # Tính tổng bình phương (dx² + dy²) - công thức khoảng cách Euclid
        sum_squared = dx * dx + dy * dy  # Bình phương mỗi thành phần rồi cộng lại (FIXED)
        # Đảm bảo sum_squared không âm (phòng trường hợp các lỗi tính toán)
        sum_squared = max(0, sum_squared)

        # Tính căn bậc hai để được khoảng cách Euclid cuối cùng
        return math.sqrt(sum_squared)

    # Phương thức đặc biệt để trả về biểu diễn chuỗi của nút
    def __repr__(self):
        # Trả về chuỗi biểu diễn nút dưới dạng "Node(x, y)" - dùng khi print() hoặc repr() (FIXED)
        return f"Node({self.x}, {self.y})"
