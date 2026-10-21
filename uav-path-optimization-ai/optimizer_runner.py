"""
Module chạy các thuật toán tối ưu hóa nhiều lần để tìm đường đi tốt nhất.
"""

import time
import json
import os
import numpy as np
from typing import List, Dict, Callable, Tuple
from generate_map import Map2D
from metrics import Metrics
from algorithms.a_star import a_star_path_planning
from algorithms.rrt_star import rrt_star_path_planning
from algorithms.pso import pso_path_planning
from algorithms.gwo import gwo_path_planning
from algorithms.ga import ga_path_planning
from algorithms.sa import sa_path_planning


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder để xử lý numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class OptimizerRunner:
    """Lớp chạy các thuật toán tối ưu hóa."""
    
    def __init__(self, map_obj: Map2D):
        """
        Khởi tạo.
        
        Args:
            map_obj: Đối tượng Map2D
        """
        # Lưu đối tượng bản đồ để các thuật toán truy cập (start/goal, obstacles,...)
        self.map = map_obj
        self.algorithms = {
            'A*': a_star_path_planning,
            'RRT*': rrt_star_path_planning,
            'PSO': pso_path_planning,
            'GWO': gwo_path_planning,
            'GA': ga_path_planning,
            'SA': sa_path_planning
        }
        
        self.results = {}
    
    def run_single_algorithm(self, algorithm_name: str, runs: int = 5) -> Dict:
        """
        Chạy một thuật toán nhiều lần.
        
        Args:
            algorithm_name: Tên thuật toán
            runs: Số lần chạy
            
        Returns:
            Dictionary chứa kết quả
        """
        # Kiểm tra thuật toán có hợp lệ hay không
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Thuật toán '{algorithm_name}' không được hỗ trợ")
        
        algorithm_func = self.algorithms[algorithm_name]
        
        # Danh sách lưu các đường, thời gian và metrics cho từng lần chạy
        paths = []
        execution_times = []
        metrics_list = []

        print(f"\nChạy thuật toán {algorithm_name}...")

        # Thực hiện chạy `runs` lần để lấy thống kê cho thuật toán (đặc biệt cần cho meta-heuristics)
        for run in range(runs):
            # Ghi thời gian chạy để tính thống kê thời gian
            start_time = time.time()
            path = algorithm_func(self.map)
            end_time = time.time()

            execution_time = end_time - start_time

            paths.append(path)
            execution_times.append(execution_time)

            # Tính các chỉ số cho đường tìm được (độ dài, mượt, an toàn,...)
            if path:
                metrics_result = Metrics.compute_all_metrics(path, self.map, execution_time)
                metrics_list.append(metrics_result)

                print(f"  Lần {run + 1}: Độ dài = {metrics_result['path_length']:.2f}, "
                      f"Thời gian = {execution_time:.4f}s")
            else:
                # Nếu không tìm thấy đường, metrics_list không ghi nhận kết quả (vẫn giữ execution_time)
                print(f"  Lần {run + 1}: Không tìm thấy đường đi")
        
        # Tính toán thống kê
        result = {
            'algorithm': algorithm_name,
            'runs': runs,
            'paths': paths,
            'execution_times': execution_times,
            'metrics': metrics_list,
            'statistics': self._calculate_statistics(metrics_list, execution_times)
        }
        
        return result
    
    def _calculate_statistics(self, metrics_list: List[Dict], 
                            execution_times: List[float]) -> Dict:
        """
        Tính toán thống kê từ danh sách chỉ số.
        
        Args:
            metrics_list: Danh sách chỉ số từ các lần chạy
            execution_times: Danh sách thời gian thực thi
            
        Returns:
            Dictionary chứa thống kê
        """
        import numpy as np
        
        # Thống kê cơ bản cho thời gian thực thi
        statistics = {
            'execution_time_mean': np.mean(execution_times),
            'execution_time_std': np.std(execution_times)
        }
        
        # Tính toán thống kê cho mỗi chỉ số
        # Nếu có metrics từ các lần chạy, tính mean/std/min/max cho từng chỉ số
        if metrics_list:
            for metric_key in metrics_list[0].keys():
                if metric_key != 'execution_time':  # Bỏ qua vì đã tính riêng
                    values = [m[metric_key] for m in metrics_list]
                    statistics[f'{metric_key}_mean'] = np.mean(values)
                    statistics[f'{metric_key}_std'] = np.std(values)
                    statistics[f'{metric_key}_min'] = np.min(values)
                    statistics[f'{metric_key}_max'] = np.max(values)
        
        return statistics
    
    def run_all_algorithms(self, runs: int = 5) -> Dict:
        """
        Chạy tất cả các thuật toán.
        
        Args:
            runs: Số lần chạy cho mỗi thuật toán
            
        Returns:
            Dictionary chứa kết quả của tất cả thuật toán
        """
        all_results = {}
        
        for algorithm_name in self.algorithms.keys():
            try:
                result = self.run_single_algorithm(algorithm_name, runs)
                all_results[algorithm_name] = result
                self.results[algorithm_name] = result
            except Exception as e:
                print(f"Lỗi chạy thuật toán {algorithm_name}: {e}")
        
        return all_results
    
    def get_best_path(self, algorithm_name: str) -> Tuple[List[Tuple], float]:
        """
        Lấy đường đi tốt nhất từ một thuật toán.
        
        Args:
            algorithm_name: Tên thuật toán
            
        Returns:
            Tuple (đường đi tốt nhất, độ dài)
        """
        # Nếu thuật toán chưa chạy, trả về None
        if algorithm_name not in self.results:
            return None, float('inf')
        
        result = self.results[algorithm_name]
        metrics_list = result['metrics']
        paths = result['paths']
        
        if not metrics_list:
            return None, float('inf')

        # Lựa chọn theo tiêu chí đường ngắn nhất (có thể thay đổi logic nếu muốn)
        best_idx = 0
        best_length = metrics_list[0]['path_length']

        for i, metrics_result in enumerate(metrics_list):
            if metrics_result['path_length'] < best_length:
                best_length = metrics_result['path_length']
                best_idx = i

        return paths[best_idx], best_length
    
    def save_results(self, output_file: str):
        """
        Lưu kết quả vào file JSON.
        
        Args:
            output_file: Tên file output
        """
        # Chuẩn bị dữ liệu để lưu (converter các đối tượng numpy)
        # Chuyển kết quả thành cấu trúc JSON-serializable và lưu vào tập tin
        save_data = {}

        for algorithm_name, result in self.results.items():
            save_data[algorithm_name] = {
                'algorithm': result['algorithm'],
                'runs': result['runs'],
                'statistics': result['statistics'],
                'metrics_list': result['metrics']
            }
        
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(save_data, f, indent=2, cls=NumpyEncoder)
        
        print(f"✅ Lưu kết quả: {output_file}")
    
    def print_summary(self):
        """In tóm tắt kết quả."""
        print("\n" + "="*80)
        print("TÓM TẮT KẾT QUẢ")
        print("="*80)
        
        # So sánh độ dài đường đi
        print("\nĐộ dài đường đi trung bình:")
        print("-" * 50)
        
        best_algo = None
        best_length = float('inf')
        
        for algorithm_name, result in self.results.items():
            stats = result['statistics']
            mean_length = stats.get('path_length_mean', float('inf'))
            std_length = stats.get('path_length_std', 0)
            
            print(f"{algorithm_name:10s}: {mean_length:8.2f} ± {std_length:6.2f}")
            
            if mean_length < best_length:
                best_length = mean_length
                best_algo = algorithm_name
        
        print(f"\nThuật toán tốt nhất: {best_algo}")
        
        # So sánh thời gian thực thi
        print("\nThời gian thực thi trung bình:")
        print("-" * 50)
        
        for algorithm_name, result in self.results.items():
            stats = result['statistics']
            mean_time = stats.get('execution_time_mean', 0)
            std_time = stats.get('execution_time_std', 0)
            
            print(f"{algorithm_name:10s}: {mean_time:8.4f} ± {std_time:8.4f} giây")


def run_optimization_experiment(map_obj: Map2D, runs: int = 5, 
                               output_dir: str = 'results') -> OptimizerRunner:
    """
    Hàm tiện ích để chạy thí nghiệm tối ưu hóa.
    
    Args:
        map_obj: Đối tượng Map2D
        runs: Số lần chạy cho mỗi thuật toán
        output_dir: Thư mục output
        
    Returns:
        Đối tượng OptimizerRunner
    """
    os.makedirs(output_dir, exist_ok=True)
    
    runner = OptimizerRunner(map_obj)
    runner.run_all_algorithms(runs)
    runner.print_summary()
    runner.save_results(os.path.join(output_dir, 'optimization_results.json'))
    
    return runner


if __name__ == "__main__":
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    runner = run_optimization_experiment(map_obj, runs=3)
