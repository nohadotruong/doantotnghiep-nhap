"""
generate_map.py - Tạo bản đồ mô phỏng đô thị 2D cho UAV
"""
import numpy as np
import json
import os
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Obstacle:
    """Lớp đại diện cho chướng ngại vật hình chữ nhật"""
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def contains_point(self, px: float, py: float) -> bool:
        """Kiểm tra điểm có nằm trong chướng ngại vật không"""
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def intersects_line(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        """Kiểm tra đoạn thẳng có cắt chướng ngại vật không"""
        x1, y1 = p1
        x2, y2 = p2
        
        # Kiểm tra các cạnh của hình chữ nhật
        edges = [
            ((self.x, self.y), (self.x + self.width, self.y)),
            ((self.x + self.width, self.y), (self.x + self.width, self.y + self.height)),
            ((self.x + self.width, self.y + self.height), (self.x, self.y + self.height)),
            ((self.x, self.y + self.height), (self.x, self.y))
        ]
        
        for edge in edges:
            if self._line_intersect(p1, p2, edge[0], edge[1]):
                return True
        
        # Kiểm tra điểm đầu/cuối có nằm trong chướng ngại vật
        if self.contains_point(x1, y1) or self.contains_point(x2, y2):
            return True
        
        return False
    
    def _line_intersect(self, p1, p2, p3, p4):
        """Kiểm tra 2 đoạn thẳng có giao nhau không"""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return False
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        return 0 <= t <= 1 and 0 <= u <= 1
    
    def to_dict(self) -> Dict:
        """Chuyển đổi sang dictionary"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }


class Map2D:
    """Lớp quản lý bản đồ 2D"""
    def __init__(self, width: float = 100, height: float = 100):
        self.width = width
        self.height = height
        self.obstacles: List[Obstacle] = []
        self.start = None
        self.goal = None
    
    def add_obstacle(self, obstacle: Obstacle):
        """Thêm chướng ngại vật"""
        self.obstacles.append(obstacle)
    
    def set_start(self, x: float, y: float):
        """Đặt điểm bắt đầu"""
        self.start = (x, y)
    
    def set_goal(self, x: float, y: float):
        """Đặt điểm đích"""
        self.goal = (x, y)
    
    def is_valid_point(self, x: float, y: float) -> bool:
        """Kiểm tra điểm có hợp lệ (trong map và không va chướng ngại vật)"""
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return False
        
        for obstacle in self.obstacles:
            if obstacle.contains_point(x, y):
                return False
        
        return True
    
    def is_valid_path(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        """Kiểm tra đường đi có hợp lệ (không cắt chướng ngại vật)"""
        for obstacle in self.obstacles:
            if obstacle.intersects_line(p1, p2):
                return False
        return True
    
    def save(self, filename: str):
        """Lưu bản đồ ra file JSON"""
        data = {
            'width': self.width,
            'height': self.height,
            'start': self.start,
            'goal': self.goal,
            'obstacles': [obs.to_dict() for obs in self.obstacles]
        }
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Đã lưu bản đồ vào {filename}")
    
    @staticmethod
    def load(filename: str) -> 'Map2D':
        """Đọc bản đồ từ file JSON"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        map_obj = Map2D(data['width'], data['height'])
        
        for obs_data in data['obstacles']:
            obstacle = Obstacle(
                obs_data['x'], 
                obs_data['y'], 
                obs_data['width'], 
                obs_data['height']
            )
            map_obj.add_obstacle(obstacle)
        
        if data.get('start'):
            map_obj.start = tuple(data['start'])
        if data.get('goal'):
            map_obj.goal = tuple(data['goal'])
        
        return map_obj
    
    def visualize(self, save_path: str = None):
        """Vẽ bản đồ"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Vẽ các chướng ngại vật
        for obstacle in self.obstacles:
            rect = patches.Rectangle(
                (obstacle.x, obstacle.y), 
                obstacle.width, 
                obstacle.height,
                linewidth=1, 
                edgecolor='black', 
                facecolor='gray'
            )
            ax.add_patch(rect)
        
        # Vẽ điểm bắt đầu và đích
        if self.start:
            ax.plot(self.start[0], self.start[1], 'go', markersize=15, label='Start')
        if self.goal:
            ax.plot(self.goal[0], self.goal[1], 'r*', markersize=20, label='Goal')
        
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_title('Bản đồ 2D cho UAV')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()


def generate_random_map(width: float = 100, height: float = 100, 
                       num_obstacles: int = 20,
                       min_size: float = 3, max_size: float = 15) -> Map2D:
    """
    Tạo bản đồ ngẫu nhiên
    
    Args:
        width: Chiều rộng bản đồ
        height: Chiều cao bản đồ
        num_obstacles: Số lượng chướng ngại vật
        min_size: Kích thước tối thiểu
        max_size: Kích thước tối đa
    """
    map_obj = Map2D(width, height)
    
    # Tạo các chướng ngại vật ngẫu nhiên
    for _ in range(num_obstacles):
        obs_width = np.random.uniform(min_size, max_size)
        obs_height = np.random.uniform(min_size, max_size)
        obs_x = np.random.uniform(0, width - obs_width)
        obs_y = np.random.uniform(0, height - obs_height)
        
        obstacle = Obstacle(obs_x, obs_y, obs_width, obs_height)
        map_obj.add_obstacle(obstacle)
    
    # Tạo điểm bắt đầu và đích hợp lệ
    while True:
        start_x = np.random.uniform(5, 20)
        start_y = np.random.uniform(5, 20)
        if map_obj.is_valid_point(start_x, start_y):
            map_obj.set_start(start_x, start_y)
            break
    
    while True:
        goal_x = np.random.uniform(width - 20, width - 5)
        goal_y = np.random.uniform(height - 20, height - 5)
        if map_obj.is_valid_point(goal_x, goal_y):
            map_obj.set_goal(goal_x, goal_y)
            break
    
    return map_obj


def generate_urban_map(width: float = 100, height: float = 100) -> Map2D:
    """Tạo bản đồ mô phỏng đô thị với các tòa nhà"""
    map_obj = Map2D(width, height)
    
    # Tạo lưới các tòa nhà (mô phỏng khu đô thị)
    building_sizes = [
        (15, 15), (20, 10), (12, 18), (25, 8), (10, 20),
        (18, 12), (8, 25), (15, 15), (22, 12)
    ]
    
    positions = [
        (10, 10), (35, 8), (65, 15),
        (8, 40), (40, 35), (70, 40),
        (15, 70), (45, 65), (75, 75)
    ]
    
    for (x, y), (w, h) in zip(positions, building_sizes):
        map_obj.add_obstacle(Obstacle(x, y, w, h))
    
    # Đặt điểm bắt đầu và đích
    map_obj.set_start(5, 5)
    map_obj.set_goal(95, 95)
    
    return map_obj


def generate_corridor_map(width: float = 100, height: float = 100) -> Map2D:
    """Tạo bản đồ với hành lang hẹp"""
    map_obj = Map2D(width, height)
    
    # Tạo các tường tạo hành lang
    map_obj.add_obstacle(Obstacle(0, 30, 40, 15))
    map_obj.add_obstacle(Obstacle(60, 30, 40, 15))
    map_obj.add_obstacle(Obstacle(0, 55, 40, 15))
    map_obj.add_obstacle(Obstacle(60, 55, 40, 15))
    
    # Thêm chướng ngại vật phức tạp
    map_obj.add_obstacle(Obstacle(25, 10, 10, 15))
    map_obj.add_obstacle(Obstacle(65, 10, 10, 15))
    map_obj.add_obstacle(Obstacle(25, 75, 10, 15))
    map_obj.add_obstacle(Obstacle(65, 75, 10, 15))
    
    map_obj.set_start(5, 50)
    map_obj.set_goal(95, 50)
    
    return map_obj


if __name__ == "__main__":
    # Tạo thư mục maps nếu chưa tồn tại
    os.makedirs('./maps', exist_ok=True)
    
    print("=== Tạo bản đồ cho UAV ===\n")
    
    # 1. Bản đồ ngẫu nhiên
    print("1. Tạo bản đồ ngẫu nhiên...")
    random_map = generate_random_map(width=100, height=100, num_obstacles=20)
    random_map.save('./maps/random_map.json')
    random_map.visualize('./maps/random_map.png')
    
    # 2. Bản đồ đô thị
    print("\n2. Tạo bản đồ đô thị...")
    urban_map = generate_urban_map()
    urban_map.save('./maps/urban_map.json')
    urban_map.visualize('./maps/urban_map.png')
    
    # 3. Bản đồ hành lang
    print("\n3. Tạo bản đồ hành lang...")
    corridor_map = generate_corridor_map()
    corridor_map.save('./maps/corridor_map.json')
    corridor_map.visualize('./maps/corridor_map.png')
    
    # 4. Bản đồ đơn giản (để test)
    print("\n4. Tạo bản đồ đơn giản...")
    simple_map = Map2D(100, 100)
    simple_map.add_obstacle(Obstacle(30, 30, 20, 20))
    simple_map.add_obstacle(Obstacle(60, 60, 15, 15))
    simple_map.set_start(10, 10)
    simple_map.set_goal(90, 90)
    simple_map.save('./maps/simple_map.json')
    simple_map.visualize('./maps/simple_map.png')
    
    print("\n✓ Đã tạo xong tất cả bản đồ!")
