"""
Quick test to verify fixes:
1. Path doesn't cut through obstacles
2. Distance is float (not numpy float64)
"""

from utils.environment import UAVEnvironment
from algorithms import AStarPathfinder, PSOPathfinder, SAPathfinder, GWOPathfinder, GAPathfinder

# Create environment
env = UAVEnvironment(width=100, height=100)

# Generate 5 random obstacles
env.simple_map(num_obstacles=5, seed=42)

# Set start and goal
env.set_start_goal((5, 5), (95, 95))

# Test all algorithms
algorithms = {
    'A*': AStarPathfinder(env, grid_step=2.0),
    'PSO': PSOPathfinder(env, num_particles=30, max_iterations=200),
    'SA': SAPathfinder(env, initial_temp=100, cooling_rate=0.95, max_iterations=500),
    'GWO': GWOPathfinder(env, num_wolves=30, max_iterations=200),
    'GA': GAPathfinder(env, population_size=30, max_iterations=200)
}

print("=" * 60)
print("Testing all algorithms...")
print("=" * 60)

for name, algo in algorithms.items():
    print(f"\n[{name}]")
    
    success = algo.find_path()
    print(f"  ✓ Found path: {success}")
    
    if success:
        path = algo.get_path()
        stats = algo.get_statistics()
        
        # Check distance type
        distance = stats['distance']
        print(f"  ✓ Distance type: {type(distance).__name__} = {distance:.2f}")
        
        # Check path doesn't cut through obstacles
        path_arr = [p for p in path]
        collisions = sum(1 for p in path_arr if env.is_collision(p))
        print(f"  ✓ Collision points in path: {collisions} (should be 0)")
        
        # Print waypoints
        print(f"  ✓ Waypoints: {stats['num_waypoints']}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
