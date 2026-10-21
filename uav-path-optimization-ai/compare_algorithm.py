"""
Module so sánh hiệu suất của các thuật toán và tạo biểu đồ, bảng số liệu.
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List
from optimizer_runner import OptimizerRunner
from generate_map import Map2D


class AlgorithmComparator:
    """Lớp so sánh các thuật toán."""
    
    def __init__(self, runner: OptimizerRunner):
        """
        Khởi tạo.
        
        Args:
            runner: Đối tượng OptimizerRunner chứa kết quả
        """
        self.runner = runner
        self.comparison_df = None
    
    def create_comparison_dataframe(self) -> pd.DataFrame:
        """
        Tạo DataFrame chứa bảng so sánh.
        
        Returns:
            DataFrame chứa thông tin so sánh
        """
        # Tạo danh sách các hàng cho DataFrame từ thống kê mỗi thuật toán
        data = []

        for algorithm_name, result in self.runner.results.items():
            stats = result['statistics']

            # Lấy các giá trị mean/SD từ phần statistics (đã tính trong OptimizerRunner)
            row = {
                'Thuật toán': algorithm_name,
                'Độ dài TB (m)': stats.get('path_length_mean', 0),
                'Độ dài SD': stats.get('path_length_std', 0),
                'Góc quay TB (°)': stats.get('smoothness_mean', 0),
                'Góc quay SD': stats.get('smoothness_std', 0),
                'Khoảng cách an toàn TB (m)': stats.get('average_safety_margin_mean', 0),
                'Thời gian TB (s)': stats.get('execution_time_mean', 0),
                'Số waypoint TB': stats.get('waypoints_count_mean', 0),
                'Hiệu suất TB': stats.get('path_efficiency_mean', 0),
                'Tỷ lệ an toàn TB': stats.get('clearance_ratio_mean', 0)
            }

            data.append(row)
        
        self.comparison_df = pd.DataFrame(data)
        return self.comparison_df
    
    def save_comparison_table(self, output_file: str):
        """
        Lưu bảng so sánh vào file CSV.
        
        Args:
            output_file: Tên file output
        """
        if self.comparison_df is None:
            self.create_comparison_dataframe()
        
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        self.comparison_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Lưu bảng so sánh: {output_file}")
    
    def plot_path_length_comparison(self, output_file: str = None):
        """
        Vẽ biểu đồ so sánh độ dài đường đi.
        
        Args:
            output_file: Tên file lưu hình ảnh (không lưu nếu None)
        """
        if self.comparison_df is None:
            self.create_comparison_dataframe()
        
        # Vẽ bar chart với mean và error bar là std
        fig, ax = plt.subplots(figsize=(10, 6))
        
        algorithms = self.comparison_df['Thuật toán']
        means = self.comparison_df['Độ dài TB (m)']
        stds = self.comparison_df['Độ dài SD']
        
        x = np.arange(len(algorithms))
        width = 0.6
        
        bars = ax.bar(x, means, width, yerr=stds, capsize=5,
                  color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        
        ax.set_xlabel('Thuật toán', fontsize=12, fontweight='bold')
        ax.set_ylabel('Độ dài đường đi (m)', fontsize=12, fontweight='bold')
        ax.set_title('So sánh độ dài đường đi', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.grid(axis='y', alpha=0.3)
        
        # Thêm giá trị trên cột
        for i, (mean, std) in enumerate(zip(means, stds)):
            ax.text(i, mean + std + 1, f'{mean:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Lưu biểu đồ: {output_file}")
        
        plt.close()
    
    def plot_execution_time_comparison(self, output_file: str = None):
        """
        Vẽ biểu đồ so sánh thời gian thực thi.
        
        Args:
            output_file: Tên file lưu hình ảnh (không lưu nếu None)
        """
        if self.comparison_df is None:
            self.create_comparison_dataframe()
        
        # Biểu đồ thời gian thực thi trung bình
        fig, ax = plt.subplots(figsize=(10, 6))
        
        algorithms = self.comparison_df['Thuật toán']
        times = self.comparison_df['Thời gian TB (s)']
        
        x = np.arange(len(algorithms))
        width = 0.6
        
        bars = ax.bar(x, times, width, 
                      color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        
        ax.set_xlabel('Thuật toán', fontsize=12, fontweight='bold')
        ax.set_ylabel('Thời gian thực thi (giây)', fontsize=12, fontweight='bold')
        ax.set_title('So sánh thời gian thực thi', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.grid(axis='y', alpha=0.3)
        
        # Thêm giá trị trên cột
        for i, time in enumerate(times):
            ax.text(i, time + 0.001, f'{time:.4f}s', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Lưu biểu đồ: {output_file}")
        
        plt.close()
    
    def plot_smoothness_comparison(self, output_file: str = None):
        """
        Vẽ biểu đồ so sánh độ mượt.
        
        Args:
            output_file: Tên file lưu hình ảnh (không lưu nếu None)
        """
        if self.comparison_df is None:
            self.create_comparison_dataframe()
        
        # Biểu đồ so sánh tổng góc quay trung bình (độ)
        fig, ax = plt.subplots(figsize=(10, 6))
        
        algorithms = self.comparison_df['Thuật toán']
        smoothness = self.comparison_df['Góc quay TB (°)']
        
        x = np.arange(len(algorithms))
        width = 0.6
        
        bars = ax.bar(x, smoothness, width,
                      color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        
        ax.set_xlabel('Thuật toán', fontsize=12, fontweight='bold')
        ax.set_ylabel('Tổng góc quay (°)', fontsize=12, fontweight='bold')
        ax.set_title('So sánh độ mượt đường đi', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.grid(axis='y', alpha=0.3)
        
        # Thêm giá trị trên cột
        for i, smooth in enumerate(smoothness):
            ax.text(i, smooth + 10, f'{smooth:.1f}°', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Lưu biểu đồ: {output_file}")
        
        plt.close()
    
    def plot_safety_comparison(self, output_file: str = None):
        """
        Vẽ biểu đồ so sánh độ an toàn.
        
        Args:
            output_file: Tên file lưu hình ảnh (không lưu nếu None)
        """
        if self.comparison_df is None:
            self.create_comparison_dataframe()
        
        # Biểu đồ so sánh khoảng cách an toàn trung bình
        fig, ax = plt.subplots(figsize=(10, 6))
        
        algorithms = self.comparison_df['Thuật toán']
        safety = self.comparison_df['Khoảng cách an toàn TB (m)']
        
        x = np.arange(len(algorithms))
        width = 0.6
        
        bars = ax.bar(x, safety, width,
                      color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        
        ax.set_xlabel('Thuật toán', fontsize=12, fontweight='bold')
        ax.set_ylabel('Khoảng cách an toàn (m)', fontsize=12, fontweight='bold')
        ax.set_title('So sánh độ an toàn (khoảng cách đến chướng ngại vật)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.grid(axis='y', alpha=0.3)
        
        # Thêm giá trị trên cột
        for i, safe in enumerate(safety):
            ax.text(i, safe + 0.1, f'{safe:.2f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Lưu biểu đồ: {output_file}")
        
        plt.close()
    
    def plot_radar_comparison(self, output_file: str = None):
        """
        Vẽ biểu đồ radar so sánh nhiều chỉ số.
        
        Args:
            output_file: Tên file lưu hình ảnh (không lưu nếu None)
        """
        if self.comparison_df is None:
            self.create_comparison_dataframe()
        
        # Chuẩn hóa dữ liệu
        categories = ['Độ dài', 'Góc quay', 'An toàn', 'Hiệu suất', 'Thời gian']
        
        # Biểu đồ radar cho tổng hợp nhiều chỉ số (chuẩn hóa trước khi vẽ)
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Đóng vòng
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for idx, (algo_name, row) in enumerate(self.comparison_df.iterrows()):
            # Chuẩn hóa các giá trị
            length_norm = 1 - (row['Độ dài TB (m)'] / self.comparison_df['Độ dài TB (m)'].max())
            smoothness_norm = 1 - (row['Góc quay TB (°)'] / self.comparison_df['Góc quay TB (°)'].max())
            safety_norm = row['Khoảng cách an toàn TB (m)'] / self.comparison_df['Khoảng cách an toàn TB (m)'].max()
            efficiency_norm = row['Hiệu suất TB']
            time_norm = 1 - (row['Thời gian TB (s)'] / self.comparison_df['Thời gian TB (s)'].max())
            
            values = [length_norm, smoothness_norm, safety_norm, efficiency_norm, time_norm]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=row['Thuật toán'], color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_title('So sánh hiệu suất toàn diện', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Lưu biểu đồ: {output_file}")
        
        plt.close()
    
    def plot_all_comparisons(self, output_dir: str = 'results'):
        """
        Vẽ tất cả các biểu đồ so sánh.
        
        Args:
            output_dir: Thư mục output
        """
        os.makedirs(output_dir, exist_ok=True)
        
        self.plot_path_length_comparison(os.path.join(output_dir, 'path_length_comparison.png'))
        self.plot_execution_time_comparison(os.path.join(output_dir, 'execution_time_comparison.png'))
        self.plot_smoothness_comparison(os.path.join(output_dir, 'smoothness_comparison.png'))
        self.plot_safety_comparison(os.path.join(output_dir, 'safety_comparison.png'))
        self.plot_radar_comparison(os.path.join(output_dir, 'radar_comparison.png'))
        self.save_comparison_table(os.path.join(output_dir, 'comparison_table.csv'))
        
        print("\nĐã tạo tất cả các biểu đồ và bảng so sánh!")


def compare_algorithms(runner: OptimizerRunner, output_dir: str = 'results'):
    """
    Hàm tiện ích để so sánh các thuật toán.
    
    Args:
        runner: Đối tượng OptimizerRunner
        output_dir: Thư mục output
    """
    comparator = AlgorithmComparator(runner)
    comparator.plot_all_comparisons(output_dir)


if __name__ == "__main__":
    # Tải kết quả từ file
    with open('results/optimization_results.json', 'r') as f:
        data = json.load(f)
    
    # Tạo mock runner
    from optimizer_runner import OptimizerRunner
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    runner = OptimizerRunner(map_obj)
    
    # TODO: Tái tạo kết quả từ file JSON
    
    comparator = AlgorithmComparator(runner)
    comparator.plot_all_comparisons()
