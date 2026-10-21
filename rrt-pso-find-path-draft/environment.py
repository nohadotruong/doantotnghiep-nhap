"""
UAVEnvironment - Map with obstacles and collision detection
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from geometry import point_in_rectangle, line_rectangle_collision, path_length


class UAVEnvironment:
    """
    Environment containing map dimensions and obstacles.
    
    Handles:
    - Map boundaries (width, height)
    - Obstacle definitions (rectangles)
    - Collision detection (point and line segment)
    - Visualization
    """
    
    def __init__(self, width, height, obstacles=None):
        """
        Initialize environment.
        
        Args:
            width (float): map width
            height (float): map height
            obstacles (list): list of (x, y, w, h) rectangles, default None (no obstacles)
        """
        self.width = width
        self.height = height
        self.obstacles = obstacles if obstacles else []
    
    def is_inside_obstacle(self, x, y):
        """
        Check if point (x, y) is invalid (outside boundary or inside obstacle).
        
        Args:
            x, y (float): point coordinates
        
        Returns:
            bool: True if point is invalid (collision/boundary), False if valid
        """
        # Check boundary
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return True
        
        # Check obstacles
        for ox, oy, ow, oh in self.obstacles:
            if point_in_rectangle(x, y, ox, oy, ow, oh):
                return True
        
        return False
    
    def is_collision(self, p1, p2):
        """
        Check if line segment from p1 to p2 collides with any obstacle.
        
        Args:
            p1, p2 (tuple): points (x, y)
        
        Returns:
            bool: True if collision, False if clear
        """
        x1, y1 = p1
        x2, y2 = p2
        
        # Check endpoints
        if self.is_inside_obstacle(x1, y1) or self.is_inside_obstacle(x2, y2):
            return True
        
        # Check line-obstacle intersection
        for ox, oy, ow, oh in self.obstacles:
            if line_rectangle_collision(x1, y1, x2, y2, ox, oy, ow, oh):
                return True
        
        return False
    
    def visualize(self, path=None, title="Map"):
        """
        Visualize map with obstacles and optional path.
        
        Args:
            path (list): list of (x, y) waypoints, default None
            title (str): figure title
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Set up axes
        ax.set_xlim(-5, self.width + 5)
        ax.set_ylim(-5, self.height + 5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(title)
        
        # Draw obstacles
        for ox, oy, ow, oh in self.obstacles:
            rect = patches.Rectangle((ox, oy), ow, oh, 
                                    linewidth=2, edgecolor='red', 
                                    facecolor='red', alpha=0.5)
            ax.add_patch(rect)
        
        # Draw path if provided
        if path is not None and len(path) > 0:
            path = np.array(path)
            ax.plot(path[:, 0], path[:, 1], 'b-', linewidth=2, label='Path')
            ax.plot(path[0, 0], path[0, 1], 'go', markersize=10, label='Start')
            ax.plot(path[-1, 0], path[-1, 1], 'r*', markersize=15, label='Goal')
            ax.legend()
        
        plt.tight_layout()
        plt.show()
    
    def visualize_multiple_paths(self, paths_dict, title="Map"):
        """
        Visualize map with multiple paths.
        
        Args:
            paths_dict (dict): {'name': path, ...}
            title (str): figure title
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Set up axes
        ax.set_xlim(-5, self.width + 5)
        ax.set_ylim(-5, self.height + 5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(title)
        
        # Draw obstacles
        for ox, oy, ow, oh in self.obstacles:
            rect = patches.Rectangle((ox, oy), ow, oh,
                                    linewidth=2, edgecolor='red',
                                    facecolor='red', alpha=0.5)
            ax.add_patch(rect)
        
        # Colors for different paths
        colors = ['blue', 'green', 'orange', 'purple', 'brown']
        
        # Draw paths
        for idx, (name, path) in enumerate(paths_dict.items()):
            if path is not None and len(path) > 0:
                path = np.array(path)
                color = colors[idx % len(colors)]
                length = path_length(path)
                ax.plot(path[:, 0], path[:, 1], color=color, linewidth=2,
                       label=f'{name} (L={length:.1f})')
                
                if idx == 0:
                    ax.plot(path[0, 0], path[0, 1], 'go', markersize=10, label='Start')
        
        # Goal marker from last path
        last_path = list(paths_dict.values())[-1]
        if last_path is not None and len(last_path) > 0:
            last_path = np.array(last_path)
            ax.plot(last_path[-1, 0], last_path[-1, 1], 'r*', markersize=15, label='Goal')
        
        ax.legend()
        plt.tight_layout()
        plt.show()
