from config.ui_config import (
    COLOR_BLACK,
    COLOR_DARK_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
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

import pygame
import sys
import time


class SimulationVisualizer:
    COLOR_WHITE = COLOR_WHITE
    COLOR_BLACK = COLOR_BLACK
    COLOR_LIGHT_GRAY = COLOR_LIGHT_GRAY
    COLOR_DARK_GRAY = COLOR_DARK_GRAY
    COLOR_GRID = (200, 200, 200)
    COLOR_OBSTACLE = (50, 50, 50)
    COLOR_START = (0, 200, 0)
    COLOR_GOAL = (200, 0, 0)
    COLOR_PATH = (0, 100, 255)
    COLOR_WAYPOINT = (100, 200, 255)

    STATE_MENU = "menu"
    STATE_RUNNING = "running"
    STATE_RESULT = "result"

    def __init__(self, grid_map):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.grid_map = grid_map
        self.running = True
        self.state = self.STATE_MENU

        self.algorithm = None
        self.path = None
        self.metrics = None
        self.execution_time = 0

        self.menu_items = [
            "1: A* algorithm",
            "2: PSO algorithm",
            "3: APSO algorithm",
            "4: HAPSO algorithm",
            "Space: Run selected algorithm",
            "Q: Quit",
        ]

        self.status = "Select an algorithm"
        self.algorithm_display = "None"

        self.grid_width = grid_map.width
        self.grid_height = grid_map.height

        max_cell_width = (WINDOW_WIDTH - 40) / self.grid_width
        max_cell_height = (WINDOW_HEIGHT - 200) / self.grid_height
        self.cell_size = int(min(max_cell_width, max_cell_height))

        self.grid_start_x = (WINDOW_WIDTH - self.grid_width * self.cell_size) // 2
        self.grid_start_y = 100

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_1:
                    self.algorithm = "A*"
                    self.algorithm_display = "A*"
                    self.status = "Algorithm: A* (Press Space to run)"
                    self.state = self.STATE_MENU
                elif event.key == pygame.K_2:
                    self.algorithm = "PSO"
                    self.algorithm_display = "PSO"
                    self.status = "Algorithm: PSO (Press Space to run)"
                    self.state = self.STATE_MENU
                elif event.key == pygame.K_3:
                    self.algorithm = "APSO"
                    self.algorithm_display = "APSO"
                    self.status = "Algorithm: APSO (Press Space to run)"
                    self.state = self.STATE_MENU
                elif event.key == pygame.K_4:
                    self.algorithm = "HAPSO"
                    self.algorithm_display = "HAPSO"
                    self.status = "Algorithm: HAPSO (Press Space to run)"
                    self.state = self.STATE_MENU
                elif event.key == pygame.K_SPACE and self.algorithm:
                    self._run_algorithm()
                elif event.key == pygame.K_ESCAPE:
                    if self.state == self.STATE_RESULT:
                        self.state = self.STATE_MENU
                        self.path = None
                        self.metrics = None

    def _run_algorithm(self):
        if not self.algorithm or not self.grid_map.start or not self.grid_map.goal:
            self.status = "ERROR: No algorithm selected or map incomplete"
            return

        try:
            self.status = f"Running {self.algorithm}..."
            start_time = time.time()

            if self.algorithm == "A*":
                planner = AStar(self.grid_map)
            elif self.algorithm == "PSO":
                planner = PSOPlanner(self.grid_map)
            elif self.algorithm == "APSO":
                planner = APSO(self.grid_map)
            elif self.algorithm == "HAPSO":
                planner = HAPSO(self.grid_map)
            else:
                self.status = f"ERROR: Unknown algorithm {self.algorithm}"
                return

            self.path = planner.find_path(self.grid_map.start, self.grid_map.goal)
            self.execution_time = time.time() - start_time

            if not self.path:
                self.status = f"{self.algorithm} failed to find path"
                return

            self.metrics = compute_all_metrics(
                self.path, self.grid_map, self.execution_time
            )
            self.status = f"{self.algorithm} completed! Press ESC to return to menu"
            self.state = self.STATE_RESULT

        except Exception as e:
            self.status = f"ERROR: {str(e)}"

    def draw(self):
        self.screen.fill(self.COLOR_LIGHT_GRAY)

        header_text = self.font_large.render(
            "SIMULATION - Interactive", True, self.COLOR_BLACK
        )
        self.screen.blit(header_text, (10, 10))

        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_RESULT:
            self._draw_result()

        self._draw_status_bar()

        pygame.display.flip()

    def _draw_menu(self):
        menu_y = 60

        status_text = self.font_small.render(self.status, True, self.COLOR_BLACK)
        self.screen.blit(status_text, (20, menu_y))

        menu_y += 40
        for item in self.menu_items:
            text_surface = self.font_small.render(item, True, self.COLOR_BLACK)
            self.screen.blit(text_surface, (20, menu_y))
            menu_y += 25

        info_y = menu_y + 20
        algo_text = self.font_small.render(
            f"Current: {self.algorithm_display}", True, self.COLOR_DARK_GRAY
        )
        self.screen.blit(algo_text, (20, info_y))

        map_info_y = info_y + 30
        map_info = [
            f"Map: {self.grid_width}x{self.grid_height}",
            f"Start: {self.grid_map.start}",
            f"Goal: {self.grid_map.goal}",
        ]
        for info_line in map_info:
            text = self.font_small.render(info_line, True, self.COLOR_DARK_GRAY)
            self.screen.blit(text, (20, map_info_y))
            map_info_y += 20

    def _draw_result(self):
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

        if self.path and len(self.path) > 1:
            for i in range(len(self.path) - 1):
                x1, y1 = self.path[i]
                x2, y2 = self.path[i + 1]

                px1 = self.grid_start_x + x1 * self.cell_size + self.cell_size // 2
                py1 = self.grid_start_y + y1 * self.cell_size + self.cell_size // 2
                px2 = self.grid_start_x + x2 * self.cell_size + self.cell_size // 2
                py2 = self.grid_start_y + y2 * self.cell_size + self.cell_size // 2

                pygame.draw.line(
                    self.screen, self.COLOR_PATH, (px1, py1), (px2, py2), 2
                )

            for x, y in self.path[1:-1]:
                px = self.grid_start_x + x * self.cell_size + self.cell_size // 2
                py = self.grid_start_y + y * self.cell_size + self.cell_size // 2
                pygame.draw.circle(self.screen, self.COLOR_WAYPOINT, (px, py), 3)

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

        metrics_y = grid_end_y + 15
        if self.metrics:
            metric_lines = [
                f"Algorithm: {self.algorithm_display} | Path Length: {self.metrics.get('path_length', 0):.2f}",
                f"Waypoints: {self.metrics.get('waypoints', 0)} | Turning Angle: {self.metrics.get('turning_angle', 0):.4f} rad",
                f"Execution Time: {self.metrics.get('execution_time', 0):.4f}s | Min Clearance: {self.metrics.get('min_clearance', 0):.2f}",
            ]

            for i, line in enumerate(metric_lines):
                text = self.font_small.render(line, True, self.COLOR_BLACK)
                self.screen.blit(text, (10, metrics_y + i * 20))

    def _draw_status_bar(self):
        status_y = WINDOW_HEIGHT - 25
        pygame.draw.line(
            self.screen,
            self.COLOR_DARK_GRAY,
            (0, status_y - 5),
            (WINDOW_WIDTH, status_y - 5),
            1,
        )

        status_surface = self.font_small.render(self.status, True, self.COLOR_BLACK)
        self.screen.blit(status_surface, (10, status_y))

    def run(self):
        print("[VISUALIZER] Starting interactive simulation...")
        print("[VISUALIZER] Select algorithm using 1-4 keys, then press Space to run")

        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        print("[VISUALIZER] Simulation closed")


def main():
    MAP_PATH = "data/maps/2026-04-23_19-53-07/map.json"

    print(f"\n{'='*60}")
    print(f"[SIMULATION] Starting interactive simulation")
    print(f"{'='*60}")
    print(f"[SIMULATION] Loading map from: {MAP_PATH}")

    grid_map = MapSerializer.load(MAP_PATH)
    if not grid_map:
        print("[SIMULATION] ERROR: Failed to load map")
        sys.exit(1)

    print(f"[SIMULATION] Map loaded: {grid_map.width}x{grid_map.height}")
    print(f"[SIMULATION] Start: {grid_map.start}, Goal: {grid_map.goal}")

    if not grid_map.start or not grid_map.goal:
        print("[SIMULATION] ERROR: Map missing start or goal")
        sys.exit(1)

    print(f"{'='*60}\n")

    try:
        visualizer = SimulationVisualizer(grid_map)
        visualizer.run()

    except Exception as e:
        print(f"[SIMULATION] ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
