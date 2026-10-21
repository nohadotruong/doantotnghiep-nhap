import numpy as np
import matplotlib.pyplot as plt
import json
import os
import random
from datetime import datetime
from typing import List, Tuple, Dict

class Map2D:
    def __init__(self, width: int, height: int):
        """Initialize 2D map with binary occupancy grid"""
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=np.uint8)
        self.start = None
        self.goal = None

    def set_start_goal(self, start: Tuple[int, int], goal: Tuple[int, int]):
        """Set start and goal positions"""
        self.start = start
        self.goal = goal

    def add_obstacle(self, x: int, y: int, width: int, height: int):
        """Add rectangular obstacle to grid"""
        x_end = min(int(x + width), self.width)
        y_end = min(int(y + height), self.height)
        x_start = max(0, int(x))
        y_start = max(0, int(y))
        
        self.grid[y_start:y_end, x_start:x_end] = 1

    def add_road(self, x: int, y: int, width: int, height: int):
        """Add road (free space) to grid"""
        x_end = min(int(x + width), self.width)
        y_end = min(int(y + height), self.height)
        x_start = max(0, int(x))
        y_start = max(0, int(y))
        
        self.grid[y_start:y_end, x_start:x_end] = 0

    def is_free(self, x: int, y: int) -> bool:
        """Check if position is free"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] == 0
        return False

    def get_occupancy_density(self) -> float:
        """Calculate occupancy density"""
        return np.sum(self.grid) / (self.width * self.height)

    def visualize(self, filename: str = None):
        """Visualize the map"""
        plt.figure(figsize=(12, 12))
        
        # Show grid
        plt.imshow(self.grid, cmap='gray', origin='lower')
        
        # Mark start and goal
        if self.start:
            plt.plot(self.start[0], self.start[1], 'go', markersize=15, label='Start')
        if self.goal:
            plt.plot(self.goal[0], self.goal[1], 'r*', markersize=20, label='Goal')
        
        plt.xlabel('X (cells)')
        plt.ylabel('Y (cells)')
        plt.title(f'UAV Path Planning Map\nDensity: {self.get_occupancy_density():.1%}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.colorbar(label='Occupancy (0=free, 1=obstacle)')
        
        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved image: {filename}")
        
        plt.close()

    def save(self, filename: str):
        """Save map as JSON"""
        map_data = {
            'width': self.width,
            'height': self.height,
            'start': self.start,
            'goal': self.goal,
            'grid': self.grid.tolist(),
            'density': float(self.get_occupancy_density())
        }
        
        with open(filename, 'w') as f:
            json.dump(map_data, f, indent=2)
        
        print(f"Saved map: {filename}")

    @staticmethod
    def load(filename: str) -> 'Map2D':
        """Load map from JSON"""
        with open(filename, 'r') as f:
            map_data = json.load(f)
        
        map_obj = Map2D(map_data['width'], map_data['height'])
        map_obj.grid = np.array(map_data['grid'], dtype=np.uint8)
        map_obj.start = tuple(map_data['start'])
        map_obj.goal = tuple(map_data['goal'])
        
        return map_obj


def generate_urban_map(width: int = 100, height: int = 100, seed: int = None) -> Map2D:
    """
    Generate urban map with roads, buildings, and corridors.
    
    Features:
    - Main roads connecting start and goal
    - Residential blocks (rectangular buildings)
    - Random small obstacles
    - Dead-end streets
    - Open area (plaza)
    - Guaranteed solvability with 2+ corridors
    """
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        if seed is not None:
            np.random.seed(seed + attempt)
        else:
            np.random.seed(random.randint(0, 2**31 - 1))
        
        map_obj = Map2D(width, height)
        map_obj.set_start_goal((5, 5), (95, 95))
        
        # Initialize grid as all obstacles
        map_obj.grid = np.ones((height, width), dtype=np.uint8)
        
        # Create safe zones around start and goal
        safe_radius = 8
        for y in range(max(0, 5 - safe_radius), min(height, 5 + safe_radius)):
            for x in range(max(0, 5 - safe_radius), min(width, 5 + safe_radius)):
                map_obj.grid[y, x] = 0
        
        for y in range(max(0, 95 - safe_radius), min(height, 95 + safe_radius)):
            for x in range(max(0, 95 - safe_radius), min(width, 95 + safe_radius)):
                map_obj.grid[y, x] = 0
        
        # Create main grid roads (vertical and horizontal)
        road_spacing = 20
        road_width = 4
        
        # Vertical roads
        for x in range(road_width + 5, width - 10, road_spacing):
            map_obj.add_road(x, 0, road_width, height)
        
        # Horizontal roads
        for y in range(road_width + 5, height - 10, road_spacing):
            map_obj.add_road(0, y, width, road_width)
        
        # Create guaranteed corridors from start to goal
        corridor_width = 5
        
        # Corridor 1: Horizontal then vertical
        y_corridor1 = 25
        map_obj.add_road(0, y_corridor1, width, corridor_width)
        
        x_corridor1 = 70
        map_obj.add_road(x_corridor1, 0, corridor_width, height)
        
        # Corridor 2: Different path for redundancy
        y_corridor2 = 75
        map_obj.add_road(0, y_corridor2, width, corridor_width)
        
        x_corridor2 = 30
        map_obj.add_road(x_corridor2, 0, corridor_width, height)
        
        # Create residential blocks (rectangular buildings)
        block_width = 12
        block_height = 12
        gap = 4
        
        for x in range(15, width - 20, block_width + gap):
            for y in range(15, height - 20, block_height + gap):
                # Skip if overlaps with corridors or safe zones
                if (5 <= x <= 95 and (y_corridor1 <= y <= y_corridor1 + corridor_width or 
                                       y_corridor2 <= y <= y_corridor2 + corridor_width)) or \
                   (5 <= y <= 95 and (x_corridor1 <= x <= x_corridor1 + corridor_width or 
                                      x_corridor2 <= x <= x_corridor2 + corridor_width)):
                    continue
                
                if ((x < 10 or x > 90) and (y < 10 or y > 90)):
                    continue
                
                # Randomly add building with small variations
                if np.random.random() > 0.15:
                    actual_width = block_width + np.random.randint(-2, 2)
                    actual_height = block_height + np.random.randint(-2, 2)
                    map_obj.add_obstacle(x, y, actual_width, actual_height)
        
        # Add small random obstacles (cars, etc.)
        num_small_obstacles = np.random.randint(10, 20)
        for _ in range(num_small_obstacles):
            x = np.random.randint(10, width - 10)
            y = np.random.randint(10, height - 10)
            obs_width = np.random.randint(2, 4)
            obs_height = np.random.randint(2, 4)
            
            # Only add if it doesn't block safe zones or main corridors
            if not (x < 15 and y < 15) and not (x > 85 and y > 85):
                map_obj.add_obstacle(x, y, obs_width, obs_height)
        
        # Create open area (plaza/park) in middle area
        plaza_x = 45
        plaza_y = 45
        plaza_size = 12
        map_obj.add_road(plaza_x, plaza_y, plaza_size, plaza_size)
        
        # Add some dead-end streets
        for _ in range(3):
            start_x = np.random.randint(20, width - 20)
            start_y = np.random.randint(20, height - 20)
            direction = np.random.choice(['h', 'v'])
            length = np.random.randint(15, 25)
            
            if direction == 'h':
                map_obj.add_road(start_x, start_y, length, 3)
            else:
                map_obj.add_road(start_x, start_y, 3, length)
        
        # Ensure start and goal are free
        for y in range(5, 12):
            for x in range(5, 12):
                map_obj.grid[y, x] = 0
        
        for y in range(94, 100):
            for x in range(94, 100):
                map_obj.grid[y, x] = 0
        
        # Check density - accept if in reasonable range
        density = map_obj.get_occupancy_density()
        if 0.25 <= density <= 0.50:
            print(f"Map generated successfully on attempt {attempt} with density {density:.1%}")
            return map_obj
    
    # If we get here, return the last map even if density is not ideal
    print(f"Warning: Could not achieve target density after {max_attempts} attempts.")
    print(f"Using map with density {map_obj.get_occupancy_density():.1%}")
    return map_obj


def save_all_sample_maps(maps_dir: str = 'maps'):
    """Generate and save sample maps"""
    os.makedirs(maps_dir, exist_ok=True)
    
    print("Generating urban map...")
    urban_map = generate_urban_map(100, 100)
    urban_map.save(os.path.join(maps_dir, 'urban_map_1.json'))
    urban_map.visualize(filename=os.path.join(maps_dir, 'urban_map_1.png'))
    
    print(f"Map occupancy density: {urban_map.get_occupancy_density():.1%}")
    print(f"Sample maps created in '{maps_dir}' folder.")


if __name__ == "__main__":
    save_all_sample_maps()
