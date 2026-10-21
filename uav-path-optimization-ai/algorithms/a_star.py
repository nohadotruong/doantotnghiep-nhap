"""
A* Pathfinding Algorithm Implementation
Finds the optimal path from start to goal avoiding obstacles
"""

import numpy as np
import heapq
from typing import List, Tuple, Optional
from generate_map import Map2D


class Node:
    """
    Represents a node in the search space for A* algorithm
    
    Attributes:
        x, y: Coordinates of the node
        g_cost: Cost from start node to current node
        h_cost: Heuristic cost from current node to goal
        f_cost: Total estimated cost (g + h)
        parent: Reference to parent node for path reconstruction
    """
    
    def __init__(self, x: float, y: float):
        """Initialize a node with given coordinates"""
        self.x = x
        self.y = y
        self.g_cost = float('inf')  # Cost from start to this node
        self.h_cost = 0              # Heuristic cost from this node to goal
        self.f_cost = float('inf')   # Total cost (g + h)
        self.parent: Optional['Node'] = None  # Parent node for path reconstruction
    
    def __lt__(self, other):
        """Compare nodes by f_cost for priority queue ordering"""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """Check if two nodes are at the same position"""
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """Make node hashable so it can be used in sets and dicts"""
        return hash((self.x, self.y))


class AStar:
    """
    A* Pathfinding Algorithm Implementation
    
    Uses a heuristic to efficiently find the shortest path from start to goal
    while avoiding obstacles.
    """
    
    def __init__(self, map_obj: Map2D, step_size: float = 1.0):
        """
        Initialize A* planner
        
        Args:
            map_obj: Map2D object containing obstacles, start, and goal
            step_size: Distance between adjacent nodes in the search space
        """
        self.map = map_obj
        self.step_size = step_size
        self.computation_time = 0
    
    def heuristic(self, current: Tuple[float, float], 
                  goal: Tuple[float, float]) -> float:
        """
        Euclidean distance heuristic (straight-line distance)
        
        Args:
            current: Current position (x, y)
            goal: Goal position (x, y)
            
        Returns:
            Euclidean distance between current and goal
        """
        dx = current[0] - goal[0]
        dy = current[1] - goal[1]
        return np.sqrt(dx**2 + dy**2)
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """
        Get all valid neighboring nodes from current node
        
        Considers 8 directions (4-connected + diagonals).
        A neighbor is valid if it doesn't collide with obstacles.
        
        Args:
            node: Current node
            
        Returns:
            List of valid neighboring nodes
        """
        neighbors = []
        
        # 8 directions: right, left, up, down, and 4 diagonals
        directions = [
            (self.step_size, 0),              # Right
            (-self.step_size, 0),             # Left
            (0, self.step_size),              # Up
            (0, -self.step_size),             # Down
            (self.step_size, self.step_size), # Up-Right
            (-self.step_size, self.step_size),# Up-Left
            (self.step_size, -self.step_size),# Down-Right
            (-self.step_size, -self.step_size)# Down-Left
        ]
        
        for dx, dy in directions:
            new_x = node.x + dx
            new_y = node.y + dy
            
            # Check if new position is within map boundaries
            within_bounds = (0 <= new_x <= self.map.width and 
                           0 <= new_y <= self.map.height)
            
            # Check if new position doesn't collide with obstacles
            is_collision_free = not self.map.is_collision(new_x, new_y, radius=0.3)
            
            if within_bounds and is_collision_free:
                neighbors.append(Node(new_x, new_y))
        
        return neighbors
    
    def find_path(self) -> List[Tuple[float, float]]:
        """
        Find optimal path from start to goal using A* algorithm
        
        Algorithm overview:
        1. Start with the start node in the open set
        2. Always expand the node with lowest f_cost
        3. For each neighbor, update cost if better path found
        4. Stop when goal is reached or no path exists
        
        Returns:
            List of coordinates from start to goal, or empty list if no path found
        """
        # Validate start and goal are set
        if not self.map.start or not self.map.goal:
            return []
        
        # Initialize start and goal nodes
        start_node = Node(self.map.start[0], self.map.start[1])
        goal_position = self.map.goal
        
        # Set initial costs for start node
        start_node.g_cost = 0
        start_node.h_cost = self.heuristic(
            (start_node.x, start_node.y), 
            goal_position
        )
        start_node.f_cost = start_node.h_cost
        
        # Open set: nodes to be evaluated (priority queue ordered by f_cost)
        open_set = []
        # Dictionary to quickly check if node is in open set
        open_nodes_map = {}
        # Closed set: already evaluated nodes
        closed_nodes = set()
        
        # Add start node to open set
        heapq.heappush(open_set, start_node)
        open_nodes_map[start_node] = start_node
        
        # Main A* loop
        while open_set:
            # Get node with lowest f_cost from open set
            current_node = heapq.heappop(open_set)
            del open_nodes_map[current_node]
            
            # Check if we reached the goal (within one step)
            distance_to_goal = self.heuristic(
                (current_node.x, current_node.y), 
                goal_position
            )
            if distance_to_goal < self.step_size:
                return self.reconstruct_path(current_node)
            
            # Mark current node as evaluated
            closed_nodes.add(current_node)
            
            # Evaluate all neighbors
            for neighbor in self.get_neighbors(current_node):
                # Skip if already evaluated
                if neighbor in closed_nodes:
                    continue
                
                # Calculate cost from start to this neighbor through current node
                distance = self.heuristic(
                    (current_node.x, current_node.y),
                    (neighbor.x, neighbor.y)
                )
                tentative_g_cost = current_node.g_cost + distance
                
                # If neighbor already in open set, check if new path is better
                if neighbor in open_nodes_map:
                    if tentative_g_cost < neighbor.g_cost:
                        # Found better path to neighbor
                        neighbor.g_cost = tentative_g_cost
                        neighbor.parent = current_node
                        neighbor.h_cost = self.heuristic(
                            (neighbor.x, neighbor.y), 
                            goal_position
                        )
                        neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                else:
                    # New node, add to open set
                    neighbor.g_cost = tentative_g_cost
                    neighbor.parent = current_node
                    neighbor.h_cost = self.heuristic(
                        (neighbor.x, neighbor.y), 
                        goal_position
                    )
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    heapq.heappush(open_set, neighbor)
                    open_nodes_map[neighbor] = neighbor
        
        # No path found
        return []
    
    def reconstruct_path(self, node: Node) -> List[Tuple[float, float]]:
        """
        Reconstruct path from start to goal by backtracking through parent links
        
        Args:
            node: Final (goal) node
            
        Returns:
            List of coordinates from start to goal
        """
        path = []
        current = node
        
        # Backtrack from goal to start following parent links
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        
        # Reverse to get path from start to goal
        path.reverse()
        return path


def a_star_path_planning(map_obj: Map2D, step_size: float = 1.0) -> List[Tuple[float, float]]:
    a_star = AStar(map_obj, step_size)
    return a_star.find_path()
