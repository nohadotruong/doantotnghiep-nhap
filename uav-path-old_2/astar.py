"""
astar.py - Thuật toán A* (A-star) cho UAV
"""
import numpy as np
from typing import List, Tuple, Optional
import heapq
from generate_map import Map2D
import time


class Node:
    """Node cho thuật toán A*"""
    def __init__(self, position: Tuple[float, float], parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Chi phí từ start đến node hiện tại
        self.h = 0  # Heuristic (ước lượng từ node hiện tại đến goal)
        self.f = 0  # Tổng chi phí f = g + h
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)


class AStar:
    """Thuật toán A* để tìm đường đi cho UAV"""
    
    def __init__(self, map_obj: Map2D, grid_resolution: float = 1.0):
        """
        Args:
            map_obj: Bản đồ
            grid_resolution: Độ phân giải lưới (mét)
        """
        self.map = map_obj
        self.grid_resolution = grid_resolution
        self.path = []
        self.computation_time = 0
        self.nodes_explored = 0
    
    def heuristic(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Tính khoảng cách Euclidean"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_neighbors(self, position: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Lấy các điểm láng giềng hợp lệ
        Sử dụng 8 hướng di chuyển
        """
        x, y = position
        neighbors = []
        
        # 8 hướng: lên, xuống, trái, phải, và 4 đường chéo
        directions = [
            (0, self.grid_resolution),    # Lên
            (0, -self.grid_resolution),   # Xuống
            (self.grid_resolution, 0),    # Phải
            (-self.grid_resolution, 0),   # Trái
            (self.grid_resolution, self.grid_resolution),    # Phải-lên
            (self.grid_resolution, -self.grid_resolution),   # Phải-xuống
            (-self.grid_resolution, self.grid_resolution),   # Trái-lên
            (-self.grid_resolution, -self.grid_resolution),  # Trái-xuống
        ]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # Kiểm tra điểm có hợp lệ không
            if self.map.is_valid_point(new_x, new_y):
                # Kiểm tra đường đi có hợp lệ không
                if self.map.is_valid_path((x, y), (new_x, new_y)):
                    neighbors.append((new_x, new_y))
        
        return neighbors
    
    def reconstruct_path(self, current_node: Node) -> List[Tuple[float, float]]:
        """Tái tạo đường đi từ goal về start"""
        path = []
        current = current_node
        
        while current is not None:
            path.append(current.position)
            current = current.parent
        
        return path[::-1]  # Đảo ngược để có đường từ start -> goal
    
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
        
        # Làm tròn start và goal về lưới
        start_pos = (
            round(self.map.start[0] / self.grid_resolution) * self.grid_resolution,
            round(self.map.start[1] / self.grid_resolution) * self.grid_resolution
        )
        goal_pos = (
            round(self.map.goal[0] / self.grid_resolution) * self.grid_resolution,
            round(self.map.goal[1] / self.grid_resolution) * self.grid_resolution
        )
        
        # Khởi tạo
        start_node = Node(start_pos)
        start_node.g = 0
        start_node.h = self.heuristic(start_pos, goal_pos)
        start_node.f = start_node.g + start_node.h
        
        # Open list (priority queue) và closed set
        open_list = []
        heapq.heappush(open_list, start_node)
        closed_set = set()
        open_dict = {start_pos: start_node}
        
        self.nodes_explored = 0
        
        while open_list:
            # Lấy node có f nhỏ nhất
            current_node = heapq.heappop(open_list)
            current_pos = current_node.position
            
            # Xóa khỏi open_dict
            if current_pos in open_dict:
                del open_dict[current_pos]
            
            # Kiểm tra đã đến goal chưa
            if self.heuristic(current_pos, goal_pos) < self.grid_resolution:
                self.computation_time = time.time() - start_time
                self.path = self.reconstruct_path(current_node)
                return self.path
            
            # Thêm vào closed set
            closed_set.add(current_pos)
            self.nodes_explored += 1
            
            # Xét các láng giềng
            for neighbor_pos in self.get_neighbors(current_pos):
                if neighbor_pos in closed_set:
                    continue
                
                # Tính chi phí
                tentative_g = current_node.g + self.heuristic(current_pos, neighbor_pos)
                
                # Kiểm tra xem đã có trong open list chưa
                if neighbor_pos in open_dict:
                    neighbor_node = open_dict[neighbor_pos]
                    if tentative_g < neighbor_node.g:
                        # Tìm được đường tốt hơn
                        neighbor_node.g = tentative_g
                        neighbor_node.f = neighbor_node.g + neighbor_node.h
                        neighbor_node.parent = current_node
                        heapq.heapify(open_list)  # Cập nhật priority queue
                else:
                    # Thêm neighbor mới
                    neighbor_node = Node(neighbor_pos, current_node)
                    neighbor_node.g = tentative_g
                    neighbor_node.h = self.heuristic(neighbor_pos, goal_pos)
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    
                    heapq.heappush(open_list, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node
        
        # Không tìm thấy đường
        self.computation_time = time.time() - start_time
        print("A*: Không tìm thấy đường đi!")
        return None
    
    def get_path_length(self) -> float:
        """Tính độ dài đường đi"""
        if not self.path or len(self.path) < 2:
            return 0
        
        length = 0
        for i in range(len(self.path) - 1):
            length += self.heuristic(self.path[i], self.path[i + 1])
        
        return length


if __name__ == "__main__":
    # Test thuật toán A*
    from generate_map import Map2D
    import matplotlib.pyplot as plt
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Chạy A*
    print("Chạy thuật toán A*...")
    astar = AStar(map_obj, grid_resolution=0.5)
    path = astar.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {astar.get_path_length():.2f} m")
        print(f"  - Thời gian: {astar.computation_time:.4f} s")
        print(f"  - Nodes explored: {astar.nodes_explored}")
        
        # Vẽ kết quả
        fig, ax = plt.subplots(figsize=(10, 10))
        map_obj.visualize()
        
        if path:
            path_array = np.array(path)
            plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, label='A* Path')
            plt.legend()
        
        plt.title(f'A* - Độ dài: {astar.get_path_length():.2f}m, Thời gian: {astar.computation_time:.4f}s')
        plt.show()
