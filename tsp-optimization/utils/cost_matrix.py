"""
Cost Matrix Generator for Multi-Point TSP

Tính ma trận chi phí thực tế giữa mọi cặp điểm bằng RRT/A*
Lưu cache để tránh tính lại nhiều lần
"""

import numpy as np
from utils.core import path_length, smoothness_penalty


class CostMatrix:
    """
    Lưu chi phí thực tế giữa mọi cặp waypoint
    
    Thuộc tính:
    - waypoints: danh sách (N+1) điểm (start + N waypoints)
    - cost_data: dict lưu {(i,j): {'distance': ..., 'path': ..., 'smoothness': ...}}
    - environment: môi trường với chướng ngại vật
    """
    
    def __init__(self, waypoints, environment, planner_type='RRT', 
                 rrt_step=5.0, rrt_max_iter=5000, astar_grid=2.0):
        """
        Args:
            waypoints: list of (x, y) tuples
                      [start, wp1, wp2, ..., wpN]
            environment: UAVEnvironment instance
            planner_type: 'RRT' or 'ASTAR'
            rrt_step: RRT step size
            rrt_max_iter: RRT max iterations
            astar_grid: A* grid resolution
        """
        self.waypoints = waypoints
        self.n = len(waypoints)
        self.environment = environment
        self.planner_type = planner_type
        self.rrt_step = rrt_step
        self.rrt_max_iter = rrt_max_iter
        self.astar_grid = astar_grid
        
        # Cost data: {(i, j): {'distance': float, 'path': list, 'smoothness': float}}
        self.cost_data = {}
        self.total_computations = 0
        self.successful_paths = 0
        
    def compute(self):
        """
        Tính ma trận chi phí cho tất cả cặp điểm
        
        Độ phức tạp: O(N² × path_search_time)
        """
        print(f"\n[CostMatrix] Bắt đầu tính ma trận chi phí ({self.n}x{self.n})")
        print(f"[CostMatrix] Sử dụng {self.planner_type}")
        
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    # Chi phí từ điểm đến chính nó = 0
                    self.cost_data[(i, j)] = {
                        'distance': 0.0,
                        'path': [self.waypoints[i]],
                        'smoothness': 0.0,
                        'success': True
                    }
                else:
                    start = self.waypoints[i]
                    goal = self.waypoints[j]
                    
                    # Tìm đường đi
                    path = self._plan_path(start, goal)
                    
                    if path:
                        dist = path_length(path)
                        smooth = smoothness_penalty(path)
                        self.successful_paths += 1
                    else:
                        dist = float('inf')
                        smooth = 0.0
                        path = []
                    
                    self.cost_data[(i, j)] = {
                        'distance': dist,
                        'path': path,
                        'smoothness': smooth,
                        'success': path is not None and len(path) > 0
                    }
                    
                    self.total_computations += 1
        
        success_rate = (self.successful_paths / max(1, self.total_computations)) * 100
        print(f"[CostMatrix] Hoàn tất! {self.successful_paths}/{self.total_computations} "
              f"đường tìm thành công ({success_rate:.1f}%)")
        
        return self.cost_data
    
    def _plan_path(self, start, goal):
        """
        Tìm đường từ start → goal bằng RRT hoặc A*
        """
        try:
            # Import local để tránh circular import
            from algorithms import RRTPlanner, AStarPlanner
            
            if self.planner_type.upper() == 'RRT':
                planner = RRTPlanner(
                    self.environment,
                    start,
                    goal,
                    step_size=self.rrt_step,
                    max_iter=self.rrt_max_iter
                )
                path = planner.plan()
            elif self.planner_type.upper() == 'ASTAR':
                planner = AStarPlanner(
                    self.environment,
                    start,
                    goal,
                    grid_resolution=self.astar_grid
                )
                path = planner.plan()
            else:
                raise ValueError(f"Unknown planner type: {self.planner_type}")
            
            return path
        except Exception as e:
            print(f"[CostMatrix] Lỗi tìm đường {start}→{goal}: {e}")
            return None
    
    def get_distance(self, i, j):
        """
        Lấy khoảng cách thực tế từ waypoint i → j
        
        Returns:
            float: khoảng cách, hoặc inf nếu không tìm được đường
        """
        if (i, j) in self.cost_data:
            return self.cost_data[(i, j)]['distance']
        return float('inf')
    
    def get_path(self, i, j):
        """
        Lấy đường đi thực tế từ waypoint i → j
        
        Returns:
            list: danh sách điểm hoặc [] nếu không tìm được
        """
        if (i, j) in self.cost_data:
            path = self.cost_data[(i, j)]['path']
            return path if path else []
        return []
    
    def get_smoothness(self, i, j):
        """
        Lấy smoothness penalty của đường từ i → j
        """
        if (i, j) in self.cost_data:
            return self.cost_data[(i, j)]['smoothness']
        return 0.0
    
    def is_path_valid(self, i, j):
        """
        Kiểm tra xem đường từ i → j có tìm thành công không
        """
        if (i, j) in self.cost_data:
            return self.cost_data[(i, j)]['success']
        return False
    
    def compute_total_cost_for_order(self, order, alpha=0.5, beta=0.3, gamma=0.2):
        """
        Tính tổng chi phí cho một thứ tự cụ thể
        
        order: list permutation [wp1_idx, wp2_idx, ..., wpN_idx]
        (start là index 0, implicit)
        
        Cost = α·distance + β·smoothness + γ·penalty
        """
        total_distance = 0.0
        total_smoothness = 0.0
        
        current = 0  # Index of start
        for next_idx in order:
            total_distance += self.get_distance(current, next_idx)
            total_smoothness += self.get_smoothness(current, next_idx)
            current = next_idx
        
        # Normalize (cần định nghĩa expected values)
        # Đơn giản: sử dụng trực tiếp, normalize sau trong PSO
        cost = alpha * total_distance + beta * total_smoothness
        
        return cost
    
    def get_summary(self):
        """In ra thống kê ma trận chi phí"""
        if not self.cost_data:
            print("[CostMatrix] Chưa tính ma trận!")
            return
        
        distances = [v['distance'] for v in self.cost_data.values() 
                    if v['distance'] != float('inf') and v['distance'] > 0]
        
        if distances:
            print(f"\n[CostMatrix Summary]")
            print(f"  - Min distance: {min(distances):.2f}")
            print(f"  - Max distance: {max(distances):.2f}")
            print(f"  - Avg distance: {np.mean(distances):.2f}")
            print(f"  - Median distance: {np.median(distances):.2f}")
        
        invalid = sum(1 for v in self.cost_data.values() if not v['success'])
        print(f"  - Invalid paths: {invalid}/{self.n**2}")
