"""
RRT* (Rapidly-exploring Random Tree Star) - tìm đường ngẫu nhiên.

Mô tả sơ lược:
- Xây dựng một cây các nút (TreeNode) mở rộng ngẫu nhiên trong không gian.
- Mỗi vòng lặp: lấy một điểm ngẫu nhiên, tìm nút gần nhất, steer theo hướng đó.
- Khi thêm nút mới, xem xét các nút lân cận để 'rewire' (kết nối lại) nhằm giảm chi phí.
- Nếu có nút đến gần goal thì lựa chọn làm path tốt nhất.

Các thành phần chính:
- `TreeNode`: chứa tọa độ, parent, cost.
- `RRTStar`: lưu tree và các tham số như `step_size`, `max_iter`.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from generate_map import Map2D


class TreeNode:
    """Nút trong cây RRT*."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.parent = None
        self.cost = 0.0  # Chi phí từ gốc
    
    def distance(self, other: 'TreeNode') -> float:
        """Tính khoảng cách Euclidean."""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def position(self) -> Tuple[float, float]:
        """Trả về tọa độ."""
        return (self.x, self.y)


class RRTStar:
    """Lớp thực hiện thuật toán RRT*."""
    
    def __init__(self, map_obj: Map2D, max_iter: int = 5000, 
                 step_size: float = 2.0, goal_sample_rate: float = 0.1):
        """
        Khởi tạo RRT*.
        
        Args:
            map_obj: Đối tượng Map2D
            max_iter: Số lần lặp tối đa
            step_size: Kích thước bước di chuyển
            goal_sample_rate: Xác suất chọn điểm đích làm mục tiêu ngẫu nhiên
        """
        self.map = map_obj
        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.search_radius = 50.0  # Bán kính tìm kiếm hàng xóm
        self.nodes = []

        # Lưu thời gian tính toán nếu cần đo (không bắt buộc)
        self.computation_time = 0
    
    def sample_random_point(self) -> Tuple[float, float]:
        """
        Lấy một điểm ngẫu nhiên trong bản đồ.
        
        Returns:
            Điểm ngẫu nhiên (x, y)
        """
        # Với xác suất goal_sample_rate chọn thẳng mục tiêu để tăng tốc tìm path
        if np.random.random() < self.goal_sample_rate:
            return self.map.goal

        # Ngẫu nhiên đều trên toàn bản đồ
        return (
            np.random.uniform(0, self.map.width),
            np.random.uniform(0, self.map.height)
        )
    
    def find_nearest_node(self, point: Tuple[float, float]) -> TreeNode:
        """
        Tìm nút gần nhất trong cây.
        
        Args:
            point: Điểm cần tìm
            
        Returns:
            Nút gần nhất
        """
        min_distance = float('inf')
        nearest_node = None
        
        for node in self.nodes:
            distance = np.sqrt((node.x - point[0])**2 + (node.y - point[1])**2)
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
        
        return nearest_node
    
    def find_nearby_nodes(self, point: Tuple[float, float], radius: float) -> List[TreeNode]:
        """
        Tìm các nút trong bán kính nhất định.
        
        Args:
            point: Điểm trung tâm
            radius: Bán kính tìm kiếm
            
        Returns:
            Danh sách các nút gần đó
        """
        nearby_nodes = []
        
        for node in self.nodes:
            distance = np.sqrt((node.x - point[0])**2 + (node.y - point[1])**2)
            if distance <= radius:
                nearby_nodes.append(node)
        
        return nearby_nodes
    
    def steer(self, from_node: TreeNode, to_point: Tuple[float, float]) -> Optional[TreeNode]:
        """
        Tạo một bước từ nút đó đến điểm đó.
        
        Args:
            from_node: Nút bắt đầu
            to_point: Điểm đích
            
        Returns:
            Nút mới hoặc None nếu không thể
        """
        direction = np.array([to_point[0] - from_node.x, to_point[1] - from_node.y])
        distance = np.linalg.norm(direction)
        
        # Nếu điểm quá gần thì trả về node tại điểm đó
        if distance < 1e-6:
            return TreeNode(to_point[0], to_point[1])

        # Chuẩn hóa hướng và di chuyển tối đa bằng `step_size`
        direction = direction / distance
        move_distance = min(self.step_size, distance)
        new_x = from_node.x + direction[0] * move_distance
        new_y = from_node.y + direction[1] * move_distance

        # Kiểm tra va chạm bằng cách sampling đoạn thẳng
        if self.is_collision_free(from_node.position(), (new_x, new_y)):
            new_node = TreeNode(new_x, new_y)
            return new_node

        return None
    
    def is_collision_free(self, p1: Tuple[float, float], 
                         p2: Tuple[float, float], samples: int = 10) -> bool:
        """
        Kiểm tra xem đường đi giữa hai điểm có va chạm không.
        
        Args:
            p1: Điểm bắt đầu
            p2: Điểm kết thúc
            samples: Số điểm kiểm tra trên đường đi
            
        Returns:
            True nếu không va chạm
        """
        # Chia đoạn thẳng thành nhiều mẫu và kiểm tra từng mẫu có va chạm không
        for i in range(samples + 1):
            t = i / samples
            x = p1[0] + (p2[0] - p1[0]) * t
            y = p1[1] + (p2[1] - p1[1]) * t

            if self.map.is_collision(x, y, radius=0.3):
                return False

        return True
    
    def rewire(self, new_node: TreeNode, nearby_nodes: List[TreeNode]):
        """
        Kết nối lại cây để giảm chi phí.
        
        Args:
            new_node: Nút mới được thêm
            nearby_nodes: Danh sách các nút gần đó
        """
        for node in nearby_nodes:
            if node == new_node:
                continue
            
            new_cost = new_node.cost + new_node.distance(node)
            
            if new_cost < node.cost and self.is_collision_free(
                new_node.position(), node.position()):
                node.parent = new_node
                node.cost = new_cost
    
    def find_path(self) -> List[Tuple[float, float]]:
        """
        Tìm đường đi từ bắt đầu đến đích.
        
        Returns:
            Danh sách các điểm trong đường đi
        """
        # Nếu không có start/goal thì không thể tìm
        if not self.map.start or not self.map.goal:
            return []

        # Khởi tạo cây với nút bắt đầu
        start_node = TreeNode(self.map.start[0], self.map.start[1])
        start_node.cost = 0
        self.nodes.append(start_node)

        goal_node = None
        best_cost = float('inf')

        for iteration in range(self.max_iter):
            # Lấy điểm ngẫu nhiên (có thể là goal với xác suất goal_sample_rate)
            random_point = self.sample_random_point()

            # Tìm nút gần nhất trong cây và tạo bước tới điểm đó
            nearest_node = self.find_nearest_node(random_point)
            new_node = self.steer(nearest_node, random_point)

            if new_node is None:
                # Không thể mở rộng tới điểm này (vd: va chạm), chuyển sang lần lặp tiếp
                continue

            # Tính chi phí và đặt parent tạm thời
            new_node.cost = nearest_node.cost + nearest_node.distance(new_node)
            new_node.parent = nearest_node

            # Tìm các nút lân cận trong bán kính để xem có thể chọn parent tốt hơn
            nearby_nodes = self.find_nearby_nodes(new_node.position(), self.search_radius)

            # Chọn parent tối ưu trong nearby_nodes nếu có đường nối không va chạm
            for node in nearby_nodes:
                if node == new_node or node == nearest_node:
                    continue

                cost = node.cost + node.distance(new_node)

                if cost < new_node.cost and self.is_collision_free(node.position(), new_node.position()):
                    new_node.parent = node
                    new_node.cost = cost

            # Thêm node mới vào cây và rewire để tối ưu chi phí các neighbor
            self.nodes.append(new_node)
            self.rewire(new_node, nearby_nodes)

            # Kiểm tra xem node mới có đến gần goal không
            distance_to_goal = new_node.distance(TreeNode(self.map.goal[0], self.map.goal[1]))

            if distance_to_goal < self.step_size and distance_to_goal < best_cost:
                if self.is_collision_free(new_node.position(), self.map.goal):
                    best_cost = distance_to_goal
                    goal_node = new_node

        # Nếu không tìm được goal_node thì không tìm thấy path
        if goal_node is None:
            return []

        # Xây dựng lại đường đi từ goal_node về start
        path = [self.map.goal]
        current = goal_node

        while current is not None:
            path.append(current.position())
            current = current.parent

        path.reverse()
        return path


def rrt_star_path_planning(map_obj: Map2D, max_iter: int = 5000, 
                          step_size: float = 2.0) -> List[Tuple[float, float]]:
    """
    Hàm tiện ích để chạy RRT*.
    
    Args:
        map_obj: Đối tượng Map2D
        max_iter: Số lần lặp tối đa
        step_size: Kích thước bước di chuyển
        
    Returns:
        Đường đi tìm được
    """
    rrt_star = RRTStar(map_obj, max_iter, step_size)
    return rrt_star.find_path()


if __name__ == "__main__":
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    path = rrt_star_path_planning(map_obj, max_iter=3000)
    
    if path:
        print(f"Tìm thấy đường đi với {len(path)} điểm")
        print(f"Độ dài: {sum(np.linalg.norm(np.array(path[i+1]) - np.array(path[i])) for i in range(len(path)-1)):.2f}")
        map_obj.visualize(path, filename='results/rrt_star_example.png')
    else:
        print("Không tìm thấy đường đi")
