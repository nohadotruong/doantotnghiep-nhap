"""
Module khởi tạo bản đồ với chướng ngại vật và điểm đến
"""
import numpy as np
import random
from typing import List, Tuple

class MapBuilder:
    """Lớp để xây dựng bản đồ với chướng ngại vật"""
    
    def __init__(self, width: int = 20, height: int = 20):
        """
        Khởi tạo bản đồ
        
        Args:
            width: Chiều rộng bản đồ
            height: Chiều cao bản đồ
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.obstacles = []
        self.targets = []
        self.start = None
        
    def add_obstacles(self, num_obstacles: int = 15, obstacle_size: int = 2):
        """
        Thêm các chướng ngại vật ngẫu nhiên vào bản đồ
        
        Args:
            num_obstacles: Số lượng chướng ngại vật
            obstacle_size: Kích thước của mỗi chướng ngại vật
        """
        for _ in range(num_obstacles):
            x = random.randint(0, self.width - obstacle_size - 1)
            y = random.randint(0, self.height - obstacle_size - 1)
            
            for dx in range(obstacle_size):
                for dy in range(obstacle_size):
                    if x + dx < self.width and y + dy < self.height:
                        self.grid[y + dy, x + dx] = 1  # 1 = chướng ngại vật
                        self.obstacles.append((x + dx, y + dy))
        
        self.obstacles = list(set(self.obstacles))  # Loại bỏ trùng lặp
    
    def add_targets(self, num_targets: int = 5):
        """
        Thêm các điểm đích ngẫu nhiên trên bản đồ
        
        Args:
            num_targets: Số lượng điểm đích
        """
        self.targets = []
        while len(self.targets) < num_targets:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if self.grid[y, x] == 0 and (x, y) not in self.targets:
                self.targets.append((x, y))
        
        self.targets = sorted(self.targets)  # Để có kết quả nhất quán
    
    def set_start_position(self, x: int = None, y: int = None):
        """
        Đặt vị trí bắt đầu
        
        Args:
            x, y: Tọa độ vị trí bắt đầu
        """
        if x is None or y is None:
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if self.grid[y, x] == 0:
                    break
        
        self.start = (x, y)
    
    def get_map_info(self):
        """Trả về thông tin bản đồ"""
        return {
            'width': self.width,
            'height': self.height,
            'start': self.start,
            'targets': self.targets,
            'obstacles': self.obstacles,
            'grid': self.grid
        }
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Kiểm tra vị trí có hợp lệ không"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y, x] == 0)
