"""
rrt_star.py - Thuật toán RRT* (Rapidly-exploring Random Tree Star) cho UAV
"""
import numpy as np
from typing import List, Tuple, Optional
from generate_map import Map2D
import time


class RRTNode:
    """Node cho cây RRT*"""
    def __init__(self, position: Tuple[float, float]):
        self.position = position
        self.parent = None
        self.cost = 0  # Chi phí từ start đến node này


class RRTStar:
    """Thuật toán RRT* để tìm đường đi cho UAV"""
    
    def __init__(self, map_obj: Map2D, 
                 max_iterations: int = 3000,
                 step_size: float = 2.0,
                 goal_sample_rate: float = 0.1,
                 search_radius: float = 5.0):
        """
        Args:
            map_obj: Bản đồ
            max_iterations: Số lần lặp tối đa
            step_size: Kích thước bước mở rộng
            goal_sample_rate: Tỷ lệ lấy mẫu hướng về goal
            search_radius: Bán kính tìm kiếm láng giềng
        """
        self.map = map_obj
        self.max_iterations = max_iterations
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.search_radius = search_radius
        
        self.nodes = []
        self.path = []
        self.computation_time = 0
    
    def distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Tính khoảng cách Euclidean"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def sample_random_point(self) -> Tuple[float, float]:
        """Lấy mẫu điểm ngẫu nhiên trong không gian"""
        # Đôi khi lấy mẫu hướng về goal
        if np.random.random() < self.goal_sample_rate:
            return self.map.goal
        
        # Lấy mẫu ngẫu nhiên
        x = np.random.uniform(0, self.map.width)
        y = np.random.uniform(0, self.map.height)
        return (x, y)
    
    def get_nearest_node(self, point: Tuple[float, float]) -> RRTNode:
        """Tìm node gần nhất với điểm cho trước"""
        min_dist = float('inf')
        nearest = None
        
        for node in self.nodes:
            dist = self.distance(node.position, point)
            if dist < min_dist:
                min_dist = dist
                nearest = node
        
        return nearest
    
    def steer(self, from_pos: Tuple[float, float], 
              to_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Di chuyển từ from_pos hướng về to_pos với bước step_size
        """
        dist = self.distance(from_pos, to_pos)
        
        if dist <= self.step_size:
            return to_pos
        
        # Tính điểm mới
        theta = np.arctan2(to_pos[1] - from_pos[1], to_pos[0] - from_pos[0])
        new_x = from_pos[0] + self.step_size * np.cos(theta)
        new_y = from_pos[1] + self.step_size * np.sin(theta)
        
        return (new_x, new_y)
    
    def get_nearby_nodes(self, position: Tuple[float, float]) -> List[RRTNode]:
        """Tìm các node trong bán kính search_radius"""
        nearby = []
        for node in self.nodes:
            if self.distance(node.position, position) <= self.search_radius:
                nearby.append(node)
        return nearby
    
    def choose_parent(self, new_pos: Tuple[float, float], 
                     nearby_nodes: List[RRTNode]) -> Tuple[RRTNode, float]:
        """
        Chọn parent tốt nhất cho node mới (RRT* optimization)
        Trả về (best_parent, min_cost)
        """
        min_cost = float('inf')
        best_parent = None
        
        for node in nearby_nodes:
            # Kiểm tra đường đi có hợp lệ không
            if self.map.is_valid_path(node.position, new_pos):
                cost = node.cost + self.distance(node.position, new_pos)
                if cost < min_cost:
                    min_cost = cost
                    best_parent = node
        
        return best_parent, min_cost
    
    def rewire(self, new_node: RRTNode, nearby_nodes: List[RRTNode]):
        """
        Rewiring: Cập nhật parent của các node gần nếu đi qua new_node ngắn hơn
        """
        for node in nearby_nodes:
            if node == new_node.parent:
                continue
            
            # Tính chi phí mới nếu đi qua new_node
            new_cost = new_node.cost + self.distance(new_node.position, node.position)
            
            # Nếu tốt hơn và đường đi hợp lệ
            if new_cost < node.cost and self.map.is_valid_path(new_node.position, node.position):
                node.parent = new_node
                node.cost = new_cost
    
    def find_path(self) -> Optional[List[Tuple[float, float]]]:
        """
        Tìm đường đi từ start đến goal
        
        Returns:
            Danh sách các điểm trên đường đi, hoặc None nếu không tìm thấy
        """
        start_time = time.time()
        
        if not self.map.start or not self.map.goal:
            print("Lỗi: Chưa đặt điểm start hoặc goal!")
            return None
        
        # Khởi tạo cây với node start
        start_node = RRTNode(self.map.start)
        start_node.cost = 0
        self.nodes = [start_node]
        
        best_goal_node = None
        best_cost = float('inf')
        
        for i in range(self.max_iterations):
            # 1. Lấy mẫu điểm ngẫu nhiên
            random_point = self.sample_random_point()
            
            # 2. Tìm node gần nhất
            nearest_node = self.get_nearest_node(random_point)
            
            # 3. Steer về phía random_point
            new_pos = self.steer(nearest_node.position, random_point)
            
            # 4. Kiểm tra điểm mới có hợp lệ không
            if not self.map.is_valid_point(new_pos[0], new_pos[1]):
                continue
            
            # 5. Tìm các node gần
            nearby_nodes = self.get_nearby_nodes(new_pos)
            
            # 6. Chọn parent tốt nhất (RRT* optimization)
            best_parent, min_cost = self.choose_parent(new_pos, nearby_nodes)
            
            if best_parent is None:
                # Không thể kết nối, thử kết nối với nearest_node
                if self.map.is_valid_path(nearest_node.position, new_pos):
                    best_parent = nearest_node
                    min_cost = nearest_node.cost + self.distance(nearest_node.position, new_pos)
                else:
                    continue
            
            # 7. Thêm node mới vào cây
            new_node = RRTNode(new_pos)
            new_node.parent = best_parent
            new_node.cost = min_cost
            self.nodes.append(new_node)
            
            # 8. Rewiring (RRT* optimization)
            self.rewire(new_node, nearby_nodes)
            
            # 9. Kiểm tra có đến goal chưa
            if self.distance(new_pos, self.map.goal) <= self.step_size:
                # Thử kết nối trực tiếp đến goal
                if self.map.is_valid_path(new_pos, self.map.goal):
                    goal_node = RRTNode(self.map.goal)
                    goal_node.parent = new_node
                    goal_node.cost = new_node.cost + self.distance(new_pos, self.map.goal)
                    
                    # Cập nhật best goal nếu tốt hơn
                    if goal_node.cost < best_cost:
                        best_cost = goal_node.cost
                        best_goal_node = goal_node
        
        self.computation_time = time.time() - start_time
        
        # Tái tạo đường đi
        if best_goal_node is not None:
            path = []
            current = best_goal_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            
            self.path = path[::-1]
            return self.path
        
        print("RRT*: Không tìm thấy đường đi!")
        return None
    
    def get_path_length(self) -> float:
        """Tính độ dài đường đi"""
        if not self.path or len(self.path) < 2:
            return 0
        
        length = 0
        for i in range(len(self.path) - 1):
            length += self.distance(self.path[i], self.path[i + 1])
        
        return length


if __name__ == "__main__":
    # Test thuật toán RRT*
    from generate_map import Map2D
    import matplotlib.pyplot as plt
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Chạy RRT*
    print("Chạy thuật toán RRT*...")
    rrt_star = RRTStar(map_obj, max_iterations=2000, step_size=2.0, search_radius=8.0)
    path = rrt_star.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {rrt_star.get_path_length():.2f} m")
        print(f"  - Thời gian: {rrt_star.computation_time:.4f} s")
        print(f"  - Nodes trong cây: {len(rrt_star.nodes)}")
        
        # Vẽ kết quả
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Vẽ cây
        for node in rrt_star.nodes:
            if node.parent:
                plt.plot([node.position[0], node.parent.position[0]],
                        [node.position[1], node.parent.position[1]],
                        'c-', alpha=0.3, linewidth=0.5)
        
        # Vẽ bản đồ
        map_obj.visualize()
        
        # Vẽ đường đi
        if path:
            path_array = np.array(path)
            plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, label='RRT* Path')
            plt.legend()
        
        plt.title(f'RRT* - Độ dài: {rrt_star.get_path_length():.2f}m, Thời gian: {rrt_star.computation_time:.4f}s')
        plt.show()
