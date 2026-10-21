import numpy as np
import heapq

class AStar:
    """Thuật toán A* cho tìm đường 2D"""
    
    def __init__(self, map_obj, resolution=1.0):
        """
        Khởi tạo A*
        
        Parameters:
        - map_obj: đối tượng Map2D
        - resolution: độ phân giải grid (m/cell)
        """
        self.map = map_obj
        self.resolution = resolution
        self.grid, self.grid_width, self.grid_height = map_obj.get_grid(resolution)
        
    def world_to_grid(self, x, y):
        """Chuyển tọa độ thế giới sang tọa độ grid"""
        grid_x = int(x / self.resolution)
        grid_y = int(y / self.resolution)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x, grid_y):
        """Chuyển tọa độ grid sang tọa độ thế giới"""
        x = grid_x * self.resolution
        y = grid_y * self.resolution
        return x, y
    
    def heuristic(self, pos1, pos2):
        """Hàm heuristic - khoảng cách Euclidean"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_neighbors(self, node):
        """
        Lấy các node láng giềng (8 hướng)
        
        Returns:
        - list of (grid_x, grid_y, cost)
        """
        x, y = node
        neighbors = []
        
        # 8 hướng di chuyển
        directions = [
            (0, 1, 1.0),      # Lên
            (1, 0, 1.0),      # Phải
            (0, -1, 1.0),     # Xuống
            (-1, 0, 1.0),     # Trái
            (1, 1, 1.414),    # Chéo phải trên
            (1, -1, 1.414),   # Chéo phải dưới
            (-1, 1, 1.414),   # Chéo trái trên
            (-1, -1, 1.414)   # Chéo trái dưới
        ]
        
        for dx, dy, cost in directions:
            new_x, new_y = x + dx, y + dy
            
            # Kiểm tra trong biên
            if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                # Kiểm tra không bị chặn
                if self.grid[new_y, new_x] == 0:
                    neighbors.append((new_x, new_y, cost))
        
        return neighbors
    
    def find_path(self, start, goal):
        """
        Tìm đường từ start đến goal
        
        Parameters:
        - start: (x, y) tọa độ thế giới
        - goal: (x, y) tọa độ thế giới
        
        Returns:
        - path: danh sách các điểm [(x, y), ...] hoặc None nếu không tìm được
        """
        # Chuyển sang tọa độ grid
        start_grid = self.world_to_grid(*start)
        goal_grid = self.world_to_grid(*goal)
        
        # Kiểm tra start và goal hợp lệ
        if self.grid[start_grid[1], start_grid[0]] == 1:
            print("Start point is inside an obstacle!")
            return None
        if self.grid[goal_grid[1], goal_grid[0]] == 1:
            print("Goal point is inside an obstacle!")
            return None
        
        # Khởi tạo
        open_set = []
        heapq.heappush(open_set, (0, start_grid))
        
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self.heuristic(start_grid, goal_grid)}
        
        closed_set = set()
        
        while open_set:
            # Lấy node có f_score nhỏ nhất
            current_f, current = heapq.heappop(open_set)
            
            # Đã đến goal
            if current == goal_grid:
                return self._reconstruct_path(came_from, current)
            
            closed_set.add(current)
            
            # Duyệt các láng giềng
            for neighbor_x, neighbor_y, move_cost in self.get_neighbors(current):
                neighbor = (neighbor_x, neighbor_y)
                
                if neighbor in closed_set:
                    continue
                
                # Tính g_score mới
                tentative_g = g_score[current] + move_cost
                
                # Nếu tìm được đường tốt hơn
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, goal_grid)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))
        
        # Không tìm được đường
        print("No path found!")
        return None
    
    def _reconstruct_path(self, came_from, current):
        """Tái tạo đường đi từ start đến goal"""
        path_grid = [current]
        
        while current in came_from:
            current = came_from[current]
            path_grid.append(current)
        
        path_grid.reverse()
        
        # Chuyển về tọa độ thế giới
        path_world = [self.grid_to_world(gx, gy) for gx, gy in path_grid]
        
        return path_world
    
    def get_path_length(self, path):
        """Tính độ dài đường đi"""
        if not path or len(path) < 2:
            return 0
        
        length = 0
        for i in range(len(path) - 1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            length += np.sqrt(dx**2 + dy**2)
        
        return length