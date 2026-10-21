"""
Module thực hiện thuật toán A* để tìm đường đi giữa hai điểm
"""
import heapq
import math
from typing import List, Tuple, Optional, Dict

class AStarPathfinder:
    """Lớp thực hiện thuật toán A* tìm đường đi"""
    
    def __init__(self, grid, width: int, height: int):
        """
        Khởi tạo A* pathfinder
        
        Args:
            grid: Ma trận bản đồ (0 = ô trống, 1 = chướng ngại vật)
            width: Chiều rộng bản đồ
            height: Chiều cao bản đồ
        """
        self.grid = grid
        self.width = width
        self.height = height
        
    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Tính heuristic sử dụng Euclidean distance
        
        Args:
            pos: Vị trí hiện tại (x, y)
            goal: Vị trí mục tiêu (x, y)
            
        Returns:
            Khoảng cách Euclidean
        """
        dx = pos[0] - goal[0]
        dy = pos[1] - goal[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Lấy các ô lân cận có thể di chuyển tới
        Hỗ trợ 8 hướng (lên, xuống, trái, phải, và 4 hướng chéo)
        
        Args:
            pos: Vị trí hiện tại (x, y)
            
        Returns:
            Danh sách các ô lân cận hợp lệ
        """
        x, y = pos
        neighbors = []
        
        # 8 hướng di chuyển
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),  # Lên, xuống, trái, phải
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Chéo
        ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 
                0 <= ny < self.height and 
                self.grid[ny, nx] == 0):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def get_cost(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Tính chi phí di chuyển giữa hai ô
        Chéo = √2, ngang/dọc = 1
        """
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        
        if dx == 1 and dy == 1:  # Chéo
            return math.sqrt(2)
        else:  # Ngang hoặc dọc
            return 1.0
    
    def find_path(self, start: Tuple[int, int], 
                  goal: Tuple[int, int]) -> Tuple[Optional[List[Tuple[int, int]]], float]:
        """
        Tìm đường đi từ start đến goal sử dụng A*
        
        Args:
            start: Vị trí bắt đầu (x, y)
            goal: Vị trí mục tiêu (x, y)
            
        Returns:
            (Danh sách các vị trí trên đường đi, Chi phí đường đi)
            Nếu không tìm được đường đi, trả về (None, float('inf'))
        """
        # Kiểm tra start và goal có hợp lệ không
        if (self.grid[start[1], start[0]] == 1 or 
            self.grid[goal[1], goal[0]] == 1):
            return None, float('inf')
        
        # Priority queue: (f_score, counter, position)
        counter = 0
        open_set = [(0, counter, start)]
        counter += 1
        
        # Lưu thông tin của node
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        f_score: Dict[Tuple[int, int], float] = {start: self.heuristic(start, goal)}
        
        visited = set()
        
        while open_set:
            _, _, current = heapq.heappop(open_set)
            
            if current in visited:
                continue
                
            visited.add(current)
            
            # Tìm được mục tiêu
            if current == goal:
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                return path[::-1], g_score[goal]
            
            # Kiểm tra các neighbor
            for neighbor in self.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                tentative_g = g_score[current] + self.get_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                    counter += 1
        
        # Không tìm được đường đi
        return None, float('inf')
