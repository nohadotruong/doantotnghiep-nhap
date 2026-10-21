import numpy as np
from typing import List, Tuple, Dict


class GreedyTSP:
    def __init__(self, cost_matrix: np.ndarray):
        self.cost_matrix = cost_matrix
        self.route = None
        self.total_cost = 0
    
    def solve(self, start: int = 0) -> Tuple[List[int], float]:
        n = len(self.cost_matrix)
        
        unvisited = set(range(n))
        current = start
        route = [current]
        unvisited.remove(current)
        total_cost = 0
        
        while unvisited:
            nearest = min(unvisited, 
                         key=lambda x: self.cost_matrix[current, x])
            cost = self.cost_matrix[current, nearest]
            total_cost += cost
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        total_cost += self.cost_matrix[current, start]
        route.append(start)
        
        self.route = route
        self.total_cost = total_cost
        
        return route, total_cost
    
    def get_route_description(self, points: List[Tuple[int, int]]) -> str:
        if self.route is None:
            return "Chưa tìm lộ trình!"
        
        description = "Lộ trình tối ưu:\n"
        description += f"Điểm bắt đầu: {points[self.route[0]]}\n"
        
        for i in range(len(self.route) - 1):
            from_idx = self.route[i]
            to_idx = self.route[i + 1]
            cost = self.cost_matrix[from_idx, to_idx]
            
            if i == len(self.route) - 2:
                description += f"→ {points[to_idx]} (Quay về, chi phí: {cost:.2f})\n"
            else:
                description += f"→ {points[to_idx]} (chi phí: {cost:.2f})\n"
        
        return description
    
    def get_detailed_route(self, points: List[Tuple[int, int]]) -> Dict:
        if self.route is None:
            return {}
        
        details = {
            'route_indices': self.route,
            'route_coordinates': [points[i] for i in self.route],
            'total_cost': self.total_cost,
            'segments': []
        }
        
        for i in range(len(self.route) - 1):
            from_idx = self.route[i]
            to_idx = self.route[i + 1]
            cost = self.cost_matrix[from_idx, to_idx]
            
            details['segments'].append({
                'from': from_idx,
                'to': to_idx,
                'from_coord': points[from_idx],
                'to_coord': points[to_idx],
                'cost': cost
            })
        
        return details
