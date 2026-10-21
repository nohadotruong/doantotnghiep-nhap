"""
multiple_runs.py - Chạy thuật toán nhiều lần để tìm kết quả tối ưu nhất
"""
import numpy as np
from typing import List, Tuple, Dict, Any
from generate_map import Map2D
from evaluate import PathEvaluator
import time


class MultipleRunsOptimizer:
    """Chạy thuật toán nhiều lần và chọn kết quả tốt nhất"""
    
    def __init__(self, map_obj: Map2D, num_runs: int = 10):
        """
        Args:
            map_obj: Bản đồ
            num_runs: Số lần chạy mỗi thuật toán
        """
        self.map = map_obj
        self.num_runs = num_runs
        self.evaluator = PathEvaluator(map_obj)
    
    def run_algorithm_multiple_times(self, algorithm_class, algorithm_name: str, 
                                     **algorithm_params) -> Dict[str, Any]:
        """
        Chạy một thuật toán nhiều lần và chọn kết quả tốt nhất
        
        Args:
            algorithm_class: Class của thuật toán (AStar, RRTStar, PSO, etc.)
            algorithm_name: Tên thuật toán
            **algorithm_params: Tham số cho thuật toán
            
        Returns:
            Dictionary chứa best_path, best_metrics, all_runs_stats
        """
        print(f"\n{'='*70}")
        print(f"Chạy {algorithm_name} {self.num_runs} lần để tìm kết quả tối ưu...")
        print(f"{'='*70}")
        
        all_paths = []
        all_metrics = []
        all_computation_times = []
        successful_runs = 0
        
        for run_idx in range(self.num_runs):
            print(f"  Lần {run_idx + 1}/{self.num_runs}...", end=' ')
            
            try:
                # Khởi tạo và chạy thuật toán
                algorithm = algorithm_class(self.map, **algorithm_params)
                path = algorithm.find_path()
                computation_time = algorithm.computation_time
                
                if path is not None and len(path) > 0:
                    # Đánh giá
                    metrics = self.evaluator.evaluate(path, computation_time, algorithm_name)
                    
                    all_paths.append(path)
                    all_metrics.append(metrics)
                    all_computation_times.append(computation_time)
                    successful_runs += 1
                    
                    print(f"✓ Độ dài: {metrics['path_length']:.2f}m, "
                          f"Thời gian: {computation_time:.4f}s")
                else:
                    print("✗ Không tìm thấy đường")
                    
            except Exception as e:
                print(f"✗ Lỗi: {str(e)}")
        
        # Tổng hợp kết quả
        if successful_runs == 0:
            print(f"\n✗ {algorithm_name} không tìm thấy đường trong tất cả {self.num_runs} lần chạy!")
            return {
                'algorithm': algorithm_name,
                'successful_runs': 0,
                'total_runs': self.num_runs,
                'best_path': None,
                'best_metrics': None,
                'statistics': None
            }
        
        # Tìm run tốt nhất (path ngắn nhất và không có collision)
        best_idx = self._find_best_run(all_metrics)
        best_path = all_paths[best_idx]
        best_metrics = all_metrics[best_idx]
        
        # Tính thống kê
        statistics = self._calculate_statistics(all_metrics, all_computation_times)
        
        # In kết quả
        print(f"\n{'='*70}")
        print(f"KẾT QUẢ {algorithm_name}:")
        print(f"  - Tỷ lệ thành công: {successful_runs}/{self.num_runs} "
              f"({100*successful_runs/self.num_runs:.1f}%)")
        print(f"  - Best run (#{best_idx + 1}):")
        print(f"    + Độ dài: {best_metrics['path_length']:.2f}m")
        print(f"    + Thời gian: {best_metrics['computation_time']:.4f}s")
        print(f"  - Thống kê {successful_runs} lần chạy thành công:")
        print(f"    + Độ dài TB: {statistics['path_length_mean']:.2f}m "
              f"± {statistics['path_length_std']:.2f}m")
        print(f"    + Độ dài min/max: {statistics['path_length_min']:.2f}m / "
              f"{statistics['path_length_max']:.2f}m")
        print(f"    + Thời gian TB: {statistics['computation_time_mean']:.4f}s "
              f"± {statistics['computation_time_std']:.4f}s")
        print(f"{'='*70}")
        
        return {
            'algorithm': algorithm_name,
            'successful_runs': successful_runs,
            'total_runs': self.num_runs,
            'success_rate': successful_runs / self.num_runs,
            'best_path': best_path,
            'best_metrics': best_metrics,
            'all_metrics': all_metrics,
            'statistics': statistics
        }
    
    def _find_best_run(self, all_metrics: List[Dict]) -> int:
        """
        Tìm run tốt nhất dựa trên:
        1. Không có collision (ưu tiên cao nhất)
        2. Độ dài đường đi ngắn nhất
        """
        # Tách runs thành có/không collision
        valid_runs = []
        collision_runs = []
        
        for idx, metrics in enumerate(all_metrics):
            if metrics['num_collisions'] == 0:
                valid_runs.append((idx, metrics['path_length']))
            else:
                collision_runs.append((idx, metrics['path_length']))
        
        # Ưu tiên chọn run không có collision
        if valid_runs:
            # Chọn run có độ dài ngắn nhất trong các run hợp lệ
            best_idx = min(valid_runs, key=lambda x: x[1])[0]
        else:
            # Nếu tất cả đều có collision, chọn run có ít collision nhất
            # và độ dài ngắn nhất
            best_idx = min(range(len(all_metrics)), 
                          key=lambda i: (all_metrics[i]['num_collisions'], 
                                        all_metrics[i]['path_length']))
        
        return best_idx
    
    def _calculate_statistics(self, all_metrics: List[Dict], 
                             all_times: List[float]) -> Dict[str, float]:
        """Tính các thống kê từ nhiều lần chạy"""
        path_lengths = [m['path_length'] for m in all_metrics]
        smoothness = [m['smoothness'] for m in all_metrics]
        optimality_ratios = [m['optimality_ratio'] for m in all_metrics]
        collisions = [m['num_collisions'] for m in all_metrics]
        
        return {
            'path_length_mean': np.mean(path_lengths),
            'path_length_std': np.std(path_lengths),
            'path_length_min': np.min(path_lengths),
            'path_length_max': np.max(path_lengths),
            'path_length_median': np.median(path_lengths),
            
            'computation_time_mean': np.mean(all_times),
            'computation_time_std': np.std(all_times),
            'computation_time_min': np.min(all_times),
            'computation_time_max': np.max(all_times),
            
            'smoothness_mean': np.mean(smoothness),
            'smoothness_std': np.std(smoothness),
            
            'optimality_ratio_mean': np.mean(optimality_ratios),
            'optimality_ratio_std': np.std(optimality_ratios),
            
            'collision_rate': sum(1 for c in collisions if c > 0) / len(collisions),
            'avg_collisions': np.mean(collisions)
        }


