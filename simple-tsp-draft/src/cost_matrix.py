import numpy as np
from typing import List, Tuple, Dict
from astar import AStarPathfinder


class CostMatrixBuilder:
    def __init__(self, pathfinder: AStarPathfinder):
        self.pathfinder = pathfinder
        self.cost_matrix = None
        self.paths = {}
    
    def build_cost_matrix(self, points: List[Tuple[int, int]]) -> np.ndarray:
        n = len(points)
        self.cost_matrix = np.full((n, n), float('inf'))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    self.cost_matrix[i, j] = 0
                else:
                    path, cost = self.pathfinder.find_path(points[i], points[j])
                    self.cost_matrix[i, j] = cost
                    
                    key = (i, j)
                    if path is not None:
                        self.paths[key] = path
                    else:
                        self.paths[key] = None
        
        return self.cost_matrix
    
    def get_cost(self, from_idx: int, to_idx: int) -> float:
        if self.cost_matrix is None:
            return float('inf')
        return self.cost_matrix[from_idx, to_idx]
    
    def get_path(self, from_idx: int, to_idx: int) -> List[Tuple[int, int]]:
        key = (from_idx, to_idx)
        return self.paths.get(key, None)
    
    def display_cost_matrix(self, points: List[Tuple[int, int]]):
        if self.cost_matrix is None:
            print("Ma trận chi phí chưa được xây dựng!")
            return
        
        n = len(points)
        print("\n=== MA TRẬN CHI PHÍ ===")
        print("Rows: Từ, Columns: Tới")
        
        header = "      "
        for j in range(n):
            header += f"{j:8d}  "
        print(header)
        
        for i in range(n):
            row = f"{i:4d}  "
            for j in range(n):
                cost = self.cost_matrix[i, j]
                if cost == float('inf'):
                    row += "    ∞    "
                else:
                    row += f"{cost:8.2f}  "
            print(row)
        
        print("\nVị trí các điểm:")
        for i, point in enumerate(points):
            print(f"  {i}: {point}")
