import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class Map2D:
    """Bản đồ 2D đơn giản cho UAV path planning"""
    
    def __init__(self, width=100, height=100):
        """
        Khởi tạo bản đồ 2D
        
        Parameters:
        - width: Chiều rộng (m)
        - height: Chiều dài (m)
        """
        self.width = width
        self.height = height
        self.obstacles = []
        
    def add_obstacle(self, x, y, w, h):
        """Thêm vật cản vào bản đồ"""
        self.obstacles.append({
            'x': x,
            'y': y,
            'width': w,
            'height': h
        })
        
    def generate_random_obstacles(self, num_obstacles=50, seed=None):
        """Tạo vật cản ngẫu nhiên"""
        np.random.seed(seed)
        
        for _ in range(num_obstacles):
            w = np.random.uniform(3, 12)
            h = np.random.uniform(3, 12)
            x = np.random.uniform(5, self.width - w - 5)
            y = np.random.uniform(5, self.height - h - 5)
            
            self.add_obstacle(x, y, w, h)
    
    def is_collision(self, x, y, margin=1.0):
        """
        Kiểm tra va chạm tại điểm (x, y)
        
        Parameters:
        - x, y: Tọa độ kiểm tra
        - margin: Khoảng cách an toàn
        
        Returns:
        - True nếu va chạm, False nếu tự do
        """
        for obs in self.obstacles:
            if (obs['x'] - margin <= x <= obs['x'] + obs['width'] + margin and
                obs['y'] - margin <= y <= obs['y'] + obs['height'] + margin):
                return True
        return False
    
    def get_grid(self, resolution=1.0):
        """
        Tạo occupancy grid
        
        Parameters:
        - resolution: Độ phân giải (m/cell)
        
        Returns:
        - grid: ma trận 2D (0=free, 1=occupied)
        - grid_width, grid_height: kích thước grid
        """
        grid_width = int(self.width / resolution)
        grid_height = int(self.height / resolution)
        grid = np.zeros((grid_height, grid_width), dtype=int)
        
        for i in range(grid_height):
            for j in range(grid_width):
                x = j * resolution
                y = i * resolution
                if self.is_collision(x, y, margin=0):
                    grid[i, j] = 1
        
        return grid, grid_width, grid_height
    
    def visualize(self, start=None, goal=None, path=None, title="2D Map"):
        """
        Vẽ bản đồ
        
        Parameters:
        - start: điểm bắt đầu (x, y)
        - goal: điểm kết thúc (x, y)
        - path: danh sách các điểm [(x, y), ...]
        - title: tiêu đề
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Vẽ vật cản
        for obs in self.obstacles:
            rect = Rectangle((obs['x'], obs['y']), obs['width'], obs['height'],
                           facecolor='#2C3E50', edgecolor='black', 
                           linewidth=1.2, alpha=0.8)
            ax.add_patch(rect)
        
        # Vẽ start
        if start:
            ax.plot(start[0], start[1], 'go', markersize=15, 
                   markeredgecolor='darkgreen', markeredgewidth=2.5,
                   label='Start', zorder=5)
        
        # Vẽ goal
        if goal:
            ax.plot(goal[0], goal[1], 'r*', markersize=25,
                   markeredgecolor='darkred', markeredgewidth=2,
                   label='Goal', zorder=5)
        
        # Vẽ đường đi
        if path:
            path_array = np.array(path)
            ax.plot(path_array[:, 0], path_array[:, 1], 'b-',
                   linewidth=2.5, label='Path', alpha=0.7, zorder=4)
            ax.plot(path_array[:, 0], path_array[:, 1], 'co',
                   markersize=4, alpha=0.5)
        
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_xlabel('X (m)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y (m)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal')
        
        if start or goal or path:
            ax.legend(fontsize=11, loc='best')
        
        plt.tight_layout()
        return fig, ax