def run_all_algorithms_optimized(map_obj: Map2D, num_runs: int = 10, 
                                 algorithms: List[str] = None) -> Dict[str, Any]:
    """
    Chạy tất cả thuật toán với nhiều lần chạy để tìm kết quả tối ưu
    
    Args:
        map_obj: Bản đồ
        num_runs: Số lần chạy mỗi thuật toán
        algorithms: Danh sách thuật toán cần chạy
        
    Returns:
        Dictionary chứa kết quả của tất cả thuật toán
    """
    from astar import AStar
    from rrt_star import RRTStar
    from pso import PSO
    from gwo import GWO
    from sa import SA
    from ga import GA
    
    if algorithms is None:
        algorithms = ["A*", "RRT*", "PSO", "GWO", "SA", "GA"]
    
    optimizer = MultipleRunsOptimizer(map_obj, num_runs=num_runs)
    results = {}
    
    # Cấu hình cho từng thuật toán
    configs = {
        "A*": {
            'class': AStar,
            'params': {'grid_resolution': 0.5},
            'runs': 1  # A* deterministic, chỉ cần chạy 1 lần
        },
        "RRT*": {
            'class': RRTStar,
            'params': {'max_iterations': 2000, 'step_size': 2.0, 'search_radius': 8.0},
            'runs': num_runs
        },
        "PSO": {
            'class': PSO,
            'params': {'num_particles': 50, 'num_waypoints': 15, 'max_iterations': 200},
            'runs': num_runs
        },
        "GWO": {
            'class': GWO,
            'params': {'num_wolves': 30, 'num_waypoints': 15, 'max_iterations': 200},
            'runs': num_runs
        },
        "SA": {
            'class': SA,
            'params': {'num_waypoints': 15, 'initial_temp': 100.0, 
                      'cooling_rate': 0.95, 'max_iterations': 100},
            'runs': num_runs
        },
        "GA": {
            'class': GA,
            'params': {'population_size': 50, 'num_waypoints': 15, 
                      'max_generations': 200, 'mutation_rate': 0.1},
            'runs': num_runs
        }
    }
    
    total_start_time = time.time()
    
    for algo_name in algorithms:
        if algo_name not in configs:
            print(f"Cảnh báo: Thuật toán {algo_name} không được hỗ trợ!")
            continue
        
        config = configs[algo_name]
        
        # Số lần chạy (A* chỉ cần 1 lần vì deterministic)
        actual_runs = config['runs']
        
        result = optimizer.run_algorithm_multiple_times(
            algorithm_class=config['class'],
            algorithm_name=algo_name,
            **config['params']
        )
        
        # Override num_runs cho A*
        if algo_name == "A*":
            result['total_runs'] = 1
            result['note'] = 'Deterministic - chỉ cần chạy 1 lần'
        
        results[algo_name] = result
    
    total_time = time.time() - total_start_time
    
    print(f"\n{'='*70}")
    print(f"✓ HOÀN THÀNH TẤT CẢ THUẬT TOÁN")
    print(f"  Tổng thời gian: {total_time:.2f}s")
    print(f"{'='*70}\n")
    
    return results


if __name__ == "__main__":
    # Test
    from generate_map import Map2D
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Chạy PSO 10 lần
    from pso import PSO
    
    optimizer = MultipleRunsOptimizer(map_obj, num_runs=10)
    result = optimizer.run_algorithm_multiple_times(
        algorithm_class=PSO,
        algorithm_name="PSO",
        num_particles=50,
        num_waypoints=15,
        max_iterations=200
    )
    
    print("\nKết quả chi tiết:")
    print(f"Best path length: {result['best_metrics']['path_length']:.2f}m")
    print(f"Statistics: {result['statistics']}")
