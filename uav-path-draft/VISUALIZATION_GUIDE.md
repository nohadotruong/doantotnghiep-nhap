# Detailed Algorithm Visualization Guide

## Overview
This project now includes **detailed step-by-step visualization** of how each pathfinding algorithm works. Instead of only showing the final path, you can now see how the algorithm explores the space at each iteration.

## Features

### 1. Algorithm Progress Visualization
Shows multiple snapshots of an algorithm's execution, revealing:
- **PSO (Particle Swarm)**: Particles moving toward the goal, with personal best and global best positions
- **A* (A-Star)**: Explored nodes (closed set) and frontier nodes (open set)
- **SA (Simulated Annealing)**: Current solution and temperature changes
- **GWO (Grey Wolf Optimizer)**: Wolf pack hierarchy (Alpha/Beta/Delta) hunting the goal
- **GA (Genetic Algorithm)**: Population evolution and best individual tracking

### 2. Execution Methods

#### Method 1: Quick Start
Run the simplified visualization script:
```bash
python quickstart_visualization.py
```
This shows a basic example of PSO progress with 5 snapshots.

#### Method 2: Main Program with Interactive Selection
Run the enhanced main.py:
```bash
python main.py
```
After running all algorithms, it prompts you to choose which algorithm to visualize in detail.

#### Method 3: Full Examples (Recommended)
Run the comprehensive examples showing all algorithms:
```bash
python examples_detailed.py
```

This includes:
- **Example 1**: Individual algorithm progress (each algorithm separately)
- **Example 2**: Side-by-side comparison of all algorithms at different iterations
- **Example 3**: Detailed PSO learning with analysis at key iterations
- **Example 4**: Convergence analysis showing how quickly each algorithm improves

## Understanding the Visualizations

### PSO Visualization
```
Cyan circles    = Current particle positions
Light green ▲   = Personal best positions of each particle
Yellow ★        = Global best position (best solution found by entire swarm)
Blue arrows     = Velocity vectors (showing particle movement direction)
```
**What to observe:**
- Particles should gradually spread toward the goal (yellow circle)
- Global best (yellow ★) should move closer to the goal over iterations
- Particles should converge around global best in later iterations

### A* Visualization
```
Light pink •    = Explored nodes (closed set)
Yellow •        = Frontier nodes to be explored (open set)
Green dashed    = Current path from start toward goal
```
**What to observe:**
- Explored nodes should expand outward from start
- Algorithm should avoid obstacles (red areas)
- Frontier should gradually reach toward the goal

### SA Visualization
```
Red line        = Current solution candidate
Green line      = Best solution found so far
(Background color intensity indicates temperature)
```
**What to observe:**
- Temperature should decrease over iterations (shown in text box)
- Solution should avoid getting stuck in local optima at high temperature
- As temperature decreases, solutions should improve and converge

### GWO Visualization
```
Light blue •    = Omega wolves (rest of pack)
Orange ◇        = Delta wolf (third best)
Purple ■        = Beta wolf (second best)
Red ★           = Alpha wolf (best solution/leader)
Red dashed ---  = Best wolves' positions
```
**What to observe:**
- Alpha wolf should move toward the goal
- Pack should follow wolf hierarchy
- All wolves should eventually gather around goal

### GA Visualization
```
Cyan lines      = All individuals in population
Green ●         = Best individual (best path found)
```
**What to observe:**
- Population should initially be scattered
- Best individual (green) should improve over generations
- Other individuals should cluster around best solution

## Key Insights

### PSO
- **Strength**: Good at broad exploration, converges to good solutions
- **Visualization shows**: Swarm behavior, particles learning from each other
- **Key phase**: Watch particles accelerate toward global best

### A*
- **Strength**: Systematic exploration using heuristics, guarantees optimal path
- **Visualization shows**: Methodical search expansion, exploration pattern
- **Key phase**: Watch frontier grow and adapt around obstacles

### SA
- **Strength**: Can escape local optima at high temperature, refines at low temperature
- **Visualization shows**: Temperature-controlled acceptance of worse solutions
- **Key phase**: Watch transition from broad search to fine-tuning

### GWO
- **Strength**: Hierarchical search combining exploitation and exploration
- **Visualization shows**: Pack hunting behavior, three-tier decision making
- **Key phase**: Watch alpha lead until convergence near goal

### GA
- **Strength**: Population-based evolution, maintains diversity
- **Visualization shows**: Selection, crossover, and mutation effects
- **Key phase**: Watch population converge while maintaining diversity

## Customization

### Adjust Number of Snapshots
In any visualization function, change `num_snapshots` parameter:
```python
fig = visualize_algorithm_progress(env, algorithm, "PSO", num_snapshots=8)  # Show 8 snapshots instead of 5
```

### Track Custom Iteration Counts
Modify algorithm parameters to see different phases:
```python
# PSO with fewer iterations to see early exploration
pso = PSOPathfinder(env, num_particles=30, max_iterations=50)

# SA with higher initial temperature for longer broad search
sa = SAPathfinder(env, initial_temp=500, cooling_rate=0.90, max_iterations=1000)

# GA with larger population
ga = GAPathfinder(env, population_size=50, max_iterations=200)
```

### Enable Tracking Manually
```python
algorithm = PSOPathfinder(env)
algorithm.track_history = True  # Enable tracking
algorithm.find_path()

# Now you can access: algorithm.position_history
# Each entry contains a snapshot of the algorithm state
```

## Files Reference

| File | Purpose |
|------|---------|
| `utils/visualize_progress.py` | Core visualization functions |
| `examples_detailed.py` | Complete examples (4 examples total) |
| `quickstart_visualization.py` | Simple PSO visualization |
| `main.py` | Enhanced main program with detail visualization option |
| `algorithms/*.py` | Modified algorithms with history tracking |

## Performance Notes

- Tracking history has minimal performance impact (< 5% overhead)
- Visualization generation is separate from pathfinding
- Disable tracking if you only care about final results:
  ```python
  algorithm.track_history = False  # (default)
  ```

## Troubleshooting

**Q: Visualization shows no snapshots?**
- Ensure `track_history = True` is set before calling `find_path()`
- Check that algorithm has valid environment and obstacles

**Q: Matplotlib window doesn't appear?**
- Make sure you have a display (X11 forwarding if on WSL)
- Try: `plt.show()` after creating figures

**Q: PSO particles are stuck in obstacles?**
- This is normal - they represent candidate solutions being evaluated
- Final path is constructed safely avoiding obstacles

## Learning Path

**Beginner**: Run `quickstart_visualization.py` to see basic PSO visualization

**Intermediate**: Run `python main.py` and select different algorithms to compare

**Advanced**: Run `python examples_detailed.py` to see all examples including convergence analysis

---

**Happy learning! Enjoy watching your algorithms find paths! 🚀**
