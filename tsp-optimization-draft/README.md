## UAV Multi-Point Path Optimization

**Đề tài:** Tối ưu hóa đường bay đa điểm cho UAV trong môi trường có chướng ngại vật

**Project:** Multi-point Path Optimization for UAV in Obstacle Environment

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Usage Examples](#usage-examples)
6. [Algorithms](#algorithms)
7. [Results](#results)
8. [API Reference](#api-reference)

---

## 🎯 Introduction

This project implements a complete solution for multi-point path optimization for Unmanned Aerial Vehicles (UAVs) in environments with obstacles. The system combines:

- **RRT\* Algorithm**: For finding collision-free paths between waypoints
- **PSO (Particle Swarm Optimization)**: For optimizing the order of waypoints visits
- **2-Opt Improvement**: For local optimization of the tour

### Key Features:

- ✅ Realistic obstacle modeling (circular and rectangular)
- ✅ Collision-free path planning using RRT\*
- ✅ Multi-point ordering optimization with PSO
- ✅ Hybrid optimization approach combining PSO + 2-Opt
- ✅ Comprehensive visualization
- ✅ Performance metrics and comparison analysis
- ✅ Scalability testing

---

## 📁 Project Structure

```
tsp-optimization-draft/
├── src/
│   ├── environment/
│   │   ├── __init__.py
│   │   └── obstacles.py          # Obstacle definitions and environment
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── rrt_star.py           # RRT* path planning algorithm
│   │   ├── pso.py                # PSO and TSP solver
│   │   └── multipoint_planner.py # Multi-point path planner
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── base.py               # Utilities and metrics
│   │   └── visualization.py      # Visualization functions
│   └── __init__.py
├── results/                       # Results and visualizations
├── demo.py                        # Simple demonstration examples
├── main_comparison.py             # Comprehensive comparison study
└── README.md                      # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Step 1: Set up Virtual Environment

```bash
cd d:\DEV\_Projects\TLU\DoAn\tsp-optimization-draft
python -m venv venv
venv\Scripts\activate  # On Windows
```

### Step 2: Install Dependencies

```bash
pip install numpy matplotlib scipy
```

### Step 3: Verify Installation

```bash
python -c "import numpy as np; import matplotlib; print('✓ Dependencies installed successfully')"
```

---

## ⚡ Quick Start

### Run the Demo

```bash
python demo.py
```

This will run three demonstrations:

1. **Simple multi-point path planning**
2. **Comparison of different optimization methods**
3. **Complex obstacle avoidance scenario**

Results are saved to the `results/` directory.

### Run Full Comparison Study

```bash
python main_comparison.py
```

This will:

- Test on multiple environments (simple, complex)
- Compare all optimization methods
- Run scalability tests
- Save detailed results to JSON files
- Generate comparison visualizations

---

## 📖 Usage Examples

### Example 1: Basic Path Planning

```python
import numpy as np
from src.environment import Environment
from src.algorithms import MultiPointPlanner
from src.utils import PerformanceMetrics

# Create environment
env = Environment(bounds=(0, 100, 0, 100))
env.add_circle_obstacle([30, 30], radius=8)
env.add_circle_obstacle([70, 70], radius=8)

# Define waypoints
start = np.array([5, 5])
goal = np.array([95, 95])
waypoints = [
    np.array([30, 70]),
    np.array([60, 30]),
    np.array([70, 60]),
]

# Plan path
planner = MultiPointPlanner(env)
path, cost, info = planner.plan(
    start, waypoints, goal,
    optimizer='combined',  # Use PSO + 2-Opt
    rrt_iterations=3000
)

print(f"Path cost: {cost:.4f}")
print(f"Path smoothness: {PerformanceMetrics.path_smoothness(path):.4f}")
```

### Example 2: Visualization

```python
from src.utils import PathVisualizer

visualizer = PathVisualizer()
visualizer.plot(env, path, waypoints,
               title="My Path Planning Result",
               save_path="results/my_result.png")
```

### Example 3: Compare Methods

```python
methods = ['greedy', 'pso', '2opt', 'combined']
results = {}

for method in methods:
    path, cost, info = planner.plan(
        start, waypoints, goal,
        optimizer=method
    )
    results[method] = {'cost': cost, 'path': path}

# Visualize comparison
visualizer.compare_paths(env, {m: r['path'] for m, r in results.items()},
                        waypoints)
```

### Example 4: Direct Environment Creation

```python
# Simple environment with few obstacles
from src.utils import create_test_environment

env, start, goal, waypoints = create_test_environment("simple")

# Complex environment with many obstacles
env, start, goal, waypoints = create_test_environment("complex")

# Narrow passages
env, start, goal, waypoints = create_test_environment("narrow")
```

---

## 🧮 Algorithms

### 1. RRT* (Rapidly-exploring Random Tree*)

**Location**: `src/algorithms/rrt_star.py`

- Asymptotically optimal motion planning algorithm
- Generates random samples and builds a tree of collision-free paths
- Includes rewiring mechanism to improve path quality
- Parameters:
  - `step_size`: Distance for each expansion step (default: 0.5)
  - `max_iter`: Maximum iterations (default: 5000)
  - `search_radius`: Radius for rewiring neighbors (default: 2.0)

**Usage**:

```python
from src.algorithms import RRTStar

rrt = RRTStar(environment, max_iter=5000, step_size=0.5)
path = rrt.plan(start_position, goal_position)
```

### 2. PSO (Particle Swarm Optimization)

**Location**: `src/algorithms/pso.py`

- Swarm-based optimization for discrete problems
- Minimizes tour cost through particle movement
- Uses order-based representation for TSP
- Parameters:
  - `num_particles`: Number of particles (default: 30)
  - `max_iterations`: Maximum iterations (default: 100)
  - `w`: Inertia weight (default: 0.7)
  - `c1`, `c2`: Cognitive and social parameters (default: 1.5 each)

**Usage**:

```python
from src.algorithms import TSPSolver

tsp_solver = TSPSolver(waypoints, distance_matrix)
best_order, best_cost = tsp_solver.solve_pso()
```

### 3. Multi-Point Planner

**Location**: `src/algorithms/multipoint_planner.py`

- Combines RRT\* and PSO for multi-point optimization
- Supports multiple optimization strategies:
  - `'greedy'`: Nearest neighbor
  - `'pso'`: Particle Swarm Optimization
  - `'2opt'`: 2-Opt local search
  - `'combined'`: PSO followed by 2-Opt (PROPOSED METHOD)

**Usage**:

```python
from src.algorithms import MultiPointPlanner

planner = MultiPointPlanner(environment)
path, cost, info = planner.plan(start, waypoints, goal,
                               optimizer='combined',
                               rrt_iterations=3000)
```

---

## 📊 Results and Metrics

### Available Metrics

The `PerformanceMetrics` class provides:

1. **Path Length**: Total distance traveled
2. **Path Smoothness**: Measure of curvature (based on angle changes)
3. **Computation Time**: Algorithm execution time
4. **Path Quality**: Optimization cost value

### Accessing Results

```python
from src.utils import PerformanceMetrics

# Calculate metrics
length = PerformanceMetrics.path_length(path)
smoothness = PerformanceMetrics.path_smoothness(path)
improvement = PerformanceMetrics.improvement_percentage(original, improved)

# Comprehensive metrics
metrics = PerformanceMetrics.compute_all_metrics(path, waypoints, cost)
```

### Saving Results

```python
from src.utils import ResultsRecorder

recorder = ResultsRecorder(save_dir="results")
key = recorder.record_result("my_experiment", result_data)
recorder.save_results(key, filename_prefix="experiment")
```

---

## 📈 Expected Results

Based on the thesis objectives, expected improvements include:

**Cost Reduction**:

- Greedy: Baseline performance
- PSO: 10-25% improvement over greedy
- PSO + 2-Opt: 15-35% improvement over greedy

**Path Quality**:

- Better waypoint ordering reduces total distance
- RRT\* ensures collision-free paths
- 2-Opt improves local path segments

**Computation Time**:

- Greedy: O(n²) - fastest
- PSO: O(n² × iterations) - moderate
- 2-Opt: O(n³) - variable
- Combined: Reasonable trade-off

---

## 🔧 Configuration and Customization

### Customizing Environment

```python
# Create custom environment
from src.environment import Environment

env = Environment(bounds=(0, 200, 0, 200))  # Change bounds

# Add various obstacles
env.add_circle_obstacle([50, 50], radius=15)
env.add_rectangle_obstacle(100, 150, 80, 120)

# Set clearance requirement
clearance = 2.0  # UAV must maintain distance from obstacles
is_safe = env.is_collision_free(position, clearance=clearance)
```

### Customizing Planner Parameters

```python
planner = MultiPointPlanner(env, cache_paths=True)

# Modify RRT* settings
planner.rrt_star.max_iter = 10000
planner.rrt_star.step_size = 1.0
planner.rrt_star.search_radius = 3.0
```

### Customizing PSO Parameters

```python
from src.algorithms import PSO

pso = PSO(
    num_particles=50,        # More particles = better exploration
    max_iterations=200,      # More iterations = better convergence
    w=0.7,                  # Inertia weight
    c1=1.5,                 # Cognitive coefficient
    c2=1.5                  # Social coefficient
)
```

---

## 🎓 Key Concepts

### Traveling Salesman Problem (TSP)

The multi-point path optimization problem is a variant of TSP where:

- We must visit multiple points (waypoints) in optimal order
- Movement is constrained by obstacles
- Real distance (RRT\*) is used instead of Euclidean distance

### Path Smoothness

A smoother path:

- Requires less control effort for the UAV
- Is more realistic for physical systems
- Reduces energy consumption

Smoothness is measured by total curvature (sum of angle changes).

### Asymptotic Optimality

RRT\* guarantees that as iterations increase, the found path approaches optimal, while always remaining collision-free.

---

## 📝 Thesis Contributions

This implementation addresses the thesis objectives:

### ✅ Objective 1: Environment Modeling

- Implemented flexible obstacle representation
- Support for circular and rectangular obstacles
- Collision detection and clearance checking

### ✅ Objective 2: Optimization Methods

- RRT\* for collision-free path segments
- PSO for waypoint ordering
- Hybrid approach combining both

### ✅ Objective 3: Comparison and Evaluation

- Multiple test environments (simple, complex, narrow)
- Comparison with traditional methods (greedy, 2-opt)
- Comprehensive performance metrics
- Scalability analysis

---

## 🐛 Troubleshooting

### Problem: "No path found"

**Solution**:

- Increase `rrt_iterations` in planner
- Reduce `step_size` for finer exploration
- Check if waypoints are in collision-free areas

### Problem: Slow execution

**Solution**:

- Reduce `max_iterations` in PSO
- Use smaller `rrt_iterations` (2000-3000 instead of 5000)
- Reduce number of waypoints for testing

### Problem: Visualization not working

**Solution**:

- Ensure matplotlib is installed: `pip install matplotlib`
- Check that save path is valid
- Try using `PathVisualizer.show()` instead of saving

---

## 📚 References

### Key Papers

1. **RRT\* Algorithm**:
   - Karaman, S., & Frazzoli, E. (2011). "Sampling-based Algorithms for Optimal Motion Planning"

2. **Particle Swarm Optimization**:
   - Kennedy, J., & Eberhart, R. (1995). "Particle Swarm Optimization"

3. **2-Opt for TSP**:
   - Croes, G. A. (1958). "A Method for Solving Traveling Salesman Problems"

### Related Work

- Motion planning for UAVs in cluttered environments
- Hybrid approaches combining sampling-based and optimization methods
- Real-time path planning algorithms

---

## 📄 License and Usage

This project is developed for educational and research purposes as part of a thesis.

---

## 👨‍💻 Author Notes

### For Thesis Writing

Key sections to include:

1. **Literature Review**: RRT\*, PSO, TSP, motion planning
2. **Problem Formulation**: Mathematical model of constraints
3. **Proposed Method**: Details of RRT\* + PSO combination
4. **Implementation**: Architecture and key algorithms
5. **Experiments**: Test scenarios and results
6. **Analysis**: Performance comparison and discussion
7. **Conclusion**: Effectiveness of proposed approach

### Key Figures for Thesis

Generate using visualization functions:

- Path planning comparison plots
- Cost comparison bar charts
- Scalability graphs
- RRT\* tree structure visualization
- Obstacle avoidance demonstrations

---

## ✨ Future Enhancements

Possible extensions:

1. **3D Path Planning**: Extend to 3D environments
2. **Dynamic Obstacles**: Handle moving obstacles
3. **Real-time Planning**: Replanning for online scenarios
4. **Energy Optimization**: Include fuel/battery constraints
5. **Time Windows**: Add time constraints for waypoint visits
6. **Uncertainty Handling**: Robust planning under uncertainty
7. **GPU Acceleration**: Speed up computation on large problems

---

**For questions or issues, review the code comments and docstrings in each module.**

Good luck with your thesis! 🚀
