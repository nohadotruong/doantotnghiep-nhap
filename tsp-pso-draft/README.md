# TSP-PSO: Traveling Salesman Problem Solver using Particle Swarm Optimization

## 📋 Overview

This project implements a solver for the **Traveling Salesman Problem (TSP)** using **Particle Swarm Optimization (PSO)**, a nature-inspired metaheuristic algorithm. It's suitable for combinatorial optimization problems where finding the shortest route visiting all cities exactly once is required.

## 🎯 Bài Toán

**Traveling Salesman Problem (TSP):**
- Cho n thành phố với tọa độ [x, y] xác định
- Tìm một hành trình đi qua tất cả các thành phố đúng một lần và quay lại thành phố ban đầu
- Tối thiểu hóa tổng khoảng cách của hành trình

**Particle Swarm Optimization (PSO):**
- Thuật toán được lấy cảm hứng từ hành vi của bầy chim hoặc đàn cá
- Mỗi "hạt" (particle) đại diện cho một giải pháp tiềm năng
- Các hạt di chuyển trong không gian tìm kiếm dựa trên:
  - Vị trí tốt nhất của chúng (cognitive - nhận thức)
  - Vị trí tốt nhất toàn bộ bầy (social - xã hội)
  - Quán tính (inertia weight)

## 📁 Project Structure

```
tsp-pso/
├── tsp_pso.py          # Core PSO-TSP implementation
├── examples.py         # Advanced examples and utilities
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from tsp_pso import TSPProblem, PSO, generate_cities, plot_solution, plot_convergence

# 1. Generate random cities
cities = generate_cities(n_cities=20, seed=42)

# 2. Create TSP problem
problem = TSPProblem(cities)

# 3. Solve with PSO
pso = PSO(problem, n_particles=30, max_iterations=500)
best_tour, best_distance, history = pso.solve()

# 4. Visualize results
plot_solution(problem, best_tour)
plot_convergence(history)

print(f"Best tour: {best_tour}")
print(f"Best distance: {best_distance:.2f}")
```

### Run Examples

```bash
# Run main example
python tsp_pso.py

# Run advanced examples
python examples.py
```

## 📚 API Reference

### Core Classes

#### `TSPProblem`
Manages the TSP problem instance.

```python
problem = TSPProblem(cities: np.ndarray)
```

**Methods:**
- `calculate_tour_distance(tour: List[int]) -> float`: Tính tổng khoảng cách của một hành trình
- `distance_matrix`: Tính ma trận khoảng cách Euclid giữa các thành phố

#### `Particle`
Represents a single particle in the swarm.

**Attributes:**
- `position`: Current tour (permutation of city indices)
- `velocity`: PSO velocity for position updates
- `best_position`: Best tour found by this particle
- `best_distance`: Distance of the best tour

**Methods:**
- `update_velocity(global_best, w, c1, c2)`: Cập nhật vận tốc dựa trên công thức PSO
- `update_position(problem)`: Cập nhật vị trí và quản lý 2-opt moves

#### `PSO`
Main PSO solver for TSP.

```python
pso = PSO(
    problem: TSPProblem,
    n_particles: int = 30,        # Số lượng hạt
    max_iterations: int = 500,    # Số lần lặp tối đa
    w: float = 0.7,               # Trọng số quán tính
    c1: float = 1.5,              # Tham số nhận thức
    c2: float = 1.5               # Tham số xã hội
)
```

**Methods:**
- `solve() -> Tuple[List[int], float, List[float]]`: Giải TSP, trả về (tốt nhất_tour, khoảng cách, lịch_sử)

### Utility Functions

```python
# Generate random cities
cities = generate_cities(n_cities: int, seed: int = None) -> np.ndarray

# Plot TSP solution
plot_solution(problem: TSPProblem, tour: List[int], title: str = "TSP Solution")

# Plot convergence curve
plot_convergence(distance_history: List[float])
```

## 🔧 Advanced Usage

### Example 1: Multiple Trials with Statistics

```python
from examples import run_multiple_trials

stats = run_multiple_trials(n_cities=20, n_trials=5, n_particles=30)
print(f"Mean distance: {stats['mean_distance']:.2f}")
print(f"Std deviation: {stats['std_distance']:.2f}")
```

### Example 2: Parameter Comparison

```python
from examples import compare_parameters

results = compare_parameters(
    n_cities=15, 
    n_particles_list=[10, 20, 30, 40]
)
```

