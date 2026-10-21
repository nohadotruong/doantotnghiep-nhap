"""
RRT (Rapidly-exploring Random Tree) Algorithm for Path Planning

Includes:
- Node: Data structure for tree nodes
- RRTPlanner: Goal-biased RRT algorithm
"""

import random
import math
from geometry import distance


class Node:
    """
    Node in RRT tree.
    
    Attributes:
        x, y (float): coordinates
        parent (Node): parent node for backtracking
    """
    
    def __init__(self, x, y, parent=None):
        """
        Initialize node.
        
        Args:
            x, y (float): coordinates
            parent (Node): parent node, default None
        """
        self.x = float(x)
        self.y = float(y)
        self.parent = parent
    
    def distance_to(self, other):
        """
        Euclidean distance to another node.
        
        Args:
            other (Node or tuple): target
        
        Returns:
            float: distance
        """
        if isinstance(other, tuple):
            return distance((self.x, self.y), other)
        return distance((self.x, self.y), (other.x, other.y))
    
    def __repr__(self):
        return f"Node({self.x:.1f}, {self.y:.1f})"


class RRTPlanner:
    """
    Goal-biased RRT algorithm for path planning.
    
    Grows a tree from start toward goal while avoiding obstacles.
    """
    
    def __init__(self, environment, start, goal, 
                 step_size=5.0, max_iter=5000, goal_sample_rate=0.2):
        """
        Initialize RRT planner.
        
        Args:
            environment (UAVEnvironment): map with obstacles
            start (tuple): start position (x, y)
            goal (tuple): goal position (x, y)
            step_size (float): step size per iteration, default 5.0
            max_iter (int): max iterations, default 5000
            goal_sample_rate (float): probability to sample goal, default 0.2
        """
        self.environment = environment
        self.start = Node(start[0], start[1])
        self.goal = Node(goal[0], goal[1])
        self.step_size = step_size
        self.max_iter = max_iter
        self.goal_sample_rate = goal_sample_rate
        self.tree = [self.start]
    
    def sample(self):
        """
        Sample a random point.
        
        With probability goal_sample_rate, return goal.
        Otherwise return random point in map.
        
        Returns:
            Node: sampled point
        """
        if random.random() < self.goal_sample_rate:
            return self.goal
        
        x = random.uniform(0, self.environment.width)
        y = random.uniform(0, self.environment.height)
        return Node(x, y)
    
    def nearest(self, point):
        """
        Find nearest node in tree to given point.
        
        Args:
            point (Node or tuple): target point
        
        Returns:
            Node: nearest node in tree
        """
        if not isinstance(point, Node):
            point = Node(point[0], point[1])
        
        nearest_node = self.tree[0]
        min_dist = nearest_node.distance_to(point)
        
        for node in self.tree[1:]:
            dist = node.distance_to(point)
            if dist < min_dist:
                min_dist = dist
                nearest_node = node
        
        return nearest_node
    
    def steer(self, from_node, to_point):
        """
        Move from_node toward to_point by step_size.
        
        Args:
            from_node (Node): starting node
            to_point (Node or tuple): target direction
        
        Returns:
            Node: new node at distance step_size
        """
        if not isinstance(to_point, Node):
            to_point = Node(to_point[0], to_point[1])
        
        dist = from_node.distance_to(to_point)
        
        if dist < self.step_size:
            return Node(to_point.x, to_point.y, parent=from_node)
        
        # Move step_size toward to_point
        dx = to_point.x - from_node.x
        dy = to_point.y - from_node.y
        
        dx = dx / dist * self.step_size
        dy = dy / dist * self.step_size
        
        new_x = from_node.x + dx
        new_y = from_node.y + dy
        
        return Node(new_x, new_y, parent=from_node)
    
    def plan(self):
        """
        Run RRT algorithm to find path.
        
        Returns:
            list: [(x1,y1), (x2,y2), ..., goal] if path found, None otherwise
        """
        for iteration in range(self.max_iter):
            # Sample random point
            random_point = self.sample()
            
            # Find nearest node in tree
            nearest = self.nearest(random_point)
            
            # Move toward random point
            new_node = self.steer(nearest, random_point)
            
            # Check collision
            if not self.environment.is_collision((nearest.x, nearest.y),
                                                 (new_node.x, new_node.y)):
                # Add to tree
                self.tree.append(new_node)
                
                # Check if near goal
                if new_node.distance_to(self.goal) < self.step_size:
                    # Try to reach goal
                    goal_node = Node(self.goal.x, self.goal.y, parent=new_node)
                    
                    if not self.environment.is_collision((new_node.x, new_node.y),
                                                         (goal_node.x, goal_node.y)):
                        # Found path!
                        self.tree.append(goal_node)
                        return self._extract_path(goal_node)
        
        return None
    
    def _extract_path(self, node):
        """
        Backtrack from goal to start to extract path.
        
        Args:
            node (Node): final node
        
        Returns:
            list: [(x1,y1), (x2,y2), ..., (xn,yn)] from start to goal
        """
        path = []
        current = node
        
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        
        path.reverse()
        return path
