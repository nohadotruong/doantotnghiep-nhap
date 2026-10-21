from config.ui_config import (
    FONT_SIZE_DEFAULT,
    FONT_SIZE_SMALL,
    FPS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from core.algorithms.apso import APSO
from core.algorithms.astar import AStar
from core.algorithms.hapso import HAPSO
from core.algorithms.pso_planner import PSOPlanner
from core.metrics import compute_all_metrics
from map.map_serializer import MapSerializer

import sys
import time

import matplotlib.pyplot as plt
import pygame

ALGORITHM_COLORS = {
    "A*": (0, 100, 255),
    "PSO": (255, 165, 0),
    "APSO": (255, 0, 255),
    "HAPSO": (0, 200, 0),
}

ALGORITHM_COLORS_MATPLOTLIB = {
    "A*": "blue",
    "PSO": "orange",
    "APSO": "magenta",
    "HAPSO": "green",
}


class ComparisonVisualizer:

    COLOR_GRID = (200, 200, 200)
    COLOR_OBSTACLE = (50, 50, 50)
    COLOR_START = (0, 200, 0)
    COLOR_GOAL = (200, 0, 0)
    COLOR_WAYPOINT = (100, 100, 100)

    def __init__(self, grid_map, results_dict):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.grid_map = grid_map
        self.results_dict = results_dict
        self.running = True

        self.grid_width = grid_map.width
        self.grid_height = grid_map.height

        max_cell_width = (WINDOW_WIDTH - 40) / self.grid_width
        max_cell_height = (WINDOW_HEIGHT - 120) / self.grid_height
        self.cell_size = int(min(max_cell_width, max_cell_height))

        self.grid_start_x = (WINDOW_WIDTH - self.grid_width * self.cell_size) // 2
        self.grid_start_y = 80

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.running = False

    def draw(self):
        self.screen.fill(self.COLOR_LIGHT_GRAY)

        header_text = self.font_large.render(
            "ALGORITHM COMPARISON - All Paths", True, self.COLOR_BLACK
        )
        self.screen.blit(header_text, (10, 10))

        status_text = self.font_small.render(
            "Press any key to continue to charts", True, self.COLOR_DARK_GRAY
        )
        self.screen.blit(status_text, (10, 40))

        grid_end_x = self.grid_start_x + self.grid_width * self.cell_size
        grid_end_y = self.grid_start_y + self.grid_height * self.cell_size

        pygame.draw.rect(
            self.screen,
            self.COLOR_WHITE,
            (
                self.grid_start_x,
                self.grid_start_y,
                self.grid_width * self.cell_size,
                self.grid_height * self.cell_size,
            ),
        )

        if self.cell_size > 5:
            for x in range(self.grid_width + 1):
                pygame.draw.line(
                    self.screen,
                    self.COLOR_GRID,
                    (self.grid_start_x + x * self.cell_size, self.grid_start_y),
                    (self.grid_start_x + x * self.cell_size, grid_end_y),
                    1,
                )

            for y in range(self.grid_height + 1):
                pygame.draw.line(
                    self.screen,
                    self.COLOR_GRID,
                    (self.grid_start_x, self.grid_start_y + y * self.cell_size),
                    (grid_end_x, self.grid_start_y + y * self.cell_size),
                    1,
                )

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if self.grid_map.grid[y][x] == self.grid_map.OBSTACLE:
                    cell_x = self.grid_start_x + x * self.cell_size
                    cell_y = self.grid_start_y + y * self.cell_size
                    pygame.draw.rect(
                        self.screen,
                        self.COLOR_OBSTACLE,
                        (cell_x, cell_y, self.cell_size, self.cell_size),
                    )

        for algo_name, (path, metrics) in self.results_dict.items():
            if not path or len(path) < 2:
                continue

            color = ALGORITHM_COLORS.get(algo_name, (255, 255, 255))
            line_width = max(1, self.cell_size // 8)

            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]

                px1 = self.grid_start_x + x1 * self.cell_size + self.cell_size // 2
                py1 = self.grid_start_y + y1 * self.cell_size + self.cell_size // 2
                px2 = self.grid_start_x + x2 * self.cell_size + self.cell_size // 2
                py2 = self.grid_start_y + y2 * self.cell_size + self.cell_size // 2

                pygame.draw.line(self.screen, color, (px1, py1), (px2, py2), line_width)

        if self.grid_map.start:
            x, y = self.grid_map.start
            cell_x = self.grid_start_x + x * self.cell_size
            cell_y = self.grid_start_y + y * self.cell_size
            pygame.draw.rect(
                self.screen,
                self.COLOR_START,
                (cell_x, cell_y, self.cell_size, self.cell_size),
            )
            pygame.draw.rect(
                self.screen,
                self.COLOR_BLACK,
                (cell_x, cell_y, self.cell_size, self.cell_size),
                2,
            )

        if self.grid_map.goal:
            x, y = self.grid_map.goal
            cell_x = self.grid_start_x + x * self.cell_size
            cell_y = self.grid_start_y + y * self.cell_size
            pygame.draw.rect(
                self.screen,
                self.COLOR_GOAL,
                (cell_x, cell_y, self.cell_size, self.cell_size),
            )
            pygame.draw.rect(
                self.screen,
                self.COLOR_BLACK,
                (cell_x, cell_y, self.cell_size, self.cell_size),
                2,
            )

        legend_y = grid_end_y + 15
        legend_x = self.grid_start_x

        for i, (algo_name, color) in enumerate(ALGORITHM_COLORS.items()):
            x = legend_x + (i % 2) * 250
            y = legend_y + (i // 2) * 20

            pygame.draw.rect(self.screen, color, (x, y, 15, 15))

            path, metrics = self.results_dict.get(algo_name, (None, None))
            if path and metrics:
                label = f"{algo_name}: {metrics['path_length']:.1f}"
            else:
                label = f"{algo_name}: No path"

            text = self.font_small.render(label, True, self.COLOR_BLACK)
            self.screen.blit(text, (x + 20, y))

        pygame.display.flip()

    def run(self):
        print("[VISUALIZER] Press any key to continue to comparison charts")

        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def show_comparison_charts(results_dict):
    algo_names = list(results_dict.keys())
    path_lengths = []
    waypoints_list = []
    turning_angles = []
    exec_times = []
    clearances = []

    for algo_name in algo_names:
        path, metrics = results_dict[algo_name]
        if path and metrics:
            path_lengths.append(metrics.get("path_length", 0))
            waypoints_list.append(metrics.get("waypoints", 0))
            turning_angles.append(metrics.get("turning_angle", 0))
            exec_times.append(metrics.get("execution_time", 0))
            clearances.append(metrics.get("min_clearance", 0))
        else:
            path_lengths.append(0)
            waypoints_list.append(0)
            turning_angles.append(0)
            exec_times.append(0)
            clearances.append(0)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Algorithm Comparison", fontsize=16)

    ax = axes[0, 0]
    colors = [ALGORITHM_COLORS_MATPLOTLIB.get(name, "gray") for name in algo_names]
    ax.bar(algo_names, path_lengths, color=colors, alpha=0.7)
    ax.set_ylabel("Path Length")
    ax.set_title("Total Path Length")
    ax.grid(axis="y", alpha=0.3)

    ax = axes[0, 1]
    ax.bar(algo_names, waypoints_list, color=colors, alpha=0.7)
    ax.set_ylabel("Number of Waypoints")
    ax.set_title("Waypoint Count")
    ax.grid(axis="y", alpha=0.3)

    ax = axes[1, 0]
    ax.bar(algo_names, turning_angles, color=colors, alpha=0.7)
    ax.set_ylabel("Total Turning Angle (rad)")
    ax.set_title("Smoothness (Turning Angle)")
    ax.grid(axis="y", alpha=0.3)

    ax = axes[1, 1]
    ax.bar(algo_names, exec_times, color=colors, alpha=0.7)
    ax.set_ylabel("Time (seconds)")
    ax.set_title("Execution Time")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    print("[COMPARISON] Displaying comparison charts... Close the window to finish")
    plt.show()


def main():
    MAP_PATH = "data/maps/2026-04-23_19-53-07/map.json"

    print(f"\n{'='*60}")
    print("[COMPARISON] Starting algorithm comparison")
    print(f"{'='*60}")
    print(f"[COMPARISON] Loading map from: {MAP_PATH}")

    grid_map = MapSerializer.load(MAP_PATH)
    if not grid_map:
        print("[COMPARISON] ERROR: Failed to load map")
        sys.exit(1)

    print(f"[COMPARISON] Map loaded: {grid_map.width}x{grid_map.height}")
    print(f"[COMPARISON] Start: {grid_map.start}, Goal: {grid_map.goal}")

    if not grid_map.start or not grid_map.goal:
        print("[COMPARISON] ERROR: Map missing start or goal")
        sys.exit(1)

    algorithms = [
        ("A*", AStar),
        ("PSO", PSOPlanner),
        ("APSO", APSO),
        ("HAPSO", HAPSO),
    ]

    results_dict = {}

    print(f"\n{'='*60}")
    print("[COMPARISON] Running algorithms...")
    print(f"{'='*60}\n")

    for i, (algo_name, algo_class) in enumerate(algorithms, 1):
        print(f"[{i}/4] Running {algo_name}...", end=" ", flush=True)

        start_time = time.time()
        try:
            planner = algo_class(grid_map)
            path = planner.find_path(grid_map.start, grid_map.goal)
            execution_time = time.time() - start_time

            if path:
                metrics = compute_all_metrics(path, grid_map, execution_time)
                results_dict[algo_name] = (path, metrics)
                print(f"✓ done ({execution_time:.4f}s, {len(path)} waypoints)")
            else:
                print(f"✗ No path found")
                results_dict[algo_name] = (None, None)

        except Exception as e:
            print(f"✗ Error: {e}")
            results_dict[algo_name] = (None, None)

    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print(f"{'='*60}")

    print(
        f"{'Algorithm':<10} {'Path Length':<15} {'Waypoints':<12} "
        f"{'Turn Angle':<15} {'Exec Time':<15} {'Clearance':<12}"
    )
    print("-" * 80)

    for algo_name in ["A*", "PSO", "APSO", "HAPSO"]:
        path, metrics = results_dict.get(algo_name, (None, None))
        if path and metrics:
            print(
                f"{algo_name:<10} "
                f"{metrics['path_length']:<15.2f} "
                f"{metrics['waypoints']:<12} "
                f"{metrics['turning_angle']:<15.4f} "
                f"{metrics['execution_time']:<15.4f} "
                f"{metrics['min_clearance']:<12.2f}"
            )
        else:
            print(
                f"{algo_name:<10} {'No path':<15} {'-':<12} {'-':<15} {'-':<15} {'-':<12}"
            )

    print(f"{'='*60}\n")

    print("[COMPARISON] Starting visualization...")
    visualizer = ComparisonVisualizer(grid_map, results_dict)
    visualizer.run()

    print("[COMPARISON] Generating comparison charts...")
    show_comparison_charts(results_dict)

    print("[COMPARISON] Done!")


if __name__ == "__main__":
    main()