### Example 3: Custom Cities File

```python
from examples import solve_custom_cities

# From JSON file
best_tour, best_distance = solve_custom_cities('cities.json')

# Auto-generate example file
best_tour, best_distance = solve_custom_cities()
```

## 📊 Parameters Explanation

| Parameter | Default | Mô tả |
|-----------|---------|-------|
| `n_particles` | 30 | Số hạt trong bầy - nhiều hạt = khám phá rộng hơn nhưng chậm hơn |
| `max_iterations` | 500 | Số lần lặp - nhiều lần = khả năng tối ưu hơn nhưng chậm hơn |
| `w` (inertia weight) | 0.7 | Trọng số quán tính - cao = khám phá, thấp = khai thác |
| `c1` (cognitive) | 1.5 | Hệ số nhận thức - ảnh hưởng đến sự thu hút vào giải pháp tốt nhất cá nhân |
| `c2` (social) | 1.5 | Hệ số xã hội - ảnh hưởng đến sự thu hút vào giải pháp tốt nhất toàn cầu |

## 💡 Tips for Better Results

1. **Tăng số hạt**: Nhiều hạt giúp khám phá không gian tìm kiếm tốt hơn
   ```python
   pso = PSO(problem, n_particles=50)
   ```

2. **Tăng số lần lặp**: Cho phép hội tụ tốt hơn
   ```python
   pso = PSO(problem, max_iterations=1000)
   ```

3. **Điều chỉnh w (inertia weight)**:
   - Bắt đầu cao (0.9) để khám phá, sau đó giảm (0.4) để khai thác
   - Hiện tại code sử dụng: `w *= 0.99` (giảm tự động)

4. **Chạy nhiều lần**: So sánh kết quả để có giải pháp tốt nhất
   ```python
   stats = run_multiple_trials(n_cities=20, n_trials=10)
   ```

5. **Điều chỉnh c1 và c2**: Thường c1 ≈ c2 ≈ 2
   ```python
   pso = PSO(problem, c1=2.0, c2=2.0)
   ```

## 📈 Algorithm Details

### PSO Update Equations

**Velocity Update:**
```
v(t+1) = w*v(t) + c1*r1*(pbest - x(t)) + c2*r2*(gbest - x(t))
```

**Position Update:**
- Sử dụng 2-opt moves (đảo ngược một phần của tour)
- Xác suất swaps dựa trên velocity values

### Convergence

Thuật toán hội tụ khi:
- Tất cả hạt hội tụ vào vùng giải pháp tốt nhất
- Không còn cải thiện sau nhiều lần lặp
- Hoặc đạt tối đa số lần lặp được đặt

## 🧪 Testing

```bash
# Run with 20 cities
python tsp_pso.py

# Run advanced examples
python examples.py

# Run with custom parameters
python -c "
from tsp_pso import *
cities = generate_cities(15)
problem = TSPProblem(cities)
pso = PSO(problem, n_particles=50, max_iterations=1000)
tour, dist, hist = pso.solve()
print(f'Distance: {dist:.2f}')
plot_convergence(hist)
"
```

## 📖 References

- Kennedy & Eberhart (1995): Particle Swarm Optimization
- Dorigo & Stützle: Ant Colony Optimization for TSP
- Various TSP benchmark datasets

## 🐛 Troubleshooting

**Problem**: Solver không hội tụ tốt
**Giải pháp**: 
- Tăng `n_particles` (30 → 50)
- Tăng `max_iterations` (500 → 1000)
- Chạy nhiều lần và lấy kết quả tốt nhất

**Problem**: Quá chậm
**Giải pháp**:
- Giảm `n_cities` (test với 10-15 thành phố trước)
- Giảm `max_iterations` (nhưng có thể ảnh hưởng đến chất lượng)
- Giảm `n_particles` (nhưng giảm khả năng khám phá)

## 📝 License

Free to use for educational and research purposes.

## 👥 Author

TSP-PSO Implementation - 2024

---

**Lưu ý**: Mã này được tối ưu hóa cho hiệu quả giáo dục. Để sử dụng trong sản xuất, cân nhắc:
- Sử dụng các thư viện tối ưu hóa như Scipy
- Cách tiếp cận khác như ACO, GA
- Tăng kích thước bộ nhớ cache cho ma trận khoảng cách
- Parallelization cho các hạt độc lập
