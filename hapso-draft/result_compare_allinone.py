"""
TỔNG HỢP CODE RESULT COMPARE

File này tổng hợp toàn bộ logic liên quan đến chức năng so sánh kết quả (Result Compare) của các thuật toán đường đi.
Bao gồm:
- Giao diện so sánh kết quả (CompareResultScreen)
- Lưu kết quả (save_result_bundle)
- Chạy và thu thập kết quả (ExperimentResult, run_experiments)

"""

# --- Giao diện so sánh kết quả ---
import pygame
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# --- Kết quả và lưu trữ ---
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path


# --- App State (rút gọn) ---
class AppState:
    def __init__(self):
        self.current_algorithm = None
        self.grid_width = 20
        self.grid_height = 20
        self.start = (0, 0)
        self.goal = (19, 19)
        self.obstacles = []


# --- Kết quả thuật toán ---
@dataclass
class ExperimentResult:
    name: str
    length: float
    smoothness: float
    nodes: int
    objective_value: float


# --- Lưu kết quả ---
def save_result_bundle(result, state, base_dir="data/results"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(base_dir, timestamp)
    Path(result_dir).mkdir(parents=True, exist_ok=True)
    result_dict = {
        "timestamp": datetime.now().isoformat(),
        "algorithm": state.current_algorithm,
        "success": getattr(result, "success", True),
        "grid": {
            "width": state.grid_width,
            "height": state.grid_height,
            "start": list(state.start) if state.start else None,
            "goal": list(state.goal) if state.goal else None,
            "obstacles_count": len(state.obstacles),
        },
        "metrics": {
            "length": result.length,
            "smoothness": result.smoothness,
            "nodes": result.nodes,
            "objective_value": result.objective_value,
        },
    }
    with open(os.path.join(result_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    return result_dir


# --- Giao diện chính ---
class CompareResultScreen:
    def __init__(self, app):
        self.app = app
        self.chart_surface = None
        self.status = "Press R to run algorithm benchmark"
        self.buttons = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self._run_and_draw()

    def update(self):
        pass

    def draw(self, surface):
        surface.fill((240, 240, 240))
        # ...vẽ giao diện, biểu đồ, nút, v.v...
        if self.chart_surface:
            surface.blit(self.chart_surface, (350, 80))

    def _run_and_draw(self):
        # Giả lập chạy benchmark các thuật toán
        results = [
            ExperimentResult("A*", 100, 20, 15, 120),
            ExperimentResult("PSO", 95, 18, 14, 110),
            ExperimentResult("APSO", 93, 17, 13, 108),
            ExperimentResult("HAPSO", 90, 16, 12, 105),
        ]
        self._draw_chart(results)
        self.status = "Benchmark completed!"

    def _draw_chart(self, results):
        # Vẽ biểu đồ so sánh kết quả
        names = [r.name for r in results]
        values = [r.objective_value for r in results]
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(names, values, color=["#4e79a7", "#f28e2b", "#e15759", "#76b7b2"])
        ax.set_ylabel("Objective Value")
        ax.set_title("Result Compare")
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        buf.seek(0)
        image = pygame.image.load(buf, "chart.png")
        self.chart_surface = image
        plt.close(fig)


# --- Sử dụng mẫu ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    app = type("App", (), {"window_width": 900, "window_height": 600})()
    compare_screen = CompareResultScreen(app)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            compare_screen.handle_event(event)
        compare_screen.update()
        compare_screen.draw(screen)
        pygame.display.flip()
    pygame.quit()